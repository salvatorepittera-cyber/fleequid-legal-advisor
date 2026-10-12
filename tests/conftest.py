"""Contesto di prova: il lavoro reale General T&C v8 → v9 (inglese) copiato in una cartella temporanea.

I test non scrivono mai nell'archivio né in `work/`: leggono i Word del repo e scrivono solo nella copia.
"""
import shutil
from argparse import Namespace
from pathlib import Path

import pytest

from tcupdate import brief as brief_mod
from tcupdate import rebuild
from tcupdate.__main__ import Ctx

REPO = Path(__file__).resolve().parent.parent
V9_DIR = REPO / "T&C" / "General T&C" / "Vers 9 - Multilanguage - Q4 2026"
DRAFT = V9_DIR / "9_Termini_e_Condizioni_Generali_Fleequid_F0009_2026_BOZZA_STUDIO.docx"
REDLINE = V9_DIR / "9_Versione_Termini_e_Condizioni_Generali_Fleequid_Versione_nr_F0009_2026_DEF_2_redline.docx"
CLI = ["--family", "General T&C", "--from", "8", "--to", "9", "--draft", str(DRAFT)]


@pytest.fixture
def v9(tmp_path, monkeypatch):
    """Ctx della v9 con `work/`, glossario e Word di output dirottati sulla cartella temporanea."""
    real_work = REPO / "work" / "general-t-c" / "v9"
    work = tmp_path / "work" / "general-t-c" / "v9"
    (work / "rb").mkdir(parents=True)
    for name in ("units.json", "chunks.json", "changes.json"):
        shutil.copy(real_work / name, work / name)
    shutil.copytree(real_work / "rb" / "EN", work / "rb" / "EN")
    shutil.copytree(REPO / "glossary", tmp_path / "glossary")
    monkeypatch.setattr(rebuild, "ROOT", tmp_path)
    monkeypatch.setattr(brief_mod, "GLOSSARY_DIR", tmp_path / "glossary")
    c = Ctx(Namespace(family="General T&C", from_=8, to=9, draft=str(DRAFT), langs="EN"))
    c.work = work
    real_out = c.out_name
    # l'IT pulita si legge dall'archivio; i Word delle lingue si scrivono nella cartella temporanea
    c.out_name = lambda lang: real_out(lang) if lang == "IT" else tmp_path / real_out(lang).name
    return c
