"""Diff IT versione precedente -> IT nuova bozza (testo + formattazione), paragrafo per paragrafo.

La fonte delle modifiche è SEMPRE il confronto prima/dopo; le evidenziazioni dello studio sono
solo un controllo incrociato (cambiato-non-evidenziato / evidenziato-non-cambiato).
"""
from __future__ import annotations

import difflib
import json
import re
from pathlib import Path

from .docx_model import Docx, fmt_signature, strip_markup

VERSION_RE = re.compile(r"\b(?:[A-Z]{2,5}-)?F\d{4}_\d{4}\b")
REF_RE = re.compile(r"\b(?:art(?:icol[oi])?\.?|artt\.)\s*(\d+(?:\.\d+)*)", re.I)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def word_diff(a: str, b: str) -> str:
    """Diff a parole leggibile: [-tolto-]{+aggiunto+}."""
    ta, tb = re.findall(r"\S+|\s+", a), re.findall(r"\S+|\s+", b)
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
        if op == "equal":
            out.append("".join(ta[i1:i2]))
        else:
            if i2 > i1:
                out.append("[-" + "".join(ta[i1:i2]) + "-]")
            if j2 > j1:
                out.append("{+" + "".join(tb[j1:j2]) + "+}")
    return "".join(out)


def typo_candidates(text: str) -> list[str]:
    found = []
    for pat, label in [
        (r"\S  +\S", "doppio spazio"),
        (r"\s+[,;.:](?!\d)", "spazio prima della punteggiatura"),
        (r"\b(\w+) \1\b", "parola ripetuta"),
        (r"\barti\.", "'arti.' (art.?)"),
        (r"\(\s|\s\)", "spazio dentro parentesi"),
    ]:
        for m in re.finditer(pat, text):
            ctx = text[max(0, m.start() - 25): m.end() + 25]
            found.append(f"{label}: «…{ctx}…»")
    return found


def diff_docs(prev: Docx, new: Docx) -> dict:
    A = [p for p in prev.paras]
    B = [p for p in new.paras]
    sa = [("TOC" if p.in_toc else "") + p.markup for p in A]
    sb = [("TOC" if p.in_toc else "") + p.markup for p in B]
    changes = []
    sm = difflib.SequenceMatcher(None, sa, sb, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        a_blk, b_blk = A[i1:i2], B[j1:j2]
        # accoppia i paragrafi del blocco per somiglianza di testo (in ordine)
        pairs = []
        if op == "replace":
            used_a, used_b = set(), set()
            match = {}
            # 1) stessa chiave logica (stesso articolo.paragrafo) -> modifica dello stesso paragrafo
            for jb, pb in enumerate(b_blk):
                for ja, pa in enumerate(a_blk):
                    if ja not in used_a and pa.key == pb.key and pa.in_toc == pb.in_toc and not pb.in_toc:
                        match[jb] = ja
                        used_a.add(ja)
                        break
            # 2) somiglianza di testo per i restanti, mantenendo l'ordine
            for jb, pb in enumerate(b_blk):
                if jb in match:
                    continue
                best, best_r = None, 0.45
                for ja, pa in enumerate(a_blk):
                    if ja in used_a or pa.in_toc != pb.in_toc:
                        continue
                    r = 1.0 if (pa.empty and pb.empty) else difflib.SequenceMatcher(
                        None, _norm(pa.text), _norm(pb.text), autojunk=False).ratio()
                    if r > best_r:
                        best, best_r = ja, r
                if best is not None:
                    match[jb] = best
                    used_a.add(best)
            pairs = []
            ia = 0
            for jb, pb in enumerate(b_blk):
                if jb in match:
                    for ja in range(ia, match[jb]):
                        if ja not in match.values():
                            pairs.append((a_blk[ja], None))
                    pairs.append((a_blk[match[jb]], pb))
                    ia = max(ia, match[jb] + 1)
                else:
                    pairs.append((None, pb))
            for ja in range(len(a_blk)):
                if ja not in match.values() and not any(x is a_blk[ja] for x, _ in pairs):
                    pairs.append((a_blk[ja], None))
        elif op == "delete":
            pairs = [(p, None) for p in a_blk]
        else:
            pairs = [(None, p) for p in b_blk]
        for pa, pb in pairs:
            ref = pb or pa
            if pa is not None and pb is not None:
                kind = "format" if _norm(pa.text) == _norm(pb.text) else "modify"
                if pa.text != pb.text and _norm(pa.text) == _norm(pb.text) and pa.markup != pb.markup:
                    kind = "format"
                elif pa.text != pb.text and _norm(pa.text) == _norm(pb.text):
                    kind = "whitespace"
            elif pb is not None:
                kind = "insert"
            else:
                kind = "delete"
            # ancora per inserimenti: paragrafo precedente nella versione nuova, mappato su prev
            anchor = None
            if kind == "insert":
                k = pb.idx - 1
                while k >= 0:
                    m = next((c for c in _pair_lookup(sm, k)), None)
                    if m is not None:
                        anchor = m
                        break
                    k -= 1
            changes.append({
                "id": f"c{len(changes) + 1:02d}",
                "kind": kind,
                "toc": bool(ref.in_toc),
                "prev_idx": pa.idx if pa else None,
                "new_idx": pb.idx if pb else None,
                "prev_key": pa.key if pa else None,
                "new_key": pb.key if pb else None,
                "article": (pb or pa).article,
                "anchor_prev_idx": anchor,
                "prev_markup": pa.markup if pa else None,
                "new_markup": pb.markup if pb else None,
                "word_diff": word_diff(pa.text if pa else "", pb.text if pb else ""),
                "highlighted_new": bool(pb and pb.highlighted),
                "new_fmt": fmt_signature(pb.segs) if pb else None,
            })
    changes.sort(key=lambda c: (c["toc"], c["new_idx"] if c["new_idx"] is not None else (c["prev_idx"] or 0)))
    for n, c in enumerate(changes, 1):
        c["id"] = f"c{n:02d}"
    # evidenziato ma identico
    changed_new = {c["new_idx"] for c in changes if c["new_idx"] is not None}
    hl_unchanged = [p.key for p in B if p.highlighted and p.idx not in changed_new and not p.in_toc]
    # header / versione
    hp, hn = prev.header_texts(), new.header_texts()
    headers = []
    for name in sorted(set(hp) | set(hn)):
        if hp.get(name) != hn.get(name):
            headers.append({"part": name, "prev": hp.get(name), "new": hn.get(name)})
    vp = sorted({m for t in hp.values() for m in VERSION_RE.findall(t)})
    vn = sorted({m for t in hn.values() for m in VERSION_RE.findall(t)})
    # rinvii interni presenti nei paragrafi nuovi/modificati
    typos = []
    for c in changes:
        if c["new_markup"] and not c["toc"]:
            prev_txt = strip_markup(c["prev_markup"] or "")
            for t in typo_candidates(strip_markup(c["new_markup"])):
                ctx = t.split("«…", 1)[1].rsplit("…»", 1)[0]
                if ctx in prev_txt:
                    continue  # già presente nella versione precedente
                typos.append({"id": c["id"], "key": c["new_key"], "issue": t})
    return {
        "prev_file": str(prev.path),
        "new_file": str(new.path),
        "prev_paragraphs": len(A),
        "new_paragraphs": len(B),
        "version_prev": vp,
        "version_new": vn,
        "headers": headers,
        "changes": changes,
        "highlighted_unchanged": hl_unchanged,
        "typo_candidates": typos,
    }


def _pair_lookup(sm: difflib.SequenceMatcher, new_idx: int):
    for a, b, size in sm.get_matching_blocks():
        if b <= new_idx < b + size:
            yield a + (new_idx - b)


def report_md(d: dict) -> str:
    L = []
    L.append(f"# Diff IT: `{Path(d['prev_file']).name}` → `{Path(d['new_file']).name}`\n")
    L.append(f"- Paragrafi: {d['prev_paragraphs']} → {d['new_paragraphs']}")
    L.append(f"- Codice versione: {', '.join(d['version_prev']) or '?'} → {', '.join(d['version_new']) or '?'}")
    body = [c for c in d["changes"] if not c["toc"]]
    toc = [c for c in d["changes"] if c["toc"]]
    L.append(f"- Modifiche nel corpo: {len(body)} (di cui NON evidenziate: {sum(1 for c in body if not c['highlighted_new'])})")
    L.append(f"- Voci d'indice cambiate: {len(toc)} (l'indice viene rigenerato)\n")
    L.append("## Modifiche nel corpo\n")
    L.append("| id | rif. | tipo | evid. | diff (parole) |\n|---|---|---|---|---|")
    for c in body:
        wd = c["word_diff"].replace("|", "\\|").replace("\n", " ")
        L.append(f"| {c['id']} | {c['new_key'] or c['prev_key']} | {c['kind']} | "
                 f"{'sì' if c['highlighted_new'] else '**NO**'} | {wd} |")
    L.append("\n## Controllo incrociato evidenziazioni\n")
    nh = [c for c in body if not c["highlighted_new"]]
    L.append("- Cambiati ma non evidenziati: " + (", ".join(f"{c['id']} ({c['new_key'] or c['prev_key']}, {c['kind']})" for c in nh) or "nessuno"))
    L.append("- Evidenziati ma identici alla versione precedente: " + (", ".join(d["highlighted_unchanged"]) or "nessuno"))
    L.append("\n## Intestazioni\n")
    for h in d["headers"]:
        L.append(f"- {h['part']}: «{h['prev']}» → «{h['new']}»")
    L.append("\n## Possibili refusi nel testo nuovo (da confermare)\n")
    for t in d["typo_candidates"]:
        L.append(f"- {t['id']} {t['key']}: {t['issue']}")
    if toc:
        L.append("\n## Indice\n")
        for c in toc:
            L.append(f"- {c['word_diff']}")
    return "\n".join(L) + "\n"


def run(prev_path, new_path, out_dir) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    d = diff_docs(Docx(prev_path), Docx(new_path))
    (out / "changes.json").write_text(json.dumps(d, ensure_ascii=False, indent=2))
    (out / "diff_report.md").write_text(report_md(d))
    return d
