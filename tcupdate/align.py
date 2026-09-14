"""Allineamento paragrafi IT (versione precedente) ↔ lingua (versione precedente).

1. chiave logica identica (articolo.paragrafo, voce di lista, paragrafo libero) → validata con
   numeri presenti nel testo e rapporto di lunghezza;
2. per i restanti, allineamento in sequenza dentro lo stesso articolo;
3. ogni abbinamento ha una confidenza: key / key? / seq / none. Sotto "key" va confermato prima di iniettare.
"""
from __future__ import annotations

import difflib
import json
import re
from pathlib import Path

from .docx_model import Docx

NUM_RE = re.compile(r"\d+(?:[.,   ]\d{3})+(?!\d)|\d+(?:\.\d+)*")


def numbers(text: str) -> set[str]:
    out = set()
    for m in NUM_RE.findall(text):
        if re.fullmatch(r"\d{1,3}(?:[.,   ]\d{3})+", m):
            out.add(re.sub(r"\D", "", m))
        else:
            out.add(m)
    return out


def _plausible(a, b) -> bool:
    if a.empty and b.empty:
        return True
    if a.empty != b.empty:
        return False
    la, lb = len(a.text), len(b.text)
    if not (0.4 <= lb / max(la, 1) <= 2.5):
        return False
    na, nb = numbers(a.text), numbers(b.text)
    if na and not (na & nb) and len(na) >= 2:
        return False
    return True


def align(it_prev: Docx, target: Docx) -> dict[int, dict]:
    res: dict[int, dict] = {}
    used = set()
    for p in it_prev.paras:
        if p.in_toc:
            continue
        q = target.by_key.get(p.key)
        if q is not None and not q.in_toc:
            res[p.idx] = {"target_idx": q.idx, "confidence": "key" if _plausible(p, q) else "key?"}
            used.add(q.idx)
    # sequenza per articolo per i non abbinati
    by_art_it: dict[str, list] = {}
    by_art_tg: dict[str, list] = {}
    for p in it_prev.paras:
        if not p.in_toc and p.idx not in res and not p.empty:
            by_art_it.setdefault(p.article, []).append(p)
    for q in target.paras:
        if not q.in_toc and q.idx not in used and not q.empty:
            by_art_tg.setdefault(q.article, []).append(q)
    for art, ps in by_art_it.items():
        qs = by_art_tg.get(art, [])
        sig = lambda x: f"{x.level}|{x.num_id is not None}|{' '.join(sorted(numbers(x.text)))}"
        sm = difflib.SequenceMatcher(None, [sig(p) for p in ps], [sig(q) for q in qs], autojunk=False)
        for a, b, size in sm.get_matching_blocks():
            for k in range(size):
                res[ps[a + k].idx] = {"target_idx": qs[b + k].idx, "confidence": "seq"}
        for p in ps:
            res.setdefault(p.idx, {"target_idx": None, "confidence": "none"})
    for p in it_prev.paras:
        if not p.in_toc:
            res.setdefault(p.idx, {"target_idx": None, "confidence": "none"})
    return res


def needed_indices(changes: dict) -> set[int]:
    """Paragrafi IT prev che servono per applicare le modifiche (modificati, cancellati, ancore)."""
    s = set()
    for c in changes["changes"]:
        if c["toc"]:
            continue
        for k in ("prev_idx", "anchor_prev_idx"):
            if c.get(k) is not None:
                s.add(c[k])
    return s


def report(it_prev: Docx, target: Docx, al: dict, changes: dict, lang: str) -> tuple[str, list[str]]:
    need = needed_indices(changes)
    problems = []
    L = [f"# Allineamento IT → {lang}\n", f"- File lingua: `{target.path.name}`",
         f"- Paragrafi IT prev: {len(it_prev.paras)}, {lang} prev: {len(target.paras)}"]
    stats = {}
    for v in al.values():
        stats[v["confidence"]] = stats.get(v["confidence"], 0) + 1
    L.append(f"- Confidenza: {stats}\n")
    L.append("## Paragrafi usati dalle modifiche\n")
    L.append("| IT idx | chiave | conf. | IT (inizio) | lingua (inizio) |\n|---|---|---|---|---|")
    for i in sorted(need):
        p = it_prev.paras[i]
        a = al.get(i, {"target_idx": None, "confidence": "none"})
        q = target.paras[a["target_idx"]] if a["target_idx"] is not None else None
        if a["confidence"] != "key":
            problems.append(f"{p.key}: confidenza {a['confidence']}")
        L.append(f"| {i} | {p.key} | {a['confidence']} | {p.text[:60]!r} | {(q.text[:60] if q else '—')!r} |")
    return "\n".join(L) + "\n", problems


def save(al: dict, path: Path):
    path.write_text(json.dumps({str(k): v for k, v in al.items()}, indent=1))


def load(path: Path) -> dict[int, dict]:
    return {int(k): v for k, v in json.loads(path.read_text()).items()}
