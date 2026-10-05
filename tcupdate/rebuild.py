"""Riscrittura integrale: quando la nuova IT riscrive gran parte del documento, ogni lingua si costruisce
sul Word IT nuovo (stessa struttura, numerazione, stili e indice) invece che sul Word precedente della lingua.

La provenienza di ogni paragrafo (da quale paragrafo della versione precedente nasce) si ricava dal redline
dello studio; la resa precedente della lingua resta il riferimento vincolante per testo e terminologia.

python3 -m tcupdate.rebuild <comando> --family "General T&C" --from 8 --to 9 --draft <bozza> [--lang EN] [--chunk k01]

  prepare   units.json + chunks.json (provenienza dal redline: --redline <file>)
  brief     brief per blocco di articoli della lingua
  check     controlla le traduzioni di un blocco (o di tutti)
  terms     tabella dei termini definiti ricavata dal blocco k01 (art. 1 + titoli)
  build     Word della lingua costruito sull'IT nuova + verifica
"""
from __future__ import annotations

import argparse
import copy
import difflib
import json
import re
import sys
import zipfile
from pathlib import Path

from lxml import etree

from . import align as align_mod
from . import brief as brief_mod
from .align import numbers
from .docx_model import (Docx, XML_SPACE, fmt_signature, parse_markup, replace_across_runs, run_text,
                         set_paragraph_markup, strip_markup, wtag)

ROOT = Path(__file__).resolve().parent.parent
CHUNK_WORDS = 6500

LANG_NAMES = {"EN": "inglese", "DE": "tedesco", "ES": "spagnolo", "FR": "francese", "NL": "olandese",
              "PL": "polacco", "PT": "portoghese", "RO": "rumeno", "RU": "russo", "CZ": "ceco"}
LOCALES = {"EN": "en-GB", "DE": "de-DE", "ES": "es-ES", "FR": "fr-FR", "NL": "nl-NL", "PL": "pl-PL",
           "PT": "pt-PT", "RO": "ro-RO", "RU": "ru-RU", "CZ": "cs-CZ"}
# dicitura dell'intestazione già usata nella versione precedente di ogni lingua
HEADER_LABEL = {"EN": "Version no", "DE": "Version Nr.", "ES": "Versión n.º", "FR": "Version n°", "NL": "Versie nr.",
                "PL": "Wersja nr.", "PT": "Versão n.", "RO": "Versiunea nr.", "RU": "Версия номер", "CZ": "Verze č."}
LINK_RE = re.compile(r"https?://[^\s<>»”)]+[^\s<>»”).,;:]|[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def norm(s: str) -> str:
    return " ".join(s.split())


# ---------- provenienza dal redline ----------
def redline_pairs(path: Path) -> list[tuple[str, str]]:
    """Per ogni paragrafo del redline: (testo con revisioni rifiutate, testo con revisioni accettate)."""
    with zipfile.ZipFile(path) as z:
        body = etree.fromstring(z.read("word/document.xml")).find(wtag("body"))
    out = []
    for p in body.iter(wtag("p")):
        acc, rej = [], []
        for el in p.iter(wtag("t"), wtag("delText")):
            anc = {etree.QName(a).localname for a in el.iterancestors() if a is not p}
            if el.tag == wtag("delText") or anc & {"del", "moveFrom"}:
                rej.append(el.text or "")
            elif anc & {"ins", "moveTo"}:
                acc.append(el.text or "")
            else:
                acc.append(el.text or "")
                rej.append(el.text or "")
        a, r = norm("".join(acc)), norm("".join(rej))
        if a or r:
            out.append((r, a))
    return out


def _kept(old: str, new: str) -> float:
    o, n = old.split(), new.split()
    m = sum(b.size for b in difflib.SequenceMatcher(None, o, n, autojunk=False).get_matching_blocks())
    return m / max(len(n), 1)


def _best(text: str, cands: list[tuple[int, str]], floor: float):
    best, score = None, floor
    sm = difflib.SequenceMatcher(None, autojunk=False)
    sm.set_seq2(text.split())
    for i, c in cands:
        sm.set_seq1(c.split())
        if sm.quick_ratio() > score:
            r = sm.ratio()
            if r > score:
                best, score = i, r
    return best


def lineage(it_prev: Docx, it_new: Docx, redline: Path | None, changes: dict) -> dict[int, dict]:
    """new_idx -> {prev_idx, kept, cat}. Il redline dà l'origine certa; il diff copre ciò che il redline non traccia."""
    prev = [(p.idx, norm(p.text)) for p in it_prev.paras if not p.in_toc and not p.empty]
    prev_exact = {}
    for i, t in prev:
        prev_exact.setdefault(t, i)
    pairs = redline_pairs(redline) if redline else []
    acc = [(k, a) for k, (r, a) in enumerate(pairs) if a]
    acc_exact = {}
    for k, a in acc:
        acc_exact.setdefault(a, k)
    by_diff = {c["new_idx"]: c["prev_idx"] for c in changes["changes"]
               if not c["toc"] and c["kind"] in ("modify", "format", "whitespace") and c["prev_idx"] is not None}
    out = {}
    for p in it_new.paras:
        if p.in_toc or p.empty:
            continue
        x = norm(p.text)
        prev_idx = prev_exact.get(x)
        if prev_idx is None and pairs:
            k = acc_exact.get(x)
            if k is None:
                k = _best(x, acc, 0.5)
            if k is not None and pairs[k][0]:
                r = pairs[k][0]
                prev_idx = prev_exact.get(r)
                if prev_idx is None:
                    prev_idx = _best(r, prev, 0.7)
        if prev_idx is None:
            prev_idx = by_diff.get(p.idx)
        if prev_idx is None:
            out[p.idx] = {"prev_idx": None, "kept": 0.0, "cat": "nuovo"}
            continue
        old = norm(it_prev.paras[prev_idx].text)
        k = _kept(old, x)
        cat = "identico" if old == x else "ritoccato" if k >= 0.8 else "modificato" if k >= 0.4 else "riscritto"
        out[p.idx] = {"prev_idx": prev_idx, "kept": round(k, 2), "cat": cat}
    return out


def wdiff(old: str, new: str) -> str:
    a, b = old.split(), new.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            out.append(" ".join(a[i1:i2]))
        else:
            if i2 > i1:
                out.append("[-" + " ".join(a[i1:i2]) + "-]")
            if j2 > j1:
                out.append("{+" + " ".join(b[j1:j2]) + "+}")
    return " ".join(out)


# ---------- unità e blocchi ----------
def build_units(it_prev: Docx, it_new: Docx, redline: Path | None, changes: dict) -> list[dict]:
    lin = lineage(it_prev, it_new, redline, changes)
    units = []
    for p in it_new.paras:
        if p.empty:
            continue
        toc_title = p.in_toc and p.style.lower().startswith(("titolosommario", "tocheading"))
        if p.in_toc and not toc_title:
            continue
        l = lin.get(p.idx, {"prev_idx": None, "kept": 0.0, "cat": "nuovo"})
        units.append({"id": f"u{len(units) + 1:03d}", "idx": p.idx, "key": "TOC" if toc_title else p.key,
                      "article": "0" if toc_title else p.article, "level": p.level,
                      "words": len(p.text.split()), "markup": p.markup, **l})
    return units


def build_chunks(units: list[dict]) -> list[dict]:
    """k01 = frontespizio + art. 1 + tutti i titoli di articolo (fissano i termini); poi blocchi di articoli interi."""
    head = [u for u in units if u["article"] in ("0", "1") or u["level"] == 0]
    chunks = [{"id": "k01", "articles": ["0", "1", "titoli"], "units": [u["id"] for u in head]}]
    cur, words = None, 0
    arts = []
    for u in units:
        if u["article"] not in ("0", "1") and u["article"] not in arts:
            arts.append(u["article"])
    for art in arts:
        us = [u for u in units if u["article"] == art and u["level"] != 0]
        w = sum(u["words"] for u in us)
        if cur is None or words + w > CHUNK_WORDS:
            cur = {"id": f"k{len(chunks) + 1:02d}", "articles": [], "units": []}
            chunks.append(cur)
            words = 0
        cur["articles"].append(art)
        cur["units"] += [u["id"] for u in us]
        words += w
    by = {u["id"]: u for u in units}
    for c in chunks:
        c["words"] = sum(by[i]["words"] for i in c["units"])
    return chunks


# ---------- brief ----------
RULES = """## Regole (vincolanti)
1. Traduci OGNI paragrafo per intero in linguaggio tecnico-legale-commerciale {name}, quello di un contratto B2B
   redatto da un giurista madrelingua: preciso, formale, senza calchi dall'italiano. Nessuna omissione, nessuna aggiunta,
   nessuna spiegazione. Il senso giuridico deve essere equivalente all'IT v{new}.
2. Continuità con la versione precedente {lang} (v{old}), che è già pubblicata e vincolante:
   - paragrafo "identico": copia ALLA LETTERA la resa v{old} {lang};
   - "ritoccato"/"modificato": parti dalla resa v{old} {lang} e cambia solo ciò che il diff IT richiede
     (aggiunte, sostituzioni, RIMOZIONI [-...-]);
   - "riscritto"/"nuovo": traduci ex novo, ma con la terminologia e le formule della v{old} {lang}.
   L'abbinamento con la resa v{old} è automatico: se il testo {lang} mostrato non corrisponde all'IT v{old} indicato,
   cerca il paragrafo giusto in `{ref}` e usa quello.
3. Terminologia: i termini contrattuali già usati nella v{old} {lang} NON cambiano (glossario e tabella termini sotto
   sono vincolanti; mai sinonimi). Per un concetto nuovo cerca prima in `{ref}`; se non c'è scegli la resa legale
   standard nella lingua e riportala in "new_terms". Un termine definito con iniziale maiuscola in IT resta un termine
   definito (maiuscola secondo l'uso già adottato nella v{old} {lang}), sempre reso allo stesso modo.
4. Formattazione: riporta <b>, <i>, <u> sulle parole corrispondenti, con lo STESSO numero di segmenti dell'IT v{new}.
   Nessun altro tag, nessun a capo aggiunto.
5. Numeri, importi, termini in giorni, rinvii ad articoli ("art. 12.6"), riferimenti normativi italiani ed europei,
   nomi propri, marchi (Fleequid®, Fleequid Care®, TrustReport...), e-mail e URL: invariati nel valore. Importi e
   migliaia con la convenzione tipografica della v{old} {lang}. I rinvii ad articoli seguono la numerazione dell'IT v{new}.
6. Non tradurre i nomi commerciali lasciati in inglese nell'IT (es. Buy Now, Dealer Sales, Marketplace) salvo che la
   v{old} {lang} li traduca già.
"""


def _terms(work: Path, lang: str) -> list[dict]:
    p = work / "rb" / lang / "terms.json"
    return json.loads(p.read_text()) if p.exists() else []


def write_briefs(c, lang: str, only: str | None = None) -> list[Path]:
    work = c.work
    units = json.loads((work / "units.json").read_text())
    chunks = json.loads((work / "chunks.json").read_text())
    by = {u["id"]: u for u in units}
    it_prev = Docx(c.prev_docs["IT"])
    tgt = Docx(c.prev_docs[lang])
    al = align_mod.align(it_prev, tgt)
    gl = brief_mod.build_glossary(it_prev, tgt, al, lang, f"{c.family} v{c.v_from}")
    ref = f"work/refs/general_{lang}.txt"
    brief_mod.general_text_dump(c.prev_docs[lang], ROOT / ref)
    terms = _terms(work, lang)
    done_k01 = {}
    p01 = work / "rb" / lang / "tr_k01.json"
    if p01.exists():
        done_k01 = json.loads(p01.read_text()).get("translations", {})
    out_dir = work / "rb" / lang
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for ch in chunks:
        if only and ch["id"] != only:
            continue
        L = [f"# Brief {lang} — blocco {ch['id']} (articoli: {', '.join(ch['articles'])}; {ch['words']} parole IT)\n",
             f"Documento: Termini e Condizioni Generali Fleequid, dalla v{c.v_from} alla v{c.v_to} (riscrittura ampia).",
             f"- Testo completo IT v{c.v_to}: `{work.relative_to(ROOT)}/it_new.txt`",
             f"- Testo completo IT v{c.v_from}: `work/refs/general_IT_v{c.v_from}.txt`",
             f"- Testo completo {lang} v{c.v_from}: `{ref}`\n",
             RULES.format(lang=lang, name=LANG_NAMES[lang], old=c.v_from, new=c.v_to, ref=ref)]
        L.append(f"## Glossario dalle versioni pubblicate (IT → {lang})\n")
        L += [f"- {strip_markup(g['it'])} → {strip_markup(g['tr'])}" for g in gl]
        if terms and ch["id"] != "k01":
            L.append(f"\n## Tabella termini v{c.v_to} già fissati per {lang} (art. 1 e titoli: vincolante)\n")
            L += [f"- {t['it']} → {t['tr']}" for t in terms]
        if ch["id"] == "k01":
            L.append("\n## Nota sul blocco k01\nContiene il frontespizio, l'art. 1 (Definizioni) e TUTTI i titoli di "
                     "articolo: le rese scelte qui diventano vincolanti per il resto del documento. In \"new_terms\" "
                     "elenca OGNI termine definito nuovo rispetto alla v" + str(c.v_from) + " con la resa scelta e la fonte. "
                     "L'unità con chiave TOC è il titolo dell'indice: usa la parola già usata nella v" + str(c.v_from) + f" {lang}.\n")
        L.append("\n## Paragrafi da tradurre\n")
        seen_art = None
        for uid in ch["units"]:
            u = by[uid]
            if ch["id"] != "k01" and u["article"] != seen_art:
                seen_art = u["article"]
                h = next((x for x in units if x["article"] == seen_art and x["level"] == 0), None)
                if h:
                    L.append(f"#### Articolo {seen_art} — {strip_markup(h['markup'])}"
                             + (f" → {strip_markup(done_k01[h['id']])}" if h["id"] in done_k01 else "") + "\n")
            pct = f", {int(u['kept'] * 100)}% dal testo v{c.v_from}" if u["prev_idx"] is not None else ""
            L.append(f"### {uid} — [{u['key']}] ({u['cat']}{pct})\n")
            L.append(f"**IT v{c.v_to}:**\n\n{u['markup']}\n")
            if u["prev_idx"] is not None:
                pp = it_prev.paras[u["prev_idx"]]
                a = al.get(u["prev_idx"], {})
                tp = tgt.paras[a["target_idx"]].markup if a.get("target_idx") is not None else None
                if u["cat"] != "identico":
                    L.append(f"**IT v{c.v_from} [{pp.key}]:**\n\n{pp.markup}\n")
                    if u["cat"] != "riscritto":
                        L.append(f"**Diff IT:**\n\n{wdiff(pp.text, strip_markup(u['markup']))}\n")
                L.append(f"**{lang} v{c.v_from} (abbinamento {a.get('confidence', 'none')}):**\n\n"
                         f"{tp or '(non abbinato: cercalo nel testo completo)'}\n")
        L.append("\n## Output richiesto\n")
        L.append(f"File `{(out_dir / ('tr_' + ch['id'] + '.json')).relative_to(ROOT)}` (UTF-8) con questa forma:\n")
        L.append("```json\n" + json.dumps({
            "lang": lang, "chunk": ch["id"],
            "translations": {ch["units"][0]: "<paragrafo completo con eventuali <b>/<i>/<u>>", "...": "..."},
            "new_terms": [{"it": "...", "tr": "...", "why": "fonte o motivo"}],
            "notes": ["dubbi e punti da far validare"],
        }, ensure_ascii=False, indent=1) + "\n```\n")
        L.append(f"Unità richieste ({len(ch['units'])}): {', '.join(ch['units'])}\n")
        path = out_dir / f"brief_{ch['id']}.md"
        path.write_text("\n".join(L))
        written.append(path)
    return written


# ---------- controlli ----------
def check_chunk(work: Path, lang: str, chunk_id: str) -> list[str]:
    units = {u["id"]: u for u in json.loads((work / "units.json").read_text())}
    ch = next(c for c in json.loads((work / "chunks.json").read_text()) if c["id"] == chunk_id)
    p = work / "rb" / lang / f"tr_{chunk_id}.json"
    if not p.exists():
        return [f"{chunk_id}: manca {p.name}"]
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        return [f"{chunk_id}: JSON non valido: {e}"]
    tr = data.get("translations", {})
    wp = work / "rb" / lang / "waivers.json"
    waived = set(json.loads(wp.read_text())) if wp.exists() else set()
    errs = []
    for uid in ch["units"]:
        u = units[uid]
        if uid not in tr or not str(tr[uid]).strip():
            errs.append(f"{uid} [{u['key']}]: traduzione mancante")
            continue
        try:
            segs = parse_markup(tr[uid])
        except ValueError as e:
            errs.append(f"{uid} [{u['key']}]: markup non valido: {e}")
            continue
        text = "".join(t for _, t in segs)
        it_segs = parse_markup(u["markup"])
        it_text = "".join(t for _, t in it_segs)
        if fmt_signature(segs) != fmt_signature(it_segs):
            errs.append(f"{uid} [{u['key']}]: B/I/U {fmt_signature(segs)} ≠ IT {fmt_signature(it_segs)}")
        if "\n" in text or "\t" in text:
            errs.append(f"{uid} [{u['key']}]: a capo o tabulazione non ammessi")
        if uid not in waived:
            miss = numbers(it_text) - numbers(text)
            if miss:
                errs.append(f"{uid} [{u['key']}]: numeri/rinvii mancanti {sorted(miss)}")
            extra = numbers(text) - numbers(it_text)
            if extra:
                errs.append(f"{uid} [{u['key']}]: numeri/rinvii non presenti nell'IT {sorted(extra)}")
        for link in LINK_RE.findall(it_text):
            if link not in text:
                errs.append(f"{uid} [{u['key']}]: link/e-mail mancante o alterato: {link}")
        ratio = len(text) / max(len(it_text), 1)
        if len(it_text) > 80 and not (0.55 <= ratio <= 1.9):
            errs.append(f"{uid} [{u['key']}]: lunghezza anomala ({ratio:.2f}× l'IT): omissione o aggiunta?")
    extra = set(tr) - set(ch["units"])
    if extra:
        errs.append(f"{chunk_id}: id estranei al blocco {sorted(extra)}")
    return errs


def derive_terms(work: Path, lang: str) -> list[dict]:
    """Termini definiti: segmenti in grassetto/corsivo dell'art. 1 IT abbinati per posizione a quelli della lingua."""
    units = {u["id"]: u for u in json.loads((work / "units.json").read_text())}
    data = json.loads((work / "rb" / lang / "tr_k01.json").read_text())
    terms, seen = [], set()

    def add(it, tr):
        it, tr = it.strip(" :.“”\"«»„"), tr.strip(" :.“”\"«»„‚‘’")
        if it and tr and (it, tr) not in seen:
            seen.add((it, tr))
            terms.append({"it": it, "tr": tr})

    for uid, t in data["translations"].items():
        u = units[uid]
        a = [s for f, s in parse_markup(u["markup"]) if f and s.strip()]
        b = [s for f, s in parse_markup(t) if f and s.strip()]
        if u["article"] == "1" and len(a) == len(b):
            for x, y in zip(a, b):
                add(x, y)
        elif u["level"] == 0:
            add("Titolo art. " + u["article"] + ": " + strip_markup(u["markup"]), strip_markup(t))
    for nt in data.get("new_terms", []):
        if nt.get("it") and nt.get("tr"):
            add(nt["it"], nt["tr"])
    (work / "rb" / lang / "terms.json").write_text(json.dumps(terms, ensure_ascii=False, indent=1))
    return terms


# ---------- costruzione del Word ----------
def _set_markup(p, markup: str):
    """Come set_paragraph_markup, ma i collegamenti ipertestuali dell'IT restano tali sul loro testo."""
    links = [(norm("".join(t.text or "" for t in h.iter(wtag("t")))), copy.deepcopy(h))
             for h in p.iter(wtag("hyperlink"))]
    for h in list(p.iter(wtag("hyperlink"))):
        h.getparent().remove(h)
    if not any(run_text(r).strip() for r in p.iter(wtag("r"))):
        # paragrafo fatto solo di link: serve un run di base da cui ereditare il formato
        r = etree.SubElement(p, wtag("r"))
        etree.SubElement(r, wtag("t")).text = "x"
    set_paragraph_markup(p, markup)
    for text, h in links:
        hit = None
        for r in p.findall(wtag("r")):
            ts = r.findall(wtag("t"))
            if len(ts) == 1 and text in (ts[0].text or ""):
                hit = (r, ts[0])
                break
        if hit is None:
            raise ValueError(f"link «{text}» non ritrovato nel paragrafo tradotto")
        r, t = hit
        before, after = t.text.split(text, 1)
        tail = copy.deepcopy(r)
        t.text = before
        if before != before.strip():
            t.set(XML_SPACE, "preserve")
        r.addnext(h)
        if after:
            tt = tail.find(wtag("t"))
            tt.text = after
            if after != after.strip():
                tt.set(XML_SPACE, "preserve")
            h.addnext(tail)
        if not before:
            r.getparent().remove(r)


def merged_translations(work: Path, lang: str) -> dict[str, str]:
    out = {}
    for ch in json.loads((work / "chunks.json").read_text()):
        out.update(json.loads((work / "rb" / lang / f"tr_{ch['id']}.json").read_text())["translations"])
    return out


def build_docx(c, lang: str) -> tuple[Path, list[str]]:
    work = c.work
    units = json.loads((work / "units.json").read_text())
    tr = merged_translations(work, lang)
    it_path = c.it_new_clean()
    d = Docx(it_path)
    log = []
    heads = {}
    for u in units:
        p = d.paras[u["idx"]]
        if u["key"] == "TOC":
            replace_across_runs(p.el, p.text.strip(), strip_markup(tr[u["id"]]))
            continue
        if u["level"] == 0:
            heads[u["key"]] = (p.text.strip(), strip_markup(tr[u["id"]]))
        _set_markup(p.el, tr[u["id"]])
    # indice: i titoli delle voci seguono i titoli tradotti (i numeri di pagina li ricalcola Word)
    n_toc = 0
    for p in d.paras:
        m = re.match(r"\s*(\d+)\.\t", p.text) if p.in_toc else None
        if m and m.group(1) in heads:
            old, new = heads[m.group(1)]
            if not replace_across_runs(p.el, old, new):
                raise SystemExit(f"Indice: titolo dell'art. {m.group(1)} non trovato nella voce")
            n_toc += 1
    log.append(f"indice: {n_toc} voci tradotte")
    for el in list(d.body.iter(wtag("lang"))):
        el.getparent().remove(el)
    hit = False
    for name, h in d.headers.items():
        for p in h.iter(wtag("p")):
            while replace_across_runs(p, "Versione nr.", HEADER_LABEL[lang]):
                hit = True
                d.mark_dirty(name)
    if not hit:
        raise SystemExit("Header: dicitura «Versione nr.» non trovata")
    styles = d.parts["word/styles.xml"]
    d.parts["word/styles.xml"] = styles.replace(b'<w:lang w:val="it-IT"', f'<w:lang w:val="{LOCALES[lang]}"'.encode(), 1)
    d.mark_dirty("word/document.xml")
    out = c.out_name(lang)
    d.save(out)
    log.append(f"header: «{HEADER_LABEL[lang]} {c.changes['version_new'][0]}»")
    return out, log


def verify_docx(c, lang: str) -> list[str]:
    units = json.loads((c.work / "units.json").read_text())
    tr = merged_translations(c.work, lang)
    it = Docx(c.it_new_clean())
    out = Docx(c.out_name(lang))
    errs = []
    if len(it.paras) != len(out.paras):
        errs.append(f"paragrafi: IT {len(it.paras)}, {lang} {len(out.paras)}")
        return errs
    if [p.key for p in it.paras] != [p.key for p in out.paras]:
        errs.append("numerazione/chiavi diverse dall'IT")
    for a, b in zip(it.paras, out.paras):
        if a.ppr_xml() != b.ppr_xml():
            errs.append(f"[{a.key}] proprietà di paragrafo diverse dall'IT")
        if a.empty != b.empty:
            errs.append(f"[{a.key}] vuoto/non vuoto diverso dall'IT")
    for u in units:
        if u["key"] == "TOC":
            continue
        po = out.paras[u["idx"]]
        if norm(po.text) != norm(strip_markup(tr[u["id"]])):
            errs.append(f"{u['id']} [{u['key']}]: testo nel Word diverso dalla traduzione")
        if fmt_signature(po.segs) != fmt_signature(it.paras[u["idx"]].segs):
            errs.append(f"{u['id']} [{u['key']}]: B/I/U diverso dall'IT")
        n_it = len(list(it.paras[u["idx"]].el.iter(wtag("hyperlink"))))
        if n_it != len(list(po.el.iter(wtag("hyperlink")))):
            errs.append(f"{u['id']} [{u['key']}]: collegamenti ipertestuali persi")
    htxt = " ".join(out.header_texts().values())
    vn = c.changes["version_new"][0]
    if f"{HEADER_LABEL[lang]} {vn}" not in htxt:
        errs.append(f"header: atteso «{HEADER_LABEL[lang]} {vn}», trovato «{htxt}»")
    if any(p.highlighted for p in out.paras):
        errs.append("testo evidenziato")
    with zipfile.ZipFile(it.path) as za, zipfile.ZipFile(out.path) as zb:
        if set(za.namelist()) != set(zb.namelist()):
            errs.append("parti zip diverse dall'IT")
        for n in za.namelist():
            if n in ("word/document.xml", "word/styles.xml") or n.startswith(("word/header", "word/footer")):
                continue
            if za.read(n) != zb.read(n):
                errs.append(f"parte modificata inattesa: {n}")
    return errs


# ---------- CLI ----------
def main(argv=None):
    from .__main__ import Ctx

    ap = argparse.ArgumentParser(prog="tcupdate.rebuild", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["prepare", "brief", "check", "terms", "build"])
    ap.add_argument("--family", required=True)
    ap.add_argument("--from", dest="from_", type=int, required=True)
    ap.add_argument("--to", type=int, required=True)
    ap.add_argument("--draft", required=True)
    ap.add_argument("--redline")
    ap.add_argument("--lang")
    ap.add_argument("--chunk")
    a = ap.parse_args(argv)
    a.langs = a.lang
    c = Ctx(a)
    if a.command == "prepare":
        it_prev, it_new = Docx(c.prev_docs["IT"]), Docx(c.it_new_clean())
        units = build_units(it_prev, it_new, Path(a.redline) if a.redline else None, c.changes)
        chunks = build_chunks(units)
        (c.work / "units.json").write_text(json.dumps(units, ensure_ascii=False, indent=1))
        (c.work / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False, indent=1))
        (c.work / "it_new.txt").write_text("\n".join(f"[{p.key}] {p.text}" for p in it_new.paras if not p.empty))
        brief_mod.general_text_dump(c.prev_docs["IT"], ROOT / "work" / "refs" / f"general_IT_v{c.v_from}.txt")
        cats = {}
        for u in units:
            k = cats.setdefault(u["cat"], [0, 0])
            k[0] += 1
            k[1] += u["words"]
        print(f"unità: {len(units)}; parole: {sum(u['words'] for u in units)}")
        for k, (n, w) in sorted(cats.items()):
            print(f"  {k}: {n} paragrafi, {w} parole")
        for ch in chunks:
            print(f"  {ch['id']}: art. {', '.join(ch['articles'])} — {len(ch['units'])} unità, {ch['words']} parole")
        return
    if not a.lang:
        ap.error("serve --lang")
    lang = a.lang.upper()
    chunks = [ch["id"] for ch in json.loads((c.work / "chunks.json").read_text())]
    if a.command == "brief":
        for p in write_briefs(c, lang, a.chunk):
            print(p.relative_to(ROOT))
    elif a.command == "check":
        bad = False
        for k in ([a.chunk] if a.chunk else chunks):
            e = check_chunk(c.work, lang, k)
            bad |= bool(e)
            print(f"{k}: OK" if not e else "\n".join(e))
        sys.exit(1 if bad else 0)
    elif a.command == "terms":
        t = derive_terms(c.work, lang)
        print(f"{len(t)} termini → {(c.work / 'rb' / lang / 'terms.json').relative_to(ROOT)}")
    elif a.command == "build":
        errs = [e for k in chunks for e in check_chunk(c.work, lang, k)]
        if errs:
            raise SystemExit("Traduzioni non valide:\n" + "\n".join(errs))
        out, log = build_docx(c, lang)
        errs = verify_docx(c, lang)
        (c.work / "translations").mkdir(exist_ok=True)
        (c.work / "translations" / f"{lang}.json").write_text(
            json.dumps({"lang": lang, "translations": merged_translations(c.work, lang)}, ensure_ascii=False, indent=1))
        print("\n".join(log))
        print(f"→ {out.relative_to(ROOT)}")
        print("verifica: OK" if not errs else "verifica: ERRORI\n" + "\n".join(errs))
        sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
