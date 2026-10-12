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

---

# Revisione (seconda passata, revisore diverso dal traduttore)

Sei il REVISORE legale madrelingua. Leggi tutto il brief della lingua e rivedi `translations/LANG.json` voce per voce.
Puoi modificare soltanto quel file. Applica le correzioni con brevi script Python (carica il JSON, sostituisci una
sottostringa esatta verificando che compaia, salva con `ensure_ascii=False, indent=1`): non riscrivere il file a mano.

1. Equivalenza giuridica con l'italiano v2: nessuna omissione, nessuna aggiunta, RIMOZIONI recepite, rinvii e numeri esatti.
2. Dove l'italiano non cambia, il testo deve essere la copia letterale della v1 della lingua. Annulla ogni riscrittura
   non richiesta dal diff.
3. Terminologia, in quest'ordine: termine già usato nella v1 di QUESTO documento per lo stesso termine italiano →
   Condizioni Generali v9 della lingua (`work/refs/general_LANG.txt`) → scelta nuova. Decisioni già prese, da applicare:
   - **Cambio di sola maiuscola in italiano** (es. «Condizioni specifiche» → «Condizioni Specifiche», «Proposta di
     Vendita» → «Proposta di vendita», «commissioni» → «Commissioni»): la PAROLA della v1 resta; cambia al più la
     maiuscola, secondo l'uso della lingua. Si passa alla resa delle CG v9 solo se la parola della v1 nel paragrafo
     diventa ambigua o coincide con un altro termine del documento: in quel caso spiega il perché in `review`.
   - **«Tariffario»** resta quello della v1 di questo documento; **«Tariffe»** (nuovo) prende la resa delle CG v9. Se le
     due parole finiscono identiche o indistinguibili nella stessa frase (art. 3.2), scegli la soluzione più chiara e
     segnalala nella risposta.
   - **«perfezionarsi / perfezionamento» dell'Accordo vincolante**: una sola resa in tutti i paragrafi tradotti, quella
     con cui le CG v9 della lingua accompagnano il termine (anche in c09 e c12, dove il verbo italiano non cambia ma
     cambia il soggetto).
   - **«Modello di Vendita in commissione»**: una sola forma in c10 e c15, costruita con i due termini delle CG v9;
     verifica in `work/refs/general_LANG.txt` se le CG usano già una forma analoga (es. per «Modello di Vendita Dealer
     Sales») e seguila.
   - Sigle e nomi della v1 (PMIV, PR, 1 Euro Auctions, Marketplace, Deposito cauzionale) restano quelli della v1 anche se
     le CG v9 ne usano altri: sono difetti di uniformità tra documenti, da segnalare nella risposta, non da correggere.
4. Sezione finale (c25–c29): la formula deve essere quella della clausola di approvazione specifica delle CG v9 della
   lingua; le sintesi tra parentesi devono usare le stesse parole degli articoli richiamati in questo documento.
5. Registro legale, grammatica, tipografia della v1 (virgolette, spazi, maiuscole dei termini definiti).
6. Tag `<b>/<i>/<u>` sulle parole corrispondenti a quelle dell'italiano v2.

Aggiungi al JSON una lista `review` con voci «cNN: prima → dopo — perché» (anche vuota). Rilancia il controllo formale
finché stampa OK. Risposta in italiano, breve: esito del controllo; correzioni sostanziali; decisioni prese sui punti
sopra; punti da far validare allo studio o all'utente (massimo cinque); difetti preesistenti della v1 notati.
