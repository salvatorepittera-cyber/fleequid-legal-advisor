"""Applica le traduzioni al Word della versione precedente di una lingua (intervento chirurgico)."""
from __future__ import annotations

import copy

from .docx_model import Docx, canonical, replace_across_runs, set_paragraph_markup, wtag

TEXT_KINDS = {"modify", "format", "whitespace"}


def _ppr_model(it_prev: Docx, it_new: Docx, new_idx: int, al: dict, target: Docx):
    """Paragrafo della lingua da usare come modello per un paragrafo inserito.

    Cerca in IT prev un paragrafo con pPr identico a quello inserito in IT nuova e ne prende il corrispondente
    nella lingua (stesso stile/numerazione della lingua, non quelli dell'IT).
    """
    want = it_new.paras[new_idx]
    want_ppr = want.ppr_xml()
    cands = [p for p in it_prev.paras if not p.in_toc and p.ppr_xml() == want_ppr and p.empty == want.empty]
    # preferisci il più vicino per posizione
    cands.sort(key=lambda p: abs(p.idx - new_idx))
    for p in cands:
        a = al.get(p.idx)
        if a and a.get("target_idx") is not None:
            return target.paras[a["target_idx"]]
    return None


def run(changes: dict, it_prev: Docx, it_new: Docx, target: Docx, al: dict,
        translations: dict[str, str], out_path, strict: bool = True) -> list[str]:
    log = []
    low = []
    inserted_after: dict[int, object] = {}
    tparas = list(target.paras)  # snapshot: gli indici restano quelli della versione precedente
    for c in changes["changes"]:
        if c["toc"]:
            continue
        kind = c["kind"]
        if kind in TEXT_KINDS or kind == "delete":
            a = al.get(c["prev_idx"])
            if not a or a["target_idx"] is None:
                raise SystemExit(f"{c['id']} [{c['prev_key']}]: paragrafo non allineato nella lingua")
            if a["confidence"] != "key":
                low.append(f"{c['id']} [{c['prev_key']}] confidenza {a['confidence']}")
            tp = tparas[a["target_idx"]]
            if kind == "delete":
                tp.el.getparent().remove(tp.el)
                log.append(f"{c['id']} [{c['prev_key']}] eliminato")
                continue
            if it_new.paras[c["new_idx"]].empty:
                continue
            text = translations.get(c["id"])
            if text is None:
                raise SystemExit(f"{c['id']} [{c['new_key']}]: traduzione mancante")
            if text == tp.markup:
                log.append(f"{c['id']} [{c['new_key']}] invariato (resa precedente già corretta)")
                continue
            set_paragraph_markup(tp.el, text)
            log.append(f"{c['id']} [{c['new_key']}] aggiornato")
        elif kind == "insert":
            anchor = c.get("anchor_prev_idx")
            a = al.get(anchor) if anchor is not None else None
            if not a or a["target_idx"] is None:
                raise SystemExit(f"{c['id']}: ancora dell'inserimento non allineata")
            anchor_el = inserted_after.get(anchor, tparas[a["target_idx"]].el)
            model = _ppr_model(it_prev, it_new, c["new_idx"], al, target)
            new_is_empty = it_new.paras[c["new_idx"]].empty
            if model is not None and model.empty and new_is_empty:
                new_el = copy.deepcopy(model.el)
            else:
                src = model.el if model is not None else tparas[a["target_idx"]].el
                new_el = copy.deepcopy(src)
                for ch in list(new_el):
                    if ch.tag != wtag("pPr"):
                        new_el.remove(ch)
                if not new_is_empty:
                    text = translations.get(c["id"])
                    if text is None:
                        raise SystemExit(f"{c['id']} [{c['new_key']}]: traduzione mancante")
                    # base rPr: dal modello se ha testo
                    tmp = copy.deepcopy(src)
                    set_paragraph_markup(tmp, text)
                    for ch in list(tmp):
                        if ch.tag != wtag("pPr") and ch.tag not in (wtag("bookmarkStart"), wtag("bookmarkEnd")):
                            new_el.append(ch)
            anchor_el.addnext(new_el)
            inserted_after[anchor] = new_el
            log.append(f"{c['id']} [{c['new_key']}] inserito" + (" (vuoto)" if new_is_empty else ""))
    # intestazioni: codice versione
    vp, vn = changes.get("version_prev") or [], changes.get("version_new") or []
    if len(vp) == 1 and len(vn) == 1 and vp != vn:
        hit = False
        for name, h in target.headers.items():
            for p in h.iter(wtag("p")):
                while replace_across_runs(p, vp[0], vn[0]):
                    hit = True
                    target.mark_dirty(name)
        log.append(f"header {vp[0]} → {vn[0]}" + ("" if hit else "  ⚠️ codice precedente NON trovato nell'header"))
        if not hit and strict:
            raise SystemExit(f"Header: codice {vp[0]} non trovato in {target.path.name}")
    if low:
        msg = "Abbinamenti non a chiave: " + "; ".join(low)
        if strict:
            raise SystemExit(msg + " (conferma l'allineamento o usa --no-strict)")
        log.append("⚠️ " + msg)
    target.mark_dirty("word/document.xml")
    target.save(out_path)
    return log
