"""Genera il Word con le osservazioni sull'IT v2 delle Condizioni Particolari «1 Euro Auctions» per lo studio legale.

Uso (dalla radice del repo):  python3 work/1-euro-auctions/v2/osservazioni_studio.py
Impaginazione e tabelle sono quelle del generatore delle T&C Generali v9 (`work/general-t-c/v9/osservazioni_studio.py`),
riusato così com'è: qui cambiano solo titolo, testo e destinazione. Le osservazioni vengono dalla traduzione nelle
10 lingue e sono state verificate sul Word italiano v2 e sul testo delle CG v9 (`work/general-t-c/v9/it_new.txt`).
"""
import importlib.util
from pathlib import Path

VERSION = "Vers_2_2026"
OUT = Path("T&C/1 Euro Auctions/Vers 2 - Multilanguage - Q4 2026/"
           f"Osservazioni_per_lo_Studio_sulla_bozza_IT_1EuroAuction_{VERSION}.docx")

TITLE = f"Condizioni Particolari di vendita «1 Euro Auctions» – versione {VERSION}"
SUBTITLE = "Osservazioni sul testo italiano emerse durante la traduzione"
INTRO = [
    f"Nel tradurre la versione {VERSION} nelle dieci lingue del Marketplace abbiamo riletto il testo italiano "
    "paragrafo per paragrafo, confrontandolo con la versione precedente e con le Condizioni Generali F0009_2026 (CG v9) "
    "a cui il documento è stato allineato. Questo documento raccoglie i punti in cui il testo ci è parso non ancora "
    "allineato, incoerente o ambiguo. Per ciascun punto indichiamo l'articolo, il passaggio, l'osservazione e una proposta.",
    "Le traduzioni seguono alla lettera il testo italiano attuale: nei paragrafi della sezione A resta quindi, in tutte "
    "le lingue, la terminologia della versione precedente. Ogni correzione che lo Studio vorrà apportare andrà riportata "
    "nelle versioni in lingua.",
    "La sezione D elenca i tre refusi che abbiamo già corretto nel Word italiano definitivo: sono riportati solo per "
    "conferma.",
]

# (articolo, testo v2, osservazione, proposta)
SECTIONS = [
    ("A. Paragrafi non aggiornati alle CG v9", "Proposta", [
        ("Premessa, penultimo capoverso",
         "«…restano integralmente applicabili le CG, le eventuali Condizioni specifiche e il Tariffario Fleequid, in quanto "
         "compatibili con la natura delle “1 Euro Auctions”, secondo la gerarchia stabilita dall’art. 3.3 delle CG.»",
         "Il capoverso non è stato modificato. Nelle CG v9 la gerarchia delle fonti è all'art. 4.3 (l'art. 3.3 riguarda "
         "altro) e «Condizioni Specifiche» è termine definito con la maiuscola. L'art. 6.4 dello stesso documento, che "
         "ripete la regola, è stato invece aggiornato («Condizioni Specifiche», «art. 4.3 delle CG»).",
         "«…le eventuali Condizioni Specifiche e il Tariffario Fleequid, …, secondo la gerarchia stabilita dall’art. 4.3 delle CG.»"),
        ("5.2",
         "«L’Acquirente aggiudicatario è tenuto al pagamento del Prezzo di aggiudicazione e delle Commissioni dovute nei "
         "termini e con le modalità previste dalle CG, nonché dal Tariffario applicabile alla specifica 1 Euro Auction.»",
         "Il comma non è stato modificato. «Acquirente aggiudicatario» e «Prezzo di aggiudicazione» sono stati sostituiti "
         "in tutto il resto del documento (artt. 2.3, 4.4: «Acquirente», «Prezzo di vendita all’Acquirente»; art. 5.1: "
         "«Importo Totale Dovuto»). Nelle CG v9 «Prezzo di aggiudicazione» non è più un termine definito.",
         "«L’Acquirente è tenuto al pagamento dell’Importo Totale Dovuto nei termini e con le modalità previste dalle CG, "
         "nonché dal Tariffario applicabile alla specifica 1 Euro Auction.» (o altra formulazione con «Prezzo di vendita "
         "all’Acquirente»)."),
        ("3.5",
         "«La corresponsione dell’eventuale integrazione economica fino al PMIV è subordinata alla regolare conclusione "
         "del Contratto e all’integrale e definitivo adempimento degli obblighi di pagamento da parte dell’Acquirente…»",
         "Il comma non è stato modificato. La rubrica dell'art. 2 e gli artt. 2.1, 2.3, 2.4, 3.4, 6.2 parlano ora solo di "
         "perfezionamento dell'Accordo vincolante; qui resta «conclusione del Contratto».",
         "Valutare «al regolare perfezionamento dell’Accordo vincolante», oppure confermare che qui si intende il Contratto."),
        ("5.4",
         "«…ivi inclusa la regolare conclusione del Contratto e l’effettivo incasso delle somme dovute dall’Acquirente…»",
         "Come al punto precedente.",
         "Uniformare alla scelta fatta per l'art. 3.5."),
        ("4 (rubrica), 4.1, 4.2",
         "Rubrica: «Struttura commissionale.»; 4.1: «…si applica, in via generale, la struttura commissionale ordinaria "
         "prevista dal Tariffario Fleequid…»; 4.2: «…una diversa struttura commissionale…».",
         "All'art. 1.1 «una struttura commissionale distinta» è stata sostituita con «specifiche condizioni economiche»; "
         "nell'art. 4 l'espressione è rimasta.",
         "Solo conferma: probabilmente voluto, perché l'art. 4 riguarda proprio le Commissioni."),
    ]),
    ("B. Rinvii alle CG v9 da verificare", "Proposta", [
        ("Premessa, secondo capoverso",
         "«Esse sono adottate ai sensi e per gli effetti degli artt. 4.3, 4.4 e 9.4, lett. d), delle Condizioni Generali "
         "del Marketplace Fleequid (“CG”)…»",
         "L'art. 9.4, lett. d) delle CG v9 stabilisce che le Condizioni particolari di vendita delle 1 Euro Auctions "
         "«trovano applicazione secondo quanto previsto dall’art. 4.5» (modalità con cui sono rese conoscibili e "
         "applicabili). L'art. 4.5 non è tra gli articoli richiamati.",
         "Valutare «degli artt. 4.3, 4.4, 4.5 e 9.4, lett. d)»."),
        ("3.6, ultimo periodo",
         "«In caso di Annullamento della vendita e di successiva vendita del Veicolo ad altro Offerente ai sensi dell’art. "
         "10.5 delle CG, la garanzia opera… esclusivamente con riferimento alla nuova vendita.»",
         "Il rinvio è corretto (l'art. 10.5 delle CG v9 disciplina la permanenza delle altre Offerte). Lo segnaliamo solo "
         "perché è l'unico rinvio nuovo a un comma specifico delle CG oltre a quelli agli artt. 12.4 e 6.3, anch'essi verificati.",
         "Nessuna azione: solo per informazione."),
    ]),
    ("C. Passaggi da confermare", "Proposta", [
        ("3 (rubrica), 4.2–4.6",
         "3.1: «Nell’ambito delle 1 Euro Auctions eseguite secondo il Modello di Vendita in commissione…»; 4.1: «Alle 1 "
         "Euro Auctions eseguite secondo il Modello di Vendita in commissione si applica…».",
         "La limitazione alla Vendita in commissione è stata introdotta negli artt. 1.3, 3.1 e 4.1, ma non nella rubrica "
         "dell'art. 3 né nei commi 4.2–4.6 (struttura commissionale diversa, Commissioni dell'Acquirente, maturazione). "
         "Per le 1 Euro Auctions in Dealer Sales l'ambito di questi commi resta implicito.",
         "Confermare che gli artt. 4.2–4.6 valgono anche in Dealer Sales, oppure precisare l'ambito."),
        ("3.1 / 3.2, ultimo periodo",
         "3.1: incasso netto «pari al Prezzo di vendita all’Acquirente al netto delle sole Commissioni a carico del "
         "Venditore»; 3.2: «La garanzia non copre le Tariffe, le penali, i rimborsi spese né gli altri importi eventualmente "
         "dovuti dal Venditore a Fleequid, che… possono essere detratti o compensati secondo la disciplina generale.»",
         "Le due regole sono compatibili (la garanzia si calcola al netto delle sole Commissioni; gli altri importi si "
         "detraggono dopo), ma il Venditore può leggere «sole Commissioni» come limite a ogni altra detrazione.",
         "Solo conferma. Se utile: «…possono essere detratti o compensati, anche dall’importo garantito, secondo la disciplina generale»."),
        ("1.1",
         "«…caratterizzata da specifiche modalità di determinazione del prezzo e da specifiche condizioni economiche "
         "rispetto alle Aste ordinarie disciplinate dalle Condizioni Generali (“CG”).»",
         "Nella versione precedente «rispetto alle Aste ordinarie» dipendeva da «distinta» («struttura commissionale "
         "distinta rispetto a»). Tolto «distinta», «rispetto alle Aste ordinarie» resta senza reggenza.",
         "«…e da condizioni economiche specifiche, distinte rispetto a quelle delle Aste ordinarie…»."),
        ("6.2",
         "«…la garanzia economica di cui all’art. 3 non maturerà né sarà dovuta, ferma la responsabilità di Fleequid per "
         "dolo o colpa grave e quanto previsto dalle Condizioni Generali in materia di responsabilità di Fleequid.»",
         "La responsabilità di Fleequid è richiamata due volte nella stessa frase (per dolo o colpa grave e secondo le CG).",
         "Solo conferma. Se utile: «…ferma la responsabilità di Fleequid per dolo o colpa grave, secondo quanto previsto dalle Condizioni Generali»."),
        ("Premessa, primo e secondo capoverso",
         "Primo capoverso: «Le presenti Condizioni Particolari d’Asta disciplinano…»; secondo capoverso: «…costituiscono "
         "Condizioni particolari di vendita ai sensi delle CG (di seguito anche “Condizioni Particolari d’Asta”)…».",
         "La denominazione abbreviata «Condizioni Particolari d’Asta» è usata nel primo capoverso, prima di essere "
         "introdotta nel secondo. Il titolo del documento è ora «Condizioni Particolari di vendita».",
         "Aprire il primo capoverso con «Le presenti Condizioni Particolari di vendita…» (facoltativo)."),
        ("4.4",
         "«All’Acquirente sono applicate le Commissioni previste ai sensi dei commi che precedono, ivi inclusa, ove "
         "prevista, la commissione fissa (“flat buyer fee”) e/o la commissione percentuale…»",
         "«Commissioni» è ora maiuscolo (termine definito); «commissione fissa» e «commissione percentuale» restano minuscoli.",
         "Solo conferma (facoltativo uniformare)."),
        ("Sezione finale, lett. (a)",
         "«art. 3.8, primo periodo (inapplicabilità della garanzia in caso di sospensione, annullamento o dichiarazione di "
         "non validità dell’Asta…); art. 6.1 (facoltà di Fleequid di sospendere, prorogare, annullare o dichiarare non valida…)».",
         "La sintesi dell'art. 3.8 non cita la proroga, quella dell'art. 6.1 sì. È coerente con i due articoli (il 3.8 "
         "non prevede la proroga).",
         "Nessuna azione: solo per informazione."),
    ]),
    ("D. Refusi già corretti nel Word italiano definitivo", "Correzione applicata", [
        ("Premessa, secondo capoverso",
         "«…ai sensi delle CG (si seguito anche “Condizioni Particolari d’Asta”)…»",
         "Refuso.",
         "«(di seguito anche …)»."),
        ("2.4",
         "«…non si perfezionerà alcun Accordo Vincolante ai sensi delle CG…»",
         "Il termine definito è «Accordo vincolante» (così nelle CG v9 e negli altri commi).",
         "«alcun Accordo vincolante»."),
        ("3.2",
         "«l’incasso netto di cui all’art. 3.1 risultante al termine della 1 Euro Auction sia inferiore al PMIV, Fleequid "
         "si impegna a corrispondere al Venditore la differenza…»",
         "È caduto il «Qualora» iniziale, presente nella versione precedente («Qualora il Prezzo di aggiudicazione…»): "
         "la frase comincia con la minuscola e il congiuntivo resta senza reggenza.",
         "«Qualora l’incasso netto di cui all’art. 3.1 risultante al termine della 1 Euro Auction sia inferiore al PMIV, …»."),
    ]),
]


def main():
    spec = importlib.util.spec_from_file_location("osservazioni_v9", "work/general-t-c/v9/osservazioni_studio.py")
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    base.OUT, base.TITLE, base.SUBTITLE, base.INTRO, base.SECTIONS = OUT, TITLE, SUBTITLE, INTRO, SECTIONS
    base_table = base.table
    # l'intestazione della terza colonna nel generatore v9 cita la versione delle Generali
    base.table = lambda header, rows, widths: base_table(
        tuple(h.replace("F0009_2026", VERSION) for h in header), rows, widths)
    base.build()


if __name__ == "__main__":
    main()
