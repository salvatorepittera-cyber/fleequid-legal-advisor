"""Riporta sull'IT v9 pulita le correzioni dello studio del 9/10/2026 (redline «DEF_DEF») e aggiorna units.json / it_new.txt.

Uso (dalla radice del repo):  PYTHONPATH=. python3 work/general-t-c/v9/defdef_apply_it.py
Interventi nostri rispetto al redline (concordati con Salvatore: refusi, non da sottoporre allo studio):
- art. 7.1: spazio dopo la virgola («privacy-policy, in conformità») e «GDPR - Regolamento»; l'URL resta un link;
- art. 18.5: virgole («emerga, o sia denunciata dall'Acquirente, successivamente…»);
- elenco finale (24.7), voce art. 13: «Pagamento anticipato» maiuscolo come nel nuovo titolo dell'art. 13;
- link al Tariffario: restano su /it/ (nel file dello studio puntano a /en/).
"""
import json
import re
from pathlib import Path

from tcupdate.docx_model import Docx, replace_across_runs, set_paragraph_markup
from tcupdate.rebuild import _set_markup, norm, redline_pairs

V9 = Path("T&C/General T&C/Vers 9 - Multilanguage - Q4 2026")
IT = V9 / "9_Termini_e_Condizioni_Generali_Fleequid_F0009_2026_IT.docx"
RED = V9 / "9_Versione_Termini_e_Condizioni_Generali_Fleequid_Versione_nr_F0009_2026_DEF_DEF_Redline.docx"
WORK = Path("work/general-t-c/v9")

CAL = ("(trenta) giorni", "(trenta) giorni di calendario")
REPL = {  # idx del paragrafo nell'IT pulita → [(vecchio, nuovo)]
    53: [("per la commercializzazione di Veicoli, secondo", "per la compravendita di Veicoli, secondo")],
    89: [("rispetto a Fleequid nella Vendita", "rispetto a Fleequid; nella Vendita")],
    90: [("Ogni riferimento contenuto", "Salvo che la singola disposizione preveda espressamente un termine in giorni di calendario, ogni riferimento contenuto")],
    101: [(" e 17.1 ed è preventivamente resa conoscibile e accettata ai sensi", " e 17.1, è preventivamente resa conoscibile ai sensi"),
          ("3.2, lett. a).", "3.2, lett. a) e accettata mediante l’adesione alle presenti CG.")],
    124: [("almeno 30 (trenta) giorni rispetto", "almeno 30 (trenta) giorni di calendario rispetto"),
          ("entro 30 (trenta) giorni dalla comunicazione", "entro 30 (trenta) giorni di calendario dalla comunicazione")],
    144: [("dell'operatività dell'account disposta", "dell'operatività del profilo disposta")],
    147: [("ogni controversia relativa all'applicazione di quanto disciplinato dal presente articolo è devoluta a un tentativo",
           "le controversie relative all’accesso al Marketplace, al suo utilizzo e alle misure di limitazione, sospensione o cessazione dell’accesso o dell’operatività dell’Utente adottate da Fleequid ai sensi del presente articolo sono devolute a un tentativo"),
          ("Resta ferma la disciplina", "Resta ferma e autonoma la disciplina"),
          ("di cui all'art. 20.", "di cui all'art. 20, alla quale non si applica il tentativo di mediazione di cui al presente comma salvo che la controversia riguardi anche, autonomamente, una delle materie indicate nel periodo precedente.")],
    154: [("importo, che prevale in ogni caso", "importo; l’obbligo e l’importo concretamente resi conoscibili all’Offerente ai sensi dell’art. 6.1 prevalgono in ogni caso")],
    176: [("eseguita mediante Rivendita, il Venditore è tenuto a corrispondere una penale", "eseguita mediante Rivendita, il Venditore è tenuto a corrispondere alla stessa una penale"),
          ("del Dealer Sales, il Venditore è tenuto a corrispondere una penale", "del Dealer Sales, il Venditore è tenuto a corrispondere alla stessa una penale")],
    178: [("Gravami sul Veicolo non espressamente", "Gravami sul Veicolo diversi da quelli espressamente")],
    217: [("3 (tre) giorni lavorativi decorrenti", "3 (tre) giorni decorrenti")],
    228: [("12.9, ultimo periodo.", "12.9.")],
    232: [("non essendo dovute Commissioni dall'Acquirente secondo la Vendita", "non essendo dovute dall’Acquirente le Commissioni previste per la Vendita")],
    16: [("Vendita differita: pagamento anticipato", "Vendita differita: Pagamento anticipato")],
    236: [("Vendita differita: pagamento anticipato", "Vendita differita: Pagamento anticipato")],
    400: [("(Vendita differita: pagamento anticipato", "(Vendita differita: Pagamento anticipato")],
    237: [("unitamente alle condizioni particolari applicabili", "unitamente alle Condizioni particolari di vendita applicabili")],
    241: [("penale di € 150,00 per ciascun", "penale di € 150,00 (euro centocinquanta/00) per ciascun")],
    248: [("dalle Condizioni Specifiche o dalle", "dalle Condizioni Specifiche applicabili o dalle")],
    263: [("in particolare le Commissioni", "in particolare, le Commissioni")],
    264: [("per fatto imputabile, il Venditore", "per fatto a lui imputabile, il Venditore")],
    271: [("di cui alla lett. b), questi", "di cui al punto (ii), questi")],
    284: [("resa conoscibile e accettata prima della", "resa conoscibile prima della"),
          ("3.2, lett. a). Fleequid può", "3.2, lett. a), ed è accettata mediante l’adesione alle presenti CG. Fleequid può")],
    289: [("accettazione di offerte inferiori", "accettazione di Offerte inferiori")],
    290: [("In caso di ritardo imputabile al Venditore nell'emissione", "In caso di ritardo nell'emissione")],
    293: [("prevista dall'art. 8.11, restando ferme la facoltà", "prevista dall'art. 8.11, lett. a), restando ferme la facoltà")],
    298: [("trasmissione della fattura il Venditore", "trasmissione della fattura, il Venditore")],
    307: [("In caso di ritardo imputabile al Venditore nell'emissione", "In caso di ritardo nell'emissione")],
    308: [("un vizio, un danno o altra circostanza imputabile al Venditore emerga o sia denunciata dall'Acquirente successivamente",
           "un vizio, un danneggiamento del Veicolo o altra circostanza imputabile al Venditore emerga, o sia denunciata dall'Acquirente, successivamente")],
    317: [("ad avvalersi, ove resa disponibile da Fleequid o dal Venditore, della possibilità", "ad avvalersi della possibilità"),
          ("avvalendosi dell'eventuale possibilità", "avvalendosi della possibilità")],
    335: [("entro 30 (trenta) giorni dalla consegna", "entro 30 (trenta) giorni di calendario dalla consegna")],
    341: [("entro 30 (trenta) giorni dalla data", "entro 30 (trenta) giorni di calendario dalla data")],
    361: [("requisiti ivi previsti, effetto", "requisiti previsti dalle medesime Condizioni Specifiche, effetto")],
    378: [("(CO),", "(CO)")],
}
# paragrafi riscritti per intero (collegamento ipertestuale / grassetto della rubrica)
MARKUP = {
    161: [("Informativa Privacy in conformità", "Informativa Privacy, raggiungibile al seguente indirizzo: https://fleequid.com/it/privacy-policy, in conformità"),
          ("GDPR -Regolamento (UE) 2016/679 raggiungibile al seguente indirizzo: https://fleequid.com/it/privacy-policy.", "GDPR - Regolamento (UE) 2016/679.")],
    334: [("Vendita in commissione con operatività di Fleequid quale Intermediario puro. ", "<b>Vendita in commissione con operatività di Fleequid quale Intermediario puro</b>. ")],
}
# scostamenti voluti dal testo accettato del redline (vedi docstring)
OURS = [("privacy-policy,in conformità", "privacy-policy, in conformità"), ("GDPR-Regolamento", "GDPR - Regolamento"),
        ("emerga, o sia denunciata, dall'Acquirente successivamente", "emerga, o sia denunciata dall'Acquirente, successivamente")]


def actual(text: str, old: str) -> str:
    pat = re.escape(old).replace("'", "['’]").replace(r"\ ", r"\s+")
    m = re.findall(pat, text)
    if len(m) != 1:
        raise SystemExit(f"«{old}»: {len(m)} occorrenze (attesa 1)")
    return m[0]


def main():
    d = Docx(IT)
    before = {p.idx: p.text for p in d.paras}
    for idx, reps in REPL.items():
        p = d.paras[idx]
        for old, new in reps:
            txt = "".join(t.text or "" for t in p.el.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"))
            if not replace_across_runs(p.el, actual(txt, old), new):
                raise SystemExit(f"[{p.key}] sostituzione fallita: {old}")
    for idx, reps in MARKUP.items():
        p = d.paras[idx]
        m = p.markup
        for old, new in reps:
            if m.count(old) != 1:
                raise SystemExit(f"[{p.key}] «{old}»: {m.count(old)} occorrenze nel markup")
            m = m.replace(old, new)
        (_set_markup if idx == 161 else set_paragraph_markup)(p.el, m)
    d.mark_dirty("word/document.xml")
    d.save(IT)

    d = Docx(IT)
    touched = sorted(set(REPL) | set(MARKUP))
    changed = [p.idx for p in d.paras if p.text != before[p.idx]]
    extra = set(changed) - set(touched) | set(touched) - set(changed) - {334}
    if extra:
        raise SystemExit(f"paragrafi cambiati inattesi o non cambiati: {sorted(extra)}")
    # confronto con il testo accettato del redline
    ne = [p for p in d.paras if not p.empty]
    pairs = redline_pairs(RED)
    assert len(ne) == len(pairs)
    bad = 0
    for p, (r, a) in zip(ne, pairs):
        if r == a:
            continue
        exp = a
        for x, y in OURS:
            exp = re.sub(re.escape(x).replace("'", "['’]"), y, exp)
        got = norm(p.text)
        if got.replace("’", "'") != exp.replace("’", "'"):
            bad += 1
            print(f"DIVERSO [{p.key}]\n  atteso: {exp}\n  avuto:  {got}")
        elif got != exp:
            print(f"solo apostrofi diversi [{p.key}]")
    if bad:
        raise SystemExit(f"{bad} paragrafi diversi dal redline accettato")
    # tracciabilità
    units = json.loads((WORK / "units.json").read_text())
    upd = []
    for u in units:
        p = d.paras[u["idx"]]
        if u["key"] != "TOC" and u["markup"] != p.markup:
            u["markup"], u["words"] = p.markup, len(p.text.split())
            upd.append(u["id"])
    (WORK / "units.json").write_text(json.dumps(units, ensure_ascii=False, indent=1))
    (WORK / "it_new.txt").write_text("\n".join(f"[{p.key}] {p.text}" for p in d.paras if not p.empty))
    (WORK / "defdef_units.json").write_text(json.dumps(upd))
    print(f"IT aggiornata: {len(changed)} paragrafi; unità toccate: {len(upd)} → {' '.join(upd)}")


if __name__ == "__main__":
    main()
