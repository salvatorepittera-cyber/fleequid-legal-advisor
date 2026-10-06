"""Genera il Word con le osservazioni sull'IT v9 delle T&C Generali da inviare allo studio legale.

Uso (dalla radice del repo):  python3 work/general-t-c/v9/osservazioni_studio.py
Le osservazioni sono state raccolte durante la traduzione nelle 10 lingue e verificate sul testo
di `work/general-t-c/v9/it_new.txt` (IT v9 pulita).
"""
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path("T&C/General T&C/Vers 9 - Multilanguage - Q4 2026/"
           "Osservazioni_per_lo_Studio_sulla_bozza_IT_F0009_2026.docx")

TITLE = "Termini e Condizioni Generali Fleequid – versione F0009_2026"
SUBTITLE = "Osservazioni sul testo italiano emerse durante la traduzione"
INTRO = [
    "Nel tradurre la versione F0009_2026 nelle dieci lingue del Marketplace abbiamo riletto il testo italiano "
    "articolo per articolo. Questo documento raccoglie i punti in cui il testo ci è parso incoerente, ambiguo o "
    "con refusi. Per ciascun punto indichiamo l'articolo, il passaggio, l'osservazione e, dove possibile, una proposta.",
    "Le traduzioni seguono alla lettera il testo italiano attuale: ogni correzione che lo Studio vorrà apportare "
    "andrà riportata nelle versioni in lingua. Nelle sezioni A–C la colonna «Come abbiamo tradotto» indica la "
    "lettura adottata, da confermare o correggere.",
    "I rinvii del tipo «lett. a)» ai sottoparagrafi di terzo livello (es. art. 3.2, lett. a) = 3.2.1) sono corretti, "
    "perché nel Word quei sottoparagrafi sono numerati con lettere: non sono segnalati.",
]

# (articolo, testo v9, osservazione, proposta / come abbiamo tradotto)
SECTIONS = [
    ("A. Rinvii interni da verificare", "Proposta", [
        ("16.4",
         "«In caso di ritardo imputabile all'Acquirente oltre il termine di cui alla lett. b), questi è tenuto a corrispondere a Fleequid una penale…»",
         "Gli obblighi dell'Acquirente nello stesso comma sono elencati come (i), (ii), (iii); la «lett. b)» presente nel comma appartiene all'elenco degli obblighi del Venditore. Il termine di 5 giorni dell'Acquirente è al punto (ii).",
         "Sostituire «lett. b)» con «punto (ii)»."),
        ("12.5",
         "«…ai fini della soglia minima di cui all'art. 12.9, ultimo periodo.»",
         "Nell'art. 12.9 la soglia del 5% non è nell'ultimo periodo: dopo di essa seguono il periodo «Ai fini del confronto e dell'integrazione…» e quello «La presente disposizione si applica a tutti i Modelli di Vendita…».",
         "Togliere «ultimo periodo» oppure indicare il periodo corretto."),
        ("17.8 / 17.14",
         "17.8: «trova applicazione la penale specifica prevista dall'art. 8.11»; 17.14: «…prevista dall'art. 8.11, lett. c)».",
         "I due commi sono paralleli (Rivendita / Intermediario puro), ma solo il 17.14 precisa la lettera dell'art. 8.11.",
         "Se voluto, precisare anche nel 17.8 «art. 8.11, lett. a)»."),
        ("10.4 / 10.5",
         "10.4: «il perfezionamento dell'Accordo vincolante secondo le modalità previste dai precedenti commi resta subordinato al relativo esito positivo».",
         "La verifica dei requisiti riguarda anche il perfezionamento disciplinato dal comma successivo (10.5), che infatti richiama «quanto previsto dall'art. 10.4 in materia di verifica dei requisiti».",
         "Valutare «secondo le modalità previste dal presente articolo»."),
        ("2.6, 17.1 / 3.2",
         "«…è preventivamente resa conoscibile e accettata ai sensi dell'art. 3.2, lett. a)».",
         "L'art. 3.2, lett. a) disciplina la conoscibilità della doppia modalità di esecuzione, non la sua accettazione.",
         "Valutare «resa conoscibile ai sensi dell'art. 3.2, lett. a) e accettata con la formulazione dell'Offerta», o altro rinvio per l'accettazione."),
        ("18.7 / 17.1",
         "18.7: «tale circostanza è resa conoscibile secondo quanto previsto dall'art. 3.2»; 17.1: «ai sensi dell'art. 3.2, lett. a)».",
         "Rinvio all'art. 3.2 con e senza lettera per la stessa funzione.",
         "Uniformare."),
        ("8.11 / 8.9",
         "«In caso di violazione, Fleequid ha diritto di applicare al Venditore la penale determinata secondo il criterio previsto dall'art. 8.9.»",
         "La penale per violazione del divieto di aggiramento rinvia a un criterio costruito sull'esclusiva dell'art. 8.9.",
         "Confermare che il rinvio è voluto."),
        ("5.5, lett. d)",
         "«nel Dealer Sales, in mancanza anche dei parametri di cui alle lett. a) e b), il Prezzo di acquisto».",
         "Per il Dealer Sales si rinvia solo alle lett. a) e b); la lett. c) riguarda la sola Vendita in commissione. Il rinvio sembra coerente.",
         "Solo conferma."),
    ]),
    ("B. Formulazioni non uniformi tra articoli", "Proposta", [
        ("1 (def. «Fleequid») / 2.9",
         "Definizione: entità «designate da Adorea S.r.l. per la commercializzazione di Veicoli, secondo quanto previsto dall'art. 2.9»; art. 2.9: «designate per la compravendita di Veicoli».",
         "La stessa categoria di entità è descritta con due attività diverse.",
         "Uniformare."),
        ("1 (premessa sui «giorni») / 11.5 / 12.7",
         "Art. 1: «Ogni riferimento… ai “giorni” è da intendersi riferito a giorni lavorativi». Art. 11.5: «3 (tre) giorni lavorativi». Art. 12.7: «Termine di pagamento ordinario di 3 (tre) giorni di cui all'art. 11.5».",
         "Solo l'art. 11.5 specifica «lavorativi»; altrove «giorni» è lavorativo per definizione. La specificazione isolata può far pensare che negli altri articoli i giorni siano di calendario.",
         "Togliere «lavorativi» dall'art. 11.5 o aggiungerlo all'art. 12.7."),
        ("4.2, 19.7 lett. c), 20.2",
         "Termini di «30 (trenta) giorni».",
         "Per effetto della definizione sono 30 giorni lavorativi, cioè circa sei settimane.",
         "Confermare che è voluto."),
        ("5.6 / 12.10",
         "5.6: «limitazione o sospensione dell'operatività dell'account»; 12.10 e resto dell'art. 5: «profilo».",
         "Due termini per lo stesso oggetto.",
         "Uniformare su «profilo» (o su «account»)."),
        ("13.1",
         "«…unitamente alle condizioni particolari applicabili all'operazione…»",
         "Minuscolo, mentre nel resto dell'articolo compare il termine definito «Condizioni particolari di vendita».",
         "Se si intende il termine definito, scriverlo per esteso con la maiuscola."),
        ("17.4",
         "«salva la diversa espressa accettazione di offerte inferiori ai sensi dell'art. 10.3».",
         "«offerte» minuscolo; «Offerta» è termine definito.",
         "Maiuscola, se si intende il termine definito."),
        ("13.5 / 15.7",
         "13.5: «penale di € 150,00 per ciascun giorno di ritardo»; 15.7 e altri: «€ 150,00 (euro centocinquanta/00)».",
         "All'art. 13.5 manca l'importo in lettere.",
         "Aggiungere «(euro centocinquanta/00)»."),
        ("17.11 / 17.5, 18.4",
         "17.11: «In caso di ritardo nell'emissione o nella trasmissione della fattura il Venditore è tenuto…»; 17.5 e 18.4: «In caso di ritardo imputabile al Venditore…».",
         "Nel 17.11 la penale non è limitata al ritardo imputabile al Venditore.",
         "Aggiungere «imputabile al Venditore», se la differenza non è voluta."),
        ("17.5 / 18.4",
         "17.5: fattura «in Euro e in conformità agli importi, ai dati e alle indicazioni comunicati da Fleequid»; 18.4: «secondo i dati e le indicazioni comunicati da Fleequid».",
         "Il requisito «in Euro» è previsto solo nella Vendita in commissione.",
         "Uniformare, se la differenza non è voluta."),
        ("8.11, lett. a)–c)",
         "a) e b): «a Fleequid, nell'ambito…, il Venditore è tenuto a corrispondere una penale…»; c): «direttamente all'Acquirente, …, il Venditore è tenuto a corrispondere a Fleequid una penale…».",
         "Nelle lett. a) e b) «a Fleequid» indica il destinatario del trasferimento e il beneficiario della penale resta implicito; nella lett. c) è espresso.",
         "Esplicitare «a Fleequid» come beneficiario anche in a) e b)."),
        ("19.3",
         "«…ad avvalersi, ove resa disponibile da Fleequid o dal Venditore, della possibilità di visionare, ispezionare e provare il Veicolo» e, poco oltre, «La mancata effettuazione dell'ispezione o della prova, da Fleequid sempre offerte…».",
         "Ispezione e prova sono prima eventuali, poi «sempre offerte».",
         "Scegliere una delle due formulazioni."),
        ("1 (definizioni)",
         "«Veicolo/i», «Acquirente/i», «Venditore/i».",
         "Solo queste definizioni conservano «/i»; le altre sono al singolare.",
         "Uniformare (facoltativo)."),
        ("24.7, voce art. 13",
         "«Art. 13 (Vendita differita: pagamento anticipato e Veicolo temporaneamente in uso…): 13.5 (… ritardo nel Pagamento anticipato…)».",
         "«pagamento anticipato» minuscolo nel titolo dell'art. 13, maiuscolo (termine definito) nel testo.",
         "Maiuscola anche nel titolo dell'art. 13."),
    ]),
    ("C. Passaggi ambigui", "Come abbiamo tradotto", [
        ("6.2, ultimo periodo",
         "«…fermo restando quanto previsto dall'art. 6.1 in ordine alla preventiva conoscibilità dell'obbligo di versamento e del relativo importo, che prevale in ogni caso sui valori ordinariamente applicati.»",
         "Non è chiaro a cosa si riferisca «che prevale»: all'importo reso conoscibile o a quanto previsto dall'art. 6.1.",
         "Riferito all'importo reso conoscibile."),
        ("8.13, lett. d)",
         "«Gravami sul Veicolo non espressamente dichiarati dal Venditore e accettati nell'ambito della specifica operazione».",
         "Si può leggere «non dichiarati, ma accettati» oppure «diversi da quelli dichiarati e accettati».",
         "Manleva per tutti i Gravami, esclusi solo quelli dichiarati dal Venditore e accettati. Suggeriamo: «Gravami sul Veicolo diversi da quelli espressamente dichiarati dal Venditore e accettati…»."),
        ("14.1",
         "«nei casi previsti dalle presenti Condizioni Generali, dalle Condizioni Specifiche o dalle Condizioni particolari di vendita applicabili».",
         "«applicabili» può riferirsi alle sole Condizioni particolari di vendita o anche alle Condizioni Specifiche.",
         "Riferito a entrambe."),
        ("15.7",
         "«Decorso inutilmente il termine applicabile per fatto imputabile, il Venditore o l'Acquirente inadempiente è tenuto a corrispondere…»",
         "«per fatto imputabile» è privo del soggetto.",
         "Imputabile al Venditore o all'Acquirente inadempiente. Suggeriamo «per fatto a lui imputabile»."),
        ("18.7",
         "«…alla sua consegna da parte del Venditore nelle condizioni convenute» e «non conformità tale da impedire l'esecuzione della vendita nelle condizioni convenute».",
         "«condizioni convenute» può indicare le condizioni pattuite oppure lo stato fisico del Veicolo.",
         "Condizioni pattuite."),
        ("18.5",
         "«Qualora una difformità, un vizio, un danno o altra circostanza imputabile al Venditore emerga…»",
         "«danno» può essere il danno al Veicolo o il pregiudizio in generale.",
         "Danno al Veicolo."),
        ("22.9",
         "«in espressa deroga all'art. 17.4 e limitatamente a quanto ivi previsto, le Condizioni Specifiche applicabili possono prevedere…»",
         "«ivi» può rinviare all'art. 17.4 o alle Condizioni Specifiche.",
         "In quasi tutte le lingue l'ambiguità è conservata; in russo è riferito all'art. 17.4."),
        ("22.6",
         "«un impegno irrevocabile del Finanziatore, avente i requisiti ivi previsti».",
         "«ivi» può rinviare all'art. 12.2 o alle Condizioni Specifiche; l'art. 12.2 non fissa requisiti.",
         "Requisiti previsti dalle Condizioni Specifiche."),
        ("12.9",
         "«Nel Dealer Sales, non essendo dovute Commissioni dall'Acquirente secondo la Vendita in commissione, non trova applicazione la penale di cui alla lett. c)».",
         "Formulazione ellittica («secondo la Vendita in commissione»).",
         "«non essendo dovute dall'Acquirente le Commissioni previste per la Vendita in commissione»."),
        ("5.9",
         "«ogni controversia relativa all'applicazione di quanto disciplinato dal presente articolo è devoluta a un tentativo di mediazione…»",
         "«presente articolo» estende il tentativo di mediazione a tutto l'art. 5 (registrazione, uso consentito, penali), non al solo sistema di gestione dei reclami del comma 5.9.",
         "Alla lettera («presente articolo»). Confermare la portata."),
        ("16.5",
         "«La messa a disposizione del Veicolo per il ritiro non costituisce di per sé costituzione in mora del creditore ai sensi dell'art. 1206 c.c.»",
         "Rispetto alla versione precedente la regola è invertita.",
         "Alla lettera. Confermare che l'inversione è voluta."),
    ]),
    ("D. Refusi e formattazione", "Proposta", [
        ("1, def. «Venditore/i»",
         "«Il termine è sempre riferito al Venditore sostanziale, soggetto diverso rispetto a Fleequid nella Vendita in commissione eseguita mediante Rivendita, ove Fleequid assuma il ruolo di venditore formale, essa è sempre indicata come Fleequid.»",
         "Manca un segno di punteggiatura tra «soggetto diverso rispetto a Fleequid» e «nella Vendita in commissione…»: sono due frasi.",
         "Punto e virgola dopo «rispetto a Fleequid» (così nelle traduzioni)."),
        ("7.1",
         "«…a quanto richiesto dall'art. 13 GDPR -Regolamento (UE) 2016/679 raggiungibile al seguente indirizzo: https://fleequid.com/it/privacy-policy.»",
         "Spazio mancante dopo il trattino; «raggiungibile al seguente indirizzo» è riferito grammaticalmente al Regolamento anziché all'Informativa Privacy.",
         "«…dell'Informativa Privacy, raggiungibile al seguente indirizzo: …, in conformità… all'art. 13 GDPR - Regolamento (UE) 2016/679»."),
        ("15.6",
         "«Rientrano tra tali somme, in particolare le Commissioni già maturate…»",
         "Manca la virgola dopo «in particolare».",
         "«Rientrano tra tali somme, in particolare, le Commissioni…»."),
        ("15.5",
         "«previsti dall'art. 16.2, dall'art. 17.5, dall'art. 17.11 e dall'art. 18.4».",
         "Altrove i rinvii multipli sono nella forma «dagli artt.».",
         "«previsti dagli artt. 16.2, 17.5, 17.11 e 18.4»."),
        ("24.2",
         "«22077 Olgiate Comasco (CO),»",
         "Virgola pendente a fine riga nel blocco dell'indirizzo.",
         "Togliere la virgola."),
        ("24.7 (rubrica)",
         "«Approvazione specifica ai sensi degli artt. 1341 e 1342 c.c.»",
         "Manca il punto finale, presente nei titoli degli articoli (dopo «c.c.» c'è uno spazio).",
         "Uniformare."),
        ("19.7, lett. b)",
         "Rubrica del sottoparagrafo.",
         "Non è in grassetto, a differenza delle rubriche delle lett. a) e c).",
         "Grassetto."),
        ("7.1 / 2.4",
         "URL dell'Informativa Privacy (7.1); lettere a.–d. dell'elenco (2.4).",
         "Rispetto alla versione precedente l'URL ha perso il grassetto e le lettere dell'elenco il corsivo.",
         "Confermare che è voluto."),
        ("Link al Tariffario",
         "Collegamenti ipertestuali al Tariffario nella bozza.",
         "Nella bozza puntavano alle pagine /en/ del sito; nella versione italiana pulita li abbiamo portati su /it/ (e sulla lingua corrispondente in ogni traduzione).",
         "Nessuna azione: solo per informazione."),
        ("Intero documento",
         "Otto doppi spazi nel testo.",
         "Rimossi nella versione italiana pulita.",
         "Nessuna azione: solo per informazione."),
    ]),
]

FONT = "Calibri"


def run(text, bold=False, italic=False, size=20, color=None):
    rpr = f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>'
    if bold:
        rpr += "<w:b/>"
    if italic:
        rpr += "<w:i/>"
    if color:
        rpr += f'<w:color w:val="{color}"/>'
    rpr += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
    return f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def para(text, bold=False, italic=False, size=20, before=0, after=120, keep=False, color=None):
    ppr = f'<w:spacing w:before="{before}" w:after="{after}"/>'
    if keep:
        ppr = "<w:keepNext/>" + ppr
    return f'<w:p><w:pPr>{ppr}</w:pPr>{run(text, bold, italic, size, color)}</w:p>'


def cell(text, width, bold=False, italic=False, shade=None):
    tcpr = f'<w:tcW w:w="{width}" w:type="dxa"/>'
    if shade:
        tcpr += f'<w:shd w:val="clear" w:color="auto" w:fill="{shade}"/>'
    return (f'<w:tc><w:tcPr>{tcpr}</w:tcPr>'
            f'<w:p><w:pPr><w:spacing w:before="40" w:after="40"/></w:pPr>{run(text, bold, italic, 18)}</w:p></w:tc>')


def table(header, rows, widths):
    borders = "".join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
                      for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
    out = [f'<w:tbl><w:tblPr><w:tblW w:w="{sum(widths)}" w:type="dxa"/><w:tblBorders>{borders}</w:tblBorders>'
           '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/>'
           '</w:tblCellMar></w:tblPr><w:tblGrid>' + "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + '</w:tblGrid>']
    out.append('<w:tr><w:trPr><w:tblHeader/></w:trPr>' +
               "".join(cell(h, w, bold=True, shade="E7E6E6") for h, w in zip(header, widths)) + '</w:tr>')
    for r in rows:
        out.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>' +
                   "".join(cell(c, w, bold=(i <= 1), italic=(i == 2)) for i, (c, w) in enumerate(zip(r, widths))) +
                   '</w:tr>')
    out.append('</w:tbl>')
    return "".join(out)


def build():
    widths = [500, 1500, 4700, 4300, 3500]
    body = [para(TITLE, bold=True, size=30, after=60), para(SUBTITLE, size=24, after=240, color="444444")]
    body += [para(p) for p in INTRO]
    n = 0
    for title, last_col, items in SECTIONS:
        body.append(para(title, bold=True, size=24, before=300, after=120, keep=True))
        rows = []
        for art, testo, oss, prop in items:
            n += 1
            rows.append((str(n), "Art. " + art if art[0].isdigit() else art, testo, oss, prop))
        body.append(table(("N.", "Articolo", "Testo della versione F0009_2026", "Osservazione", last_col), rows, widths))
        body.append(para("", after=0))
    sect = ('<w:sectPr><w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/>'
            '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>')
    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
           + "".join(body) + sect + '</w:body></w:document>')
    types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             '<Default Extension="xml" ContentType="application/xml"/>'
             '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
             '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '</Relationships>')
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", doc)
    print(f"{n} osservazioni → {OUT}")


if __name__ == "__main__":
    build()
