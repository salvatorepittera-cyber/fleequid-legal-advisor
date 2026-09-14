"""Modello di lettura/scrittura dei .docx delle T&C.

Ogni paragrafo del corpo diventa un `Para` con:
- testo e segmenti formattati (grassetto/corsivo/sottolineato) in markup <b>/<i>/<u>;
- chiave logica stabile tra lingue: "4.2" (articolo.paragrafo), "9.2.L1" (voce di lista
  secondaria dentro 9.2), "4.2~1" (paragrafo non numerato dopo 4.2), "0~0+e1" (vuoto);
- flag evidenziazione e appartenenza all'indice (TOC).

Il salvataggio riscrive solo le parti modificate dello zip; tutte le altre restano byte per byte.
"""
from __future__ import annotations

import copy
import re
import zipfile
from dataclasses import dataclass, field
from html import escape
from pathlib import Path

from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = "{%s}" % W_NS
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
NSMAP = {"w": W_NS}

FMT_TAGS = ("b", "i", "u")


def wtag(name: str) -> str:
    return W + name


def _on(el) -> bool:
    """Proprietà booleana w:b / w:i attiva (senza val o con val true/1/on)."""
    if el is None:
        return False
    v = el.get(wtag("val"))
    return v is None or v in ("1", "true", "on")


def run_fmt(r) -> str:
    """Restituisce una stringa con le lettere b/i/u attive sul run."""
    rpr = r.find(wtag("rPr"))
    if rpr is None:
        return ""
    f = ""
    if _on(rpr.find(wtag("b"))):
        f += "b"
    if _on(rpr.find(wtag("i"))):
        f += "i"
    u = rpr.find(wtag("u"))
    if u is not None and u.get(wtag("val"), "single") != "none":
        f += "u"
    return f


def run_text(r) -> str:
    out = []
    for c in r:
        if c.tag == wtag("t"):
            out.append(c.text or "")
        elif c.tag == wtag("tab"):
            out.append("\t")
        elif c.tag in (wtag("br"), wtag("cr")):
            out.append("\n")
        elif c.tag == wtag("noBreakHyphen"):
            out.append("‑")
    return "".join(out)


def para_runs(p):
    """Run "di testo" del paragrafo, anche dentro hyperlink/smartTag/ins, esclusi i run cancellati."""
    for el in p.iter(wtag("r")):
        anc = el.getparent()
        skip = False
        while anc is not None and anc is not p:
            if anc.tag == wtag("del"):
                skip = True
                break
            anc = anc.getparent()
        if not skip:
            yield el


def segments(p) -> list[tuple[str, str]]:
    """Segmenti (fmt, testo) con run adiacenti di pari formato fusi.

    Gli spazi puri non spezzano un segmento formattato: vengono assorbiti dal precedente.
    """
    segs: list[list[str]] = []
    for r in para_runs(p):
        # salta i risultati/istruzioni di campo (numeri di pagina del TOC restano testo normale)
        if r.find(wtag("instrText")) is not None:
            continue
        t = run_text(r)
        if not t:
            continue
        f = run_fmt(r)
        if segs and (segs[-1][0] == f or not t.strip()):
            segs[-1][1] += t
        elif segs and not segs[-1][1].strip():
            segs[-1][0], segs[-1][1] = f, segs[-1][1] + t
        else:
            segs.append([f, t])
    return [(f, t) for f, t in segs]


def to_markup(segs: list[tuple[str, str]]) -> str:
    out = []
    for f, t in segs:
        s = escape(t, quote=False)
        # gli spazi iniziali/finali restano fuori dai tag, per leggibilità e confronto
        lead = s[: len(s) - len(s.lstrip())]
        trail = s[len(s.rstrip()):]
        core = s.strip()
        if f and core:
            open_ = "".join(f"<{c}>" for c in f)
            close = "".join(f"</{c}>" for c in reversed(f))
            out.append(f"{lead}{open_}{core}{close}{trail}")
        else:
            out.append(s)
    return "".join(out)


_TAG_RE = re.compile(r"<(/?)([biu])>")


def parse_markup(s: str) -> list[tuple[str, str]]:
    """Inverso di to_markup: '<b>tre</b> mesi' -> [('b','tre'), ('',' mesi')]."""
    from html import unescape

    active: list[str] = []
    out: list[tuple[str, str]] = []
    pos = 0
    for m in _TAG_RE.finditer(s):
        if m.start() > pos:
            out.append(("".join(c for c in FMT_TAGS if c in active), unescape(s[pos:m.start()])))
        if m.group(1):
            if m.group(2) not in active:
                raise ValueError(f"Tag di chiusura </{m.group(2)}> senza apertura in: {s[:80]}")
            active.remove(m.group(2))
        else:
            active.append(m.group(2))
        pos = m.end()
    if active:
        raise ValueError(f"Tag non chiusi {active} in: {s[:80]}")
    if pos < len(s):
        out.append(("".join(c for c in FMT_TAGS if c in active), unescape(s[pos:])))
    merged: list[list[str]] = []
    for f, t in out:
        if merged and merged[-1][0] == f:
            merged[-1][1] += t
        else:
            merged.append([f, t])
    return [(f, t) for f, t in merged if t]


def strip_markup(s: str) -> str:
    from html import unescape

    return unescape(_TAG_RE.sub("", s))


def fmt_signature(segs) -> dict[str, int]:
    """Numero di segmenti non vuoti per ciascun formato (per la verifica)."""
    sig = {"b": 0, "i": 0, "u": 0}
    for f, t in segs:
        if t.strip():
            for c in f:
                sig[c] += 1
    return sig


@dataclass
class Para:
    idx: int
    el: object
    key: str = ""
    article: str = ""
    level: int | None = None  # 0 = articolo, 1 = paragrafo, ... (solo lista principale)
    style: str = ""
    num_id: str | None = None
    ilvl: int | None = None
    in_toc: bool = False
    highlighted: bool = False
    segs: list = field(default_factory=list)

    @property
    def text(self) -> str:
        return "".join(t for _, t in self.segs)

    @property
    def markup(self) -> str:
        return to_markup(self.segs)

    @property
    def empty(self) -> bool:
        return not self.text.strip()

    def ppr_xml(self) -> bytes:
        ppr = self.el.find(wtag("pPr"))
        return etree.tostring(ppr) if ppr is not None else b""


class Docx:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        with zipfile.ZipFile(self.path) as z:
            self.infos = z.infolist()
            self.parts = {i.filename: z.read(i.filename) for i in self.infos}
        self.tree = etree.fromstring(self.parts["word/document.xml"])
        self.body = self.tree.find(wtag("body"))
        self._numbering = self._load_numbering()
        self._style_num = self._load_style_numbering()
        self.headers = {n: etree.fromstring(b) for n, b in self.parts.items()
                        if re.fullmatch(r"word/(header|footer)\d*\.xml", n)}
        self.dirty: set[str] = set()
        self.reindex()

    # ---------- numerazione ----------
    def _load_numbering(self):
        raw = self.parts.get("word/numbering.xml")
        res = {"num2abs": {}, "abs": {}, "overrides": {}}
        if not raw:
            return res
        t = etree.fromstring(raw)
        for a in t.findall(wtag("abstractNum")):
            lv = {}
            for l in a.findall(wtag("lvl")):
                fmt = l.find(wtag("numFmt"))
                txt = l.find(wtag("lvlText"))
                st = l.find(wtag("start"))
                lv[int(l.get(wtag("ilvl")))] = {
                    "fmt": fmt.get(wtag("val")) if fmt is not None else "decimal",
                    "text": txt.get(wtag("val")) if txt is not None else "",
                    "start": int(st.get(wtag("val"))) if st is not None else 1,
                }
            res["abs"][a.get(wtag("abstractNumId"))] = lv
        for n in t.findall(wtag("num")):
            nid = n.get(wtag("numId"))
            res["num2abs"][nid] = n.find(wtag("abstractNumId")).get(wtag("val"))
        return res

    def _load_style_numbering(self):
        raw = self.parts.get("word/styles.xml")
        out = {}
        if not raw:
            return out
        for s in etree.fromstring(raw).findall(wtag("style")):
            np_ = s.find(f"{wtag('pPr')}/{wtag('numPr')}")
            if np_ is not None:
                ni = np_.find(wtag("numId"))
                il = np_.find(wtag("ilvl"))
                out[s.get(wtag("styleId"))] = (
                    ni.get(wtag("val")) if ni is not None else None,
                    int(il.get(wtag("val"))) if il is not None else 0,
                )
        return out

    def _num_of(self, p):
        ppr = p.find(wtag("pPr"))
        style = ""
        num_id, ilvl = None, None
        if ppr is not None:
            ps = ppr.find(wtag("pStyle"))
            style = ps.get(wtag("val")) if ps is not None else ""
            if style in self._style_num:
                num_id, ilvl = self._style_num[style]
            np_ = ppr.find(wtag("numPr"))
            if np_ is not None:
                ni = np_.find(wtag("numId"))
                il = np_.find(wtag("ilvl"))
                if ni is not None:
                    num_id = ni.get(wtag("val"))
                if il is not None:
                    ilvl = int(il.get(wtag("val")))
        if num_id == "0":
            num_id = None
        if num_id is not None and ilvl is None:
            ilvl = 0
        return style, num_id, ilvl

    def _main_abstract(self, raw):
        """La lista 'articoli' è l'abstractNum decimale con livello 0 e 1 più usato."""
        score = {}
        for _, num_id, ilvl in raw:
            if num_id is None:
                continue
            a = self._numbering["num2abs"].get(num_id)
            lv = self._numbering["abs"].get(a, {})
            if lv.get(0, {}).get("fmt") == "decimal" and lv.get(1, {}).get("fmt") == "decimal":
                score[a] = score.get(a, 0) + 1
        return max(score, key=score.get) if score else None

    # ---------- indicizzazione ----------
    def reindex(self):
        ps = list(self.body.iter(wtag("p")))
        toc_ps = set()
        for sdt in self.body.iter(wtag("sdt")):
            g = sdt.find(f".//{wtag('docPartGallery')}")
            if g is not None and "Contents" in (g.get(wtag("val")) or ""):
                toc_ps.update(sdt.iter(wtag("p")))
        raw = [self._num_of(p) for p in ps]
        main = self._main_abstract(raw)
        counters: list[int] = []
        sec_counter = 0
        sec_list = None
        unnum = 0
        empty_run = 0
        last_key = "0"
        paras = []
        for i, (p, (style, num_id, ilvl)) in enumerate(zip(ps, raw)):
            para = Para(idx=i, el=p, style=style, num_id=num_id, ilvl=ilvl,
                        in_toc=p in toc_ps or style.lower().startswith(("sommario", "toc")))
            para.segs = segments(p)
            para.highlighted = any(
                (r.find(wtag("rPr")) is not None and r.find(wtag("rPr")).find(wtag("highlight")) is not None)
                for r in para_runs(p) if run_text(r).strip())
            abs_id = self._numbering["num2abs"].get(num_id) if num_id else None
            if para.in_toc:
                para.key = f"TOC#{i}"
            elif num_id and abs_id == main:
                while len(counters) <= ilvl:
                    counters.append(0)
                counters[ilvl] += 1
                del counters[ilvl + 1:]
                para.level = ilvl
                para.key = ".".join(str(c) for c in counters)
                last_key, unnum, sec_counter, sec_list, empty_run = para.key, 0, 0, None, 0
            elif num_id and not para.empty:
                if sec_list != (num_id, ilvl):
                    # nuova lista secondaria o cambio livello: il contatore riparte solo se cambia lista
                    if sec_list is None or sec_list[0] != num_id:
                        sec_counter = 0
                    sec_list = (num_id, ilvl)
                sec_counter += 1
                para.key = f"{last_key}.L{sec_counter}" if (ilvl or 0) == 0 else f"{last_key}.L{sec_counter}.{ilvl}"
                empty_run = 0
            elif not para.empty:
                para.key = f"{last_key}~{unnum}"
                unnum += 1
                empty_run = 0
            else:
                empty_run += 1
                para.key = f"{last_key}~{unnum}+e{empty_run}"
            para.article = para.key.split(".")[0].split("~")[0] if not para.in_toc else ""
            paras.append(para)
        self.paras = paras
        self.by_key = {p.key: p for p in paras}

    # ---------- header ----------
    def header_texts(self) -> dict[str, str]:
        return {n: "".join(t.text or "" for t in x.iter(wtag("t"))) for n, x in self.headers.items()}

    # ---------- salvataggio ----------
    def mark_dirty(self, part: str):
        self.dirty.add(part)

    def save(self, out: str | Path):
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        parts = dict(self.parts)
        if "word/document.xml" in self.dirty:
            parts["word/document.xml"] = etree.tostring(self.tree, xml_declaration=True, encoding="UTF-8", standalone=True)
        for n, x in self.headers.items():
            if n in self.dirty:
                parts[n] = etree.tostring(x, xml_declaration=True, encoding="UTF-8", standalone=True)
        for n in self.dirty:
            if n.startswith("raw:"):
                pass
        with zipfile.ZipFile(out, "w") as z:
            for info in self.infos:
                zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
                zi.compress_type = info.compress_type
                zi.external_attr = info.external_attr
                z.writestr(zi, parts[info.filename])
        return out


# ---------- utilità di scrittura ----------
RPR_ORDER = [
    "rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike", "outline",
    "shadow", "emboss", "imprint", "noProof", "snapToGrid", "vanish", "webHidden", "color", "spacing",
    "w", "kern", "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd", "fitText",
    "vertAlign", "rtl", "cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath",
]


def _rpr_insert(rpr, el):
    name = etree.QName(el).localname
    pos = RPR_ORDER.index(name) if name in RPR_ORDER else len(RPR_ORDER)
    for i, c in enumerate(rpr):
        cn = etree.QName(c).localname
        if cn in RPR_ORDER and RPR_ORDER.index(cn) > pos:
            rpr.insert(i, el)
            return
    rpr.append(el)


def base_rpr(p):
    """rPr di base del paragrafo: quello del primo run di testo senza b/i/u, ripulito da b/i/u/highlight."""
    runs = [r for r in para_runs(p) if run_text(r).strip()]
    pick = next((r for r in runs if not run_fmt(r)), runs[0] if runs else None)
    rpr = copy.deepcopy(pick.find(wtag("rPr"))) if pick is not None and pick.find(wtag("rPr")) is not None else None
    if rpr is None:
        ppr_rpr = p.find(f"{wtag('pPr')}/{wtag('rPr')}")
        rpr = copy.deepcopy(ppr_rpr) if ppr_rpr is not None else etree.Element(wtag("rPr"))
        rpr.tag = wtag("rPr")
        for bad in ("ins", "del", "moveFrom", "moveTo"):
            for e in rpr.findall(wtag(bad)):
                rpr.remove(e)
    for name in ("b", "bCs", "i", "iCs", "u", "highlight"):
        for e in rpr.findall(wtag(name)):
            rpr.remove(e)
    return rpr


def fmt_rpr(base, fmt: str, bold_cs: bool = False):
    rpr = copy.deepcopy(base)
    if "b" in fmt:
        _rpr_insert(rpr, etree.Element(wtag("b")))
        if bold_cs:
            _rpr_insert(rpr, etree.Element(wtag("bCs")))
    if "i" in fmt:
        _rpr_insert(rpr, etree.Element(wtag("i")))
    if "u" in fmt:
        u = etree.Element(wtag("u"))
        u.set(wtag("val"), "single")
        _rpr_insert(rpr, u)
    return rpr


def set_paragraph_markup(p, markup: str):
    """Sostituisce il contenuto testuale del paragrafo mantenendo pPr e segnalibri."""
    base = base_rpr(p)
    had_bcs = any(r.find(f"{wtag('rPr')}/{wtag('bCs')}") is not None for r in para_runs(p))
    problems = [t for t in ("fldChar", "fldSimple", "drawing", "footnoteReference", "object")
                if p.find(f".//{wtag(t)}") is not None]
    if problems:
        raise ValueError(f"Paragrafo con elementi non testuali {problems}: intervento manuale richiesto")
    keep_start = [c for c in p if c.tag == wtag("bookmarkStart")]
    keep_end = [c for c in p if c.tag == wtag("bookmarkEnd")]
    for c in list(p):
        if c.tag != wtag("pPr"):
            p.remove(c)
    for b in keep_start:
        p.append(b)
    for fmt, text in parse_markup(markup):
        for k, piece in enumerate(text.split("\n")):
            r = etree.SubElement(p, wtag("r"))
            r.append(fmt_rpr(base, fmt, had_bcs))
            if k:
                etree.SubElement(r, wtag("br"))
            chunks = piece.split("\t")
            for j, ch in enumerate(chunks):
                if j:
                    etree.SubElement(r, wtag("tab"))
                if ch:
                    t = etree.SubElement(r, wtag("t"))
                    t.text = ch
                    if ch != ch.strip() or "  " in ch:
                        t.set(XML_SPACE, "preserve")
    for b in keep_end:
        p.append(b)


def replace_across_runs(p, old: str, new: str) -> bool:
    """Sostituisce `old` con `new` nel testo del paragrafo anche se spezzato su più w:t.

    Il testo nuovo eredita il formato del primo w:t coinvolto. Restituisce True se sostituito.
    """
    ts = [t for t in p.iter(wtag("t"))]
    full = "".join(t.text or "" for t in ts)
    pos = full.find(old)
    if pos < 0:
        return False
    end = pos + len(old)
    acc = 0
    first = True
    for t in ts:
        s = t.text or ""
        a, b = acc, acc + len(s)
        acc = b
        if b <= pos or a >= end:
            continue
        lo, hi = max(pos, a) - a, min(end, b) - a
        if first:
            t.text = s[:lo] + new + s[hi:]
            first = False
        else:
            t.text = s[:lo] + s[hi:]
        if t.text != (t.text or "").strip():
            t.set(XML_SPACE, "preserve")
    return True


def remove_highlight(root) -> int:
    n = 0
    for h in list(root.iter(wtag("highlight"))):
        h.getparent().remove(h)
        n += 1
    return n


def canonical(el) -> bytes:
    return etree.tostring(el, method="c14n")
