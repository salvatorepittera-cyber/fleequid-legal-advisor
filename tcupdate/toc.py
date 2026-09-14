"""Aggiornamento numeri di pagina dell'indice.

Word (AppleScript) apre una COPIA temporanea, aggiorna il sommario ed esporta il PDF; si legge l'indice
aggiornato dalla copia e si scrivono SOLO i numeri di pagina nel docx originale (che non viene risalvato da Word).
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .docx_model import Docx, wtag

SCRIPT = r'''
on run argv
  set inPath to item 1 of argv
  set pdfPath to item 2 of argv

  set tmpPath to item 3 of argv
  with timeout of 300 seconds
    tell application "Microsoft Word"
      set d to open file name (POSIX file inPath as text) without add to recent files
      if (count of tables of contents of d) > 0 then
        update table of contents 1 of d
      end if
      save as d file name (POSIX file pdfPath as text) file format format PDF
      save as d file name (POSIX file tmpPath as text) file format format document
      close d saving no
    end tell
  end timeout
end run
'''


def _toc_pages(doc: Docx) -> list[tuple[int, str]]:
    """(indice paragrafo TOC, numero di pagina) leggendo l'ultimo numero di ogni voce."""
    out = []
    for p in doc.paras:
        if p.in_toc:
            m = re.search(r"(\d+)\s*$", p.text)
            if m and re.match(r"\s*\d+\.", p.text):
                out.append((p.idx, m.group(1)))
    return out


def _set_page(p_el, page: str) -> bool:
    """Riscrive il risultato del campo PAGEREF (ultimo w:t numerico dopo il separatore)."""
    ts = [t for t in p_el.iter(wtag("t")) if (t.text or "").strip()]
    for t in reversed(ts):
        if re.fullmatch(r"\s*\d+\s*", t.text or ""):
            if t.text.strip() != page:
                t.text = page
                return True
            return False
    return False


def update(docx_path: Path, pdf_path: Path) -> list[str]:
    docx_path, pdf_path = Path(docx_path).resolve(), Path(pdf_path).resolve()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    # Word è in sandbox: la copia di lavoro sta nel suo container, dove può leggere/scrivere senza chiedere permessi
    word_tmp = Path.home() / "Library/Containers/com.microsoft.Word/Data/tmp"
    word_tmp.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=word_tmp) as td:
        src = Path(td) / "in.docx"
        tmp_out = Path(td) / "word_refreshed.docx"
        shutil.copy(docx_path, src)
        tmp_pdf = Path(td) / "out.pdf"
        r = subprocess.run(["osascript", "-", str(src), str(tmp_pdf), str(tmp_out)],
                           input=SCRIPT, text=True, capture_output=True, timeout=400)
        if r.returncode != 0:
            raise SystemExit(f"Word/AppleScript: {r.stderr.strip()}")
        shutil.copy(tmp_pdf, pdf_path)
        fresh = _toc_pages(Docx(tmp_out))
    doc = Docx(docx_path)
    mine = _toc_pages(doc)
    if len(mine) != len(fresh):
        raise SystemExit(f"Indice: {len(mine)} voci nel file, {len(fresh)} nella copia aggiornata da Word")
    log = []
    changed = False
    toc_paras = [p for p in doc.paras if p.idx in {i for i, _ in mine}]
    for p, (_, old), (_, new) in zip(toc_paras, mine, fresh):
        if old != new:
            if _set_page(p.el, new):
                changed = True
                log.append(f"{p.text.split(chr(9))[1] if chr(9) in p.text else p.text[:40]}: pag. {old} → {new}")
    if changed:
        doc.mark_dirty("word/document.xml")
        doc.save(docx_path)
    return log or ["indice già allineato"]
