# Istruzioni per il revisore di un blocco (T&C Generali Fleequid v8 → v9)

Contesto: Fleequid (Adorea S.r.l.) gestisce un marketplace europeo B2B di autobus e veicoli commerciali usati.
I Termini e Condizioni Generali passano dalla v8 alla v9 con una riscrittura ampia dell'italiano. Sei il REVISORE
legale madrelingua della lingua indicata: rivedi UN blocco tradotto da un altro traduttore.

Lavora SOLO nella cartella del worktree indicata nel prompt. Niente `cd` altrove, niente commit, nessun altro file toccato.
`LANG` e `kNN` sono quelli del prompt.

## File
- `work/general-t-c/v9/rb/LANG/brief_kNN.md`: regole, glossario, tabella termini v9, IT v9, IT v8, diff, resa LANG v8 (leggilo INTEGRALMENTE);
- `work/general-t-c/v9/rb/LANG/tr_kNN.json`: traduzione da rivedere;
- `work/general-t-c/v9/rb/LANG/terms.json`: termini v9 fissati dal blocco k01 (se esiste: vincolanti);
- `work/refs/general_LANG.txt`: testo completo LANG v8; `work/general-t-c/v9/it_new.txt`: IT v9 completo.

## Controlli, unità per unità
1. Equivalenza giuridica con l'IT v9: nessuna omissione, nessuna aggiunta, rimozioni recepite, nessun cambio di senso
   (obblighi, facoltà, termini, condizioni, soggetti, importi, rinvii).
2. Continuità con la LANG v8 pubblicata: dove l'IT non cambia il testo deve essere la copia letterale della resa v8.
   Scostamenti ammessi solo se richiesti dal diff IT o per correggere un errore evidente. Annulla le riscritture gratuite.
3. Terminologia: tabella termini v9 (terms.json) → termine già usato nella LANG v8 di questo documento → glossario →
   scelta nuova. Ripristina le sostituzioni indebite. Ogni termine definito reso sempre allo stesso modo.
   - Blocco k01: valuta criticamente le rese dei termini definiti NUOVI (`new_terms`, `notes`): devono essere quelle
     che userebbe un giurista madrelingua in condizioni generali di un marketplace/asta di veicoli, univoche, non
     confondibili tra loro, utilizzabili in tutto il documento (controlla in it_new.txt come il termine è usato
     altrove). Cambia una resa solo per un motivo concreto e, se la cambi, cambiala OVUNQUE nel blocco e in `new_terms`.
     Un termine già definito nella v8 non si cambia.
   - Altri blocchi: NON cambiare i termini della tabella; se uno ti sembra sbagliato, segnalalo nella risposta.
4. Registro legale, grammatica, ortografia, tipografia della lingua (virgolette, maiuscole dei termini definiti,
   formato di importi e date coerente con la v8).
5. Tag `<b>/<i>/<u>` sulle parole corrispondenti a quelle dell'IT.
6. URL ed e-mail identici all'IT (non localizzarli: lo fa il sistema).

Correggi direttamente `tr_kNN.json` mantenendo la struttura e aggiungi una lista `review` con voci
"uNNN: prima → dopo — perché". Poi esegui esattamente (sostituendo LANG e kNN) finché stampa `kNN: OK`:

    python3 -m tcupdate.rebuild check --lang LANG --chunk kNN --family "General T&C" --from 8 --to 9 --draft "T&C/General T&C/Vers 9 - Multilanguage - Q4 2026/9_Termini_e_Condizioni_Generali_Fleequid_F0009_2026_BOZZA_STUDIO.docx"

Se resta un errore sui numeri che è un falso positivo inevitabile (orari, numerali secondo l'uso della lingua),
non forzare il testo: segnala l'id nella risposta.

## Risposta (in italiano, sintetica)
- esito del check (ed eventuali id con falso positivo);
- correzioni sostanziali (non l'elenco completo);
- per k01: tabella finale dei termini definiti nuovi IT → LANG;
- punti da far validare allo studio; termini della tabella che ti sembrano sbagliati.

## Letture obbligatorie aggiuntive
Prima di iniziare leggi anche `work/general-t-c/v9/rb/NOTE_COMUNI.md` (note valide per tutte le lingue) e, se esiste, `work/general-t-c/v9/rb/LANG/NOTE_LINGUA.md` (decisioni già prese per la tua lingua: vincolanti).
Nella risposta elenca le locuzioni ricorrenti non in tabella con la resa scelta: servono all'armonizzazione.
