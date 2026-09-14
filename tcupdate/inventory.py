"""Scansione dell'archivio T&C: famiglie, versioni, file per lingua (codici lingua normalizzati)."""
from __future__ import annotations

import re
from pathlib import Path

LANGS = ["IT", "EN", "DE", "ES", "FR", "NL", "PL", "PT", "RO", "RU", "CZ"]
TARGET_LANGS = [l for l in LANGS if l != "IT"]

# alias usati storicamente nei nomi file
ALIASES = {
    "IT": "IT", "ITA": "IT",
    "EN": "EN", "ENG": "EN", "ING": "EN",
    "DE": "DE", "TED": "DE", "GER": "DE",
    "ES": "ES", "SPA": "ES",
    "FR": "FR", "FRA": "FR",
    "NL": "NL", "OLA": "NL",
    "PL": "PL", "POL": "PL",
    "PT": "PT", "POR": "PT",
    "RO": "RO", "RUM": "RO",
    "RU": "RU", "RUS": "RU",
    "CZ": "CZ", "CS": "CZ", "CECO": "CZ",
}

ROOT = Path(__file__).resolve().parent.parent
TC_ROOT = ROOT / "T&C"


def lang_of(path: Path) -> str | None:
    stem = path.name
    while stem.lower().endswith(".docx"):
        stem = stem[:-5]
    tokens = [t for t in re.split(r"[_\s.\-]+", stem.upper()) if t]
    for t in reversed(tokens[-3:]):
        if t in ALIASES:
            return ALIASES[t]
    return None


def version_of(folder: Path) -> int | None:
    m = re.match(r"\s*Vers(?:ione)?\.?\s*(\d+)", folder.name, re.I)
    return int(m.group(1)) if m else None


def families() -> dict[str, dict[int, Path]]:
    out: dict[str, dict[int, Path]] = {}
    for fam in sorted(p for p in TC_ROOT.iterdir() if p.is_dir()):
        vers = {version_of(v): v for v in fam.iterdir() if v.is_dir() and version_of(v) is not None}
        if not vers:
            # famiglia senza sottocartelle di versione (es. 1 Euro Auctions): versione 1 = cartella stessa
            vers = {1: fam}
        out[fam.name] = dict(sorted(vers.items()))
    return out


def docs_by_lang(folder: Path) -> dict[str, Path]:
    res: dict[str, Path] = {}
    for f in sorted(folder.glob("*.docx*")):
        if f.name.startswith("~$") or not f.is_file():
            continue
        lang = lang_of(f)
        if lang:
            if lang in res:
                raise ValueError(f"Due file per la lingua {lang} in {folder}: {res[lang].name}, {f.name}")
            res[lang] = f
    if not res and re.search(r"\bIT\b", folder.name):
        # cartelle storiche solo italiane: il file senza codice lingua è l'IT
        files = [f for f in sorted(folder.glob("*.docx")) if not f.name.startswith("~$")]
        if len(files) == 1:
            res["IT"] = files[0]
    return res


def find_family(name: str) -> str:
    fams = families()
    if name in fams:
        return name
    cand = [f for f in fams if name.lower() in f.lower()]
    if len(cand) != 1:
        raise SystemExit(f"Famiglia '{name}' ambigua o assente. Disponibili: {list(fams)}")
    return cand[0]


def draft_in(folder: Path) -> Path:
    """La bozza IT dello studio nella cartella della nuova versione (quella con evidenziazioni)."""
    cands = [f for f in folder.glob("*.docx") if not f.name.startswith("~$") and "_DEF_" not in f.name.upper()]
    if len(cands) != 1:
        raise SystemExit(f"Bozza IT non individuabile in {folder}: {[c.name for c in cands]}. Passa --draft.")
    return cands[0]


def print_inventory():
    for fam, vers in families().items():
        print(f"## {fam}")
        for v, folder in vers.items():
            langs = docs_by_lang(folder)
            missing = [l for l in LANGS if l not in langs]
            print(f"  v{v}: {folder.name} — {len(langs)} lingue" + (f" (mancano: {', '.join(missing)})" if missing else ""))
