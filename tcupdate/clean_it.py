"""IT nuova: rimuove SOLO le evidenziazioni e applica le correzioni di refusi approvate.

Le correzioni stanno in `work/<famiglia>/v<N>/it_fixes.json`:
[{"key": "9.4", "old": "arti. 4.2", "new": "art. 4.2"}, ...]
Grassetti, corsivi, sottolineati e ogni altra proprietà restano intatti.
"""
from __future__ import annotations

import json
from pathlib import Path

from .docx_model import Docx, remove_highlight, replace_across_runs


def run(draft: Path, out: Path, fixes_path: Path | None) -> list[str]:
    d = Docx(draft)
    log = []
    fixes = json.loads(fixes_path.read_text()) if fixes_path and fixes_path.exists() else []
    for fx in fixes:
        p = d.by_key.get(fx["key"])
        if p is None:
            raise SystemExit(f"Correzione IT: chiave {fx['key']} inesistente")
        if not replace_across_runs(p.el, fx["old"], fx["new"]):
            raise SystemExit(f"Correzione IT: «{fx['old']}» non trovato in {fx['key']}")
        log.append(f"{fx['key']}: «{fx['old']}» → «{fx['new']}»")
    n = remove_highlight(d.tree)
    for name, h in d.headers.items():
        if remove_highlight(h):
            d.mark_dirty(name)
    d.mark_dirty("word/document.xml")
    d.save(out)
    log.append(f"evidenziazioni rimosse: {n}")
    return log
