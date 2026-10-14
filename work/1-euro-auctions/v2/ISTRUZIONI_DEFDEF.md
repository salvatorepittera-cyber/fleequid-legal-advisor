# 1 Euro Auctions v2: correzioni dello studio del 13/10 da riportare nelle lingue

Le traduzioni v2 erano già fatte e revisionate. Lo studio ha poi corretto l'italiano in 12 paragrafi. Vanno riportate
nella lingua SOLO quelle correzioni: intervento chirurgico, niente riscritture, niente miglioramenti.

Lavora SOLO nella cartella di lavoro indicata nel prompt. Niente `cd` altrove, nessun comando git, nessun commit.
Puoi scrivere soltanto `work/1-euro-auctions/v2/translations/LANG.json`. Lancia i comandi uno alla volta, semplici.
Modifica il JSON con brevi script Python (carica, assegna la voce, salva con `ensure_ascii=False, indent=1`).

## File
- `work/1-euro-auctions/v2/DEFDEF_CORREZIONI.md`: i 12 paragrafi con l'italiano di prima, quello di ora e il diff.
- `work/1-euro-auctions/v2/briefs/LANG.md`: per ogni paragrafo IT v1, IT v2 definitivo e **resa LANG v1**; glossario; in
  fondo gli articoli completi di contesto. Gli id (c01…c37) sono quelli di `DEFDEF_CORREZIONI.md`.
- `work/1-euro-auctions/v2/translations/LANG.json`: le traduzioni v2 attuali (`translations`), già rinumerate.
- `work/refs/general_LANG.txt`: Condizioni Generali v9 nella lingua.
- `work/1-euro-auctions/v2/ISTRUZIONI.md`: le regole terminologiche con cui è stata fatta la v2 (valgono ancora).

## Da dove si parte, voce per voce
- **Già tradotti** (c01, c03, c05, c07, c12): parti dalla voce attuale del JSON e cambia solo ciò che cambia nel diff.
- **Nuovi** (c02, c04, c06, c16, c19, c24, c26): la voce non c'è ancora. Parti dalla **resa LANG v1** riportata nel brief,
  copiala alla lettera e cambia solo ciò che cambia tra IT v1 e IT v2 definitivo. Aggiungi la voce al JSON.
- Tutte le altre voci del JSON non si toccano.

## Indicazioni per paragrafo
- **c01** (titolo): in italiano cambia solo la maiuscola («Condizioni particolari di vendita», ora identico al termine
  definito delle CG v9). Se la voce attuale è già la resa delle CG v9 del termine, resta com'è; cambia la maiuscola
  solo se l'uso della lingua e il titolo delle CG v9 lo richiedono.
- **c02**: «Condizioni Particolari d'Asta» → «Condizioni particolari di vendita»: stessa resa del termine usata in c03
  («costituiscono Condizioni particolari di vendita ai sensi delle CG»). Il resto è la v1 alla lettera.
- **c03**: si aggiunge l'art. 4.5 all'elenco dei rinvii; la denominazione abbreviata diventa «Condizioni Particolari»:
  usa la resa con cui «Condizioni Particolari» / «presenti Condizioni Particolari» è reso nel RESTO di questo documento
  (v1, es. artt. 1.3, 2.3, 6.4). La resa di «d'Asta» sparisce.
- **c04**: resta la prima parte fino a «anche mediante semplice indicazione o etichettatura»; il resto è sostituito da
  «purché il relativo testo sia reso accessibile e consultabile prima della formulazione dell'Offerta ai sensi
  dell'art. 4.5 delle CG». Sparisce tutta la seconda frase (applicazione automatica, senza ulteriore accettazione).
  «Offerta» come nella v1 di questo documento; per «formulazione dell'Offerta» guarda come le CG v9 della lingua
  rendono l'art. 4.5 e la formulazione delle Offerte.
- **c05**: sparisce la prima frase. Resta la seconda frase della voce attuale, identica.
- **c06**: base v1. «Condizioni Specifiche» con la stessa resa della voce c28 (art. 6.4), che in italiano è quasi
  identica; sparisce «in quanto compatibili con la natura delle "1 Euro Auctions"»; art. 3.3 → art. 4.3.
- **c07**: «da condizioni economiche specifiche, distinte rispetto a quelle delle Aste ordinarie».
- **c12**: sparisce la coda «; conseguentemente, non sorgerà … alcun obbligo di acquisto del Veicolo». Punto fermo dopo «CG».
- **c16** e **c26**: «regolare conclusione del Contratto» → «regolare perfezionamento dell'Accordo vincolante», con la
  stessa resa di «perfezionamento dell'Accordo vincolante» delle voci c10, c27 e c34. Il resto è la v1 alla lettera.
- **c19** (rubrica, tutta in grassetto): «Struttura commissionale nella vendita in commissione.» In italiano è
  minuscolo ma è il termine definito «Vendita in commissione»: usa la resa del termine già usata nella voce c08.
- **c24**: «Acquirente» senza «aggiudicatario»; «Importo Totale Dovuto» come nella voce c23; «e dalle condizioni
  applicabili alla specifica 1 Euro Auction» (non più il Tariffario).

## Difetti della v1 già corretti, da conservare
Nelle voci nuove parti dalla resa v1, che contiene difetti già corretti nei Word consegnati. Vanno riportati nella voce:
- **FR c06**: «Conditions particulières» → «Conditions spécifiques» (è la resa di «Condizioni Specifiche», come in c28).
- **FR c16**: «MCSP» → «PMIV».
- **PL c16**: «Sprzedawca musi być w pełni» → «Sprzedawca musi w pełni».

## Registro delle correzioni
Aggiungi al JSON la lista `defdef`: una riga per ognuno dei 12 id, «cNN: cosa è cambiato» oppure «cNN: invariata — perché».

## Controllo formale (da ripetere finché stampa OK)

    python3 -m tcupdate.checktr work/1-euro-auctions/v2 LANG "T&C/1 Euro Auctions/Vers 2 - Multilanguage - Q4 2026/2_CPA_1EuroAuction_Versione_2_2026_DEF_ITA.docx"

## Risposta (in italiano, breve)
Esito del controllo; per ogni id la voce finale in una riga con una retro-traduzione italiana letterale delle sole parti
cambiate; dubbi (massimo tre). Non segnalare di nuovo i difetti della v1 fuori da questi 12 paragrafi.
