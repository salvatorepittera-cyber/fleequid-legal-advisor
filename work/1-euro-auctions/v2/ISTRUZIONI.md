# 1 Euro Auctions v1 → v2: istruzioni per traduttori e revisori

Contesto: Fleequid (Adorea S.r.l.) gestisce un marketplace europeo B2B di autobus e veicoli commerciali usati. Il documento
sono le «Condizioni Particolari» delle aste "1 Euro Auctions". Lo studio legale ha aggiornato l'italiano per allinearlo
alle nuove Condizioni Generali (CG) v9: cambiano i rinvii agli articoli delle CG e la terminologia, e in fondo nasce una
sezione di approvazione specifica delle clausole ai sensi degli artt. 1341 e 1342 c.c.

Lavora SOLO nella cartella di lavoro indicata nel prompt. Niente `cd` altrove, nessun comando git, nessun commit.
Puoi scrivere soltanto `work/1-euro-auctions/v2/translations/LANG.json`. Lancia i comandi uno alla volta, semplici.

## File
- `work/1-euro-auctions/v2/briefs/LANG.md`: regole, glossario, i 27 paragrafi con IT v1, IT v2, diff e resa LANG v1, e in
  fondo gli articoli completi di contesto. Leggilo INTEGRALMENTE.
- `work/refs/general_LANG.txt`: testo completo delle Condizioni Generali v9 nella lingua (già pubblicate).

## Priorità terminologica
1. Dove l'italiano NON cambia: copia alla lettera la resa v1 di questo documento, anche se le CG v9 usano un'altra parola.
2. Dove l'italiano introduce un termine delle CG v9, usa la resa delle CG v9 della lingua: voci del glossario marcate
   `[General T&C v9]` e, per conferma, `work/refs/general_LANG.txt`. Termini nuovi di questa versione: Accordo vincolante,
   Prezzo di vendita all'Acquirente, Importo Totale Dovuto, Annullamento della vendita, Vendita in commissione, Modello di
   Vendita, Condizioni particolari di vendita, Commissioni (maiuscolo), Tariffe, Condizioni Specifiche, fonti contrattuali.
3. Dove l'italiano SOSTITUISCE un termine (es. «Aggiudicazione» → «Accordo vincolante», «Prezzo di aggiudicazione» →
   «Prezzo di vendita all'Acquirente»), la sostituzione va recepita: il termine vecchio non deve restare.
4. Le voci di glossario marcate «Fleequid Care» riguardano un altro documento: valgono solo se non contrastano con 1 e 2.
5. Solo se un concetto non c'è né nella v1 né nelle CG v9: scelta nuova, da riportare in `new_terms` con il motivo.

## Punti specifici
- Titolo (c01): «Condizioni Particolari d'Asta» diventa «Condizioni Particolari di vendita». Nel preambolo (c02) restano
  entrambe le espressioni: «Condizioni particolari di vendita ai sensi delle CG» (termine definito delle CG v9: usa la
  resa delle CG v9) e «Condizioni Particolari d'Asta» (denominazione abbreviata: resa della v1).
- I rinvii agli articoli delle CG seguono l'italiano v2 (artt. 4.3, 4.4, 9.4 lett. d), 10.5, 12.4, 6.3). Forma dei rinvii
  («art.», «lett.», «c.c.») come nella v1 della lingua e, se la v1 non ha il caso, come nelle CG v9 della lingua.
- Sezione finale (c24–c29): c24 è la riga di asterischi «*****», da lasciare identica. Per c25–c29 riprendi la formula
  usata nella clausola di approvazione specifica (artt. 1341 e 1342 c.c.) in fondo alle CG v9 della lingua: cercala in
  `work/refs/general_LANG.txt`. Le sintesi tra parentesi delle clausole richiamate (artt. 2.3, 3.6, 3.7, 3.8, 6.1, 6.2)
  devono riprendere le parole con cui quegli articoli sono tradotti in QUESTO documento (v1 o paragrafi che stai traducendo).
- Tre refusi dell'italiano v2, già segnalati: traduci il senso corretto, senza riprodurli.
  - c02: «(si seguito anche …)» sta per «(di seguito anche …)».
  - c09: «Accordo Vincolante» è il termine definito «Accordo vincolante», uguale agli altri paragrafi.
  - c11: il paragrafo comincia con «l'incasso netto di cui all'art. 3.1 … sia inferiore al PMIV» perché è caduto il
    «Qualora» iniziale: traduci «Qualora l'incasso netto di cui all'art. 3.1 …».

## Controllo formale (da ripetere finché stampa OK)

    python3 -m tcupdate.checktr work/1-euro-auctions/v2 LANG "T&C/1 Euro Auctions/Vers 2 - Multilanguage - Q4 2026/2_CPA_1EuroAuction_Versione_2_2026_DEF_ITA.docx"
