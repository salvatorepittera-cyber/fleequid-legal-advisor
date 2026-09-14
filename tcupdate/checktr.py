"""Auto-controllo di un file di traduzioni prima dell'iniezione.

python3 -m tcupdate.checktr work/<famiglia>/v<N> <LANG> "<file IT nuova pulita>"
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from .align import numbers
from .docx_model import Docx, fmt_signature, parse_markup


def check(work: Path, lang: str, it_new_path: Path) -> list[str]:
    ch = json.loads((work / "changes.json").read_text())
    tr = json.loads((work / "translations" / f"{lang}.json").read_text())["translations"]
    it_new = Docx(it_new_path)
    errs = []
    from .docx_model import Docx as _D
    it_prev = _D(ch["prev_file"])
    for c in ch["changes"]:
        if c["toc"] or c["new_idx"] is None:
            continue
        pn = it_new.paras[c["new_idx"]]
        if pn.empty:
            continue
        if c["id"] not in tr:
            errs.append(f"{c['id']}: traduzione mancante")
            continue
        try:
            segs = parse_markup(tr[c["id"]])
        except ValueError as e:
            errs.append(f"{c['id']}: markup non valido: {e}")
            continue
        text = "".join(t for _, t in segs)
        if fmt_signature(segs) != fmt_signature(pn.segs):
            errs.append(f"{c['id']} [{pn.key}]: B/I/U {fmt_signature(segs)} ≠ IT {fmt_signature(pn.segs)}")
        miss = numbers(pn.text) - numbers(text)
        if miss:
            errs.append(f"{c['id']} [{pn.key}]: numeri mancanti {sorted(miss)}")
        if c["prev_idx"] is not None:
            removed = (numbers(it_prev.paras[c["prev_idx"]].text) - numbers(pn.text)) & numbers(text)
            if removed:
                errs.append(f"{c['id']} [{pn.key}]: numeri rimossi ancora presenti {sorted(removed)}")
    extra = set(tr) - {c["id"] for c in ch["changes"]}
    if extra:
        errs.append(f"id sconosciuti: {sorted(extra)}")
    return errs


if __name__ == "__main__":
    e = check(Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]))
    print("OK" if not e else "\n".join(e))
    sys.exit(1 if e else 0)
