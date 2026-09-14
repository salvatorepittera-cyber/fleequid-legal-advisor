"""Pacchetto di lavoro per il traduttore di una lingua + glossario ricavato dalle versioni pubblicate."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .docx_model import Docx, strip_markup

ROOT = Path(__file__).resolve().parent.parent
GLOSSARY_DIR = ROOT / "glossary"

TRANSLATABLE = {"modify", "insert", "format", "whitespace"}


def definitions(doc: Docx, al: dict | None = None) -> dict[int, list[str]]:
    """Termini definiti: segmenti formattati (b/i) prima dei due punti nei paragrafi dell'art. 1."""
    out = {}
    for p in doc.paras:
        if p.in_toc or p.article != "1" or not p.segs or not p.segs[0][0]:
            continue
        terms, pos = [], 0
        head = p.text.split(":", 1)[0] if ":" in p.text[:120] else None
        if head is None:
            continue
        for f, t in p.segs:
            if pos >= len(head):
                break
            if f and t.strip():
                terms.append(t.strip().strip("“”\"«»„:").strip())
            pos += len(t)
        if terms:
            out[p.idx] = terms
    return out


def build_glossary(it_prev: Docx, target: Docx, al: dict, lang: str, source: str) -> list[dict]:
    it_defs = definitions(it_prev)
    tg_defs = definitions(target)
    pairs = []
    for i, terms in it_defs.items():
        a = al.get(i)
        if a and a["target_idx"] in tg_defs:
            tr = tg_defs[a["target_idx"]]
            if len(tr) == len(terms):
                pairs += [{"it": x, "tr": y, "source": source} for x, y in zip(terms, tr)]
            else:
                pairs.append({"it": " / ".join(terms), "tr": " / ".join(tr), "source": source})
    # memoria cumulativa per lingua
    GLOSSARY_DIR.mkdir(exist_ok=True)
    gpath = GLOSSARY_DIR / f"{lang}.json"
    cur = json.loads(gpath.read_text()) if gpath.exists() else []
    seen = {(g["it"], g["tr"]) for g in cur}
    for p in pairs:
        p["it"], p["tr"] = p["it"].strip(" /"), p["tr"].strip(" /")
        if not p["it"] or not p["tr"]:
            continue
        if (p["it"], p["tr"]) not in seen:
            cur.append(p)
            seen.add((p["it"], p["tr"]))
    gpath.write_text(json.dumps(cur, ensure_ascii=False, indent=1))
    return cur


def article_block(doc: Docx, article: str) -> str:
    lines = []
    for p in doc.paras:
        if not p.in_toc and p.article == article and not p.empty:
            lines.append(f"[{p.key}] {p.markup}")
    return "\n".join(lines)


RULES = """## Regole (vincolanti)
1. Traduci l'INTERO paragrafo indicato in linguaggio tecnico-legale-commerciale della lingua di arrivo, coerente
   con il resto del documento {lang} (stesso registro, stesse formule).
2. Dove il testo IT non è cambiato, RIPRENDI ALLA LETTERA la resa della versione precedente {lang}.
   Cambia solo ciò che il diff IT richiede (aggiunte, rimozioni, sostituzioni).
3. Terminologia: usa SEMPRE i termini già usati nella versione precedente {lang} e nel glossario. Mai sinonimi.
   Per un concetto nuovo cerca prima nelle T&C Generali {lang} (file di riferimento sotto); se lo trovi usa quella
   resa, altrimenti scegli la resa legale standard e segnalala in "new_terms".
4. Formattazione: riporta <b>, <i>, <u> sulle parole corrispondenti, con lo stesso numero di segmenti dell'IT nuova.
   Non aggiungere né togliere formattazioni. Nessun altro tag.
5. Numeri, importi, rinvii ad articoli, nomi propri, e-mail: invariati nel valore, scritti con la convenzione tipografica
   già usata nella versione precedente {lang} (es. separatore migliaia).
6. Se la modifica IT è solo la correzione di un refuso italiano (es. concordanza) e la resa {lang} precedente è già
   corretta, restituisci il testo precedente identico.
7. Le rimozioni nel diff IT ([-...-]) vanno recepite: il concetto rimosso non deve restare nella traduzione.
"""


def build(changes: dict, it_prev: Docx, it_new: Docx, target: Docx, al: dict, lang: str,
          glossary: list[dict], general_ref: Path | None, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    L = [f"# Brief traduzione {lang}\n",
         f"Documento base {lang} (versione precedente): `{target.path.name}`",
         f"Versione IT nuova: `{it_new.path.name}`\n",
         RULES.format(lang=lang)]
    if general_ref:
        L.append(f"Riferimento T&C Generali {lang} (testo): `{general_ref}`\n")
    L.append("## Glossario (IT → " + lang + ")\n")
    for g in glossary:
        L.append(f"- {strip_markup(g['it'])} → {strip_markup(g['tr'])}")
    L.append("\n## Paragrafi da tradurre\n")
    todo = []
    arts = []
    for c in changes["changes"]:
        if c["toc"] or c["kind"] not in TRANSLATABLE:
            continue
        pn = it_new.paras[c["new_idx"]]
        if pn.empty:
            continue
        tgt_prev = None
        if c["prev_idx"] is not None:
            a = al.get(c["prev_idx"], {})
            if a.get("target_idx") is not None:
                tgt_prev = target.paras[a["target_idx"]].markup
        todo.append(c["id"])
        if pn.article not in arts:
            arts.append(pn.article)
        L.append(f"### {c['id']} — [{pn.key}] ({c['kind']})\n")
        L.append(f"**IT precedente:**\n\n{c['prev_markup'] or '(nuovo paragrafo)'}\n")
        L.append(f"**IT nuova:**\n\n{pn.markup}\n")
        L.append(f"**Diff IT (parole):**\n\n{c['word_diff']}\n")
        L.append(f"**{lang} precedente:**\n\n{tgt_prev or '(nessuno: paragrafo nuovo)'}\n")
    L.append("\n## Contesto: articoli interessati\n")
    for art in arts:
        L.append(f"### Articolo {art} — IT nuova\n\n{article_block(it_new, art)}\n")
        L.append(f"### Articolo {art} — {lang} precedente\n\n{article_block(target, art)}\n")
    L.append("\n## Output richiesto\n")
    L.append("Scrivi un file JSON con questa forma esatta (UTF-8):\n")
    L.append("```json\n" + json.dumps({
        "lang": lang,
        "translations": {cid: "<testo completo del paragrafo con eventuali <b>/<i>/<u>>" for cid in todo},
        "new_terms": [{"it": "...", "tr": "...", "why": "..."}],
        "notes": ["..."],
    }, ensure_ascii=False, indent=1) + "\n```\n")
    path = out_dir / f"{lang}.md"
    path.write_text("\n".join(L))
    return path


def general_text_dump(general_doc: Path, out: Path) -> Path:
    d = Docx(general_doc)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(f"[{p.key}] {p.text}" for p in d.paras if not p.empty))
    return out
