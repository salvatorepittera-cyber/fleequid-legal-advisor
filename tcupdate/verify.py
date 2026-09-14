"""Controlli bloccanti su un Word di output rispetto alla versione precedente della stessa lingua."""
from __future__ import annotations

import difflib
import zipfile
from pathlib import Path

from .align import numbers
from .docx_model import Docx, canonical, fmt_signature

TEXT_KINDS = {"modify", "format", "whitespace", "insert"}


def run(changes: dict, it_prev: Docx, it_new: Docx, prev: Docx, out: Docx, al: dict | None,
        is_it: bool = False) -> tuple[list[str], list[str]]:
    errors, warns = [], []
    body = [c for c in changes["changes"] if not c["toc"]]
    n_ins = sum(1 for c in body if c["kind"] == "insert")
    n_del = sum(1 for c in body if c["kind"] == "delete")

    # 1. conteggio paragrafi
    base = it_prev if is_it else prev
    exp = len(base.paras) + n_ins - n_del
    if is_it:
        exp = len(it_new.paras)
    if len(out.paras) != exp:
        errors.append(f"paragrafi: attesi {exp}, trovati {len(out.paras)}")

    # 2. paragrafi non toccati identici (XML canonico), TOC escluso
    if not is_it:
        touched = set()
        for c in body:
            if c["prev_idx"] is not None and al:
                t = al.get(c["prev_idx"], {}).get("target_idx")
                if t is not None:
                    touched.add(t)
        pa = [(p.idx, canonical(p.el)) for p in prev.paras if not p.in_toc]
        pb = [(p.idx, canonical(p.el)) for p in out.paras if not p.in_toc]
        sm = difflib.SequenceMatcher(None, [x for _, x in pa], [x for _, x in pb], autojunk=False)
        matched_prev = set()
        for a, b, size in sm.get_matching_blocks():
            matched_prev.update(pa[a + k][0] for k in range(size))
        unexpected = [prev.paras[i].key for i, _ in pa if i not in matched_prev and i not in touched]
        if unexpected:
            errors.append(f"paragrafi cambiati senza essere nel diff: {unexpected[:10]}")
        # numerazione/chiavi: le chiavi non vuote di output devono coincidere con quelle IT nuova se prev≡IT prev
        k_it_prev = [p.key for p in it_prev.paras if not p.in_toc and not p.empty]
        k_prev = [p.key for p in prev.paras if not p.in_toc and not p.empty]
        k_new = [p.key for p in it_new.paras if not p.in_toc and not p.empty]
        k_out = [p.key for p in out.paras if not p.in_toc and not p.empty]
        if k_prev == k_it_prev:
            if k_out != k_new:
                d = [x for x in difflib.unified_diff(k_new, k_out, lineterm="", n=0)][2:8]
                errors.append(f"struttura/numerazione diversa dall'IT nuova: {d}")
        else:
            warns.append("struttura lingua precedente non parallela all'IT: controllo numerazione per chiavi saltato")

    # 3. parti zip non toccate identiche
    with zipfile.ZipFile(prev.path if not is_it else it_new.path) as za, zipfile.ZipFile(out.path) as zb:
        na, nb = set(za.namelist()), set(zb.namelist())
        if na != nb:
            errors.append(f"parti zip diverse: {sorted(na ^ nb)}")
        for n in sorted(na & nb):
            if n == "word/document.xml" or n.startswith("word/header") or n.startswith("word/footer"):
                continue
            if za.read(n) != zb.read(n):
                errors.append(f"parte modificata inattesa: {n}")

    # 4. evidenziazioni
    hl = sum(1 for _ in out.tree.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}highlight"))
    if hl:
        (errors if is_it else warns).append(f"evidenziazioni presenti: {hl}")

    # 5. header
    vp, vn = changes.get("version_prev") or [], changes.get("version_new") or []
    htxt = " ".join(out.header_texts().values())
    for v in vn:
        if v not in htxt:
            errors.append(f"header: manca il codice {v}")
    for v in vp:
        if v not in vn and v in htxt:
            errors.append(f"header: resta il vecchio codice {v}")

    # 6. per paragrafo modificato: formattazione e numeri
    out_by_key = out.by_key
    for c in body:
        if c["kind"] not in TEXT_KINDS:
            continue
        pn = it_new.paras[c["new_idx"]]
        if pn.empty:
            continue
        po = out_by_key.get(pn.key)
        if po is None:
            errors.append(f"{c['id']} [{pn.key}]: paragrafo assente nell'output")
            continue
        sig_it, sig_out = fmt_signature(pn.segs), fmt_signature(po.segs)
        if sig_it != sig_out:
            errors.append(f"{c['id']} [{pn.key}]: formattazione B/I/U {sig_out} ≠ IT nuova {sig_it}")
        n_new = numbers(pn.text)
        n_out = numbers(po.text)
        missing = n_new - n_out
        if missing:
            errors.append(f"{c['id']} [{pn.key}]: numeri/rinvii mancanti {sorted(missing)}")
        if c["prev_markup"] is not None:
            n_prev_it = numbers(it_prev.paras[c["prev_idx"]].text)
            removed = (n_prev_it - n_new) & n_out
            if removed:
                errors.append(f"{c['id']} [{pn.key}]: restano numeri rimossi dall'IT {sorted(removed)}")
        if not is_it and c["prev_idx"] is not None and al:
            t = al.get(c["prev_idx"], {}).get("target_idx")
            if t is not None and prev.paras[t].markup == po.markup and pn.text != it_prev.paras[c["prev_idx"]].text:
                warns.append(f"{c['id']} [{pn.key}]: testo identico alla versione precedente (ok solo se refuso IT)")
    return errors, warns
