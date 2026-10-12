# Istruzioni per il traduttore di un blocco (T&C Generali Fleequid v8 → v9)

Contesto: Fleequid (Adorea S.r.l.) gestisce un marketplace europeo B2B di autobus e veicoli commerciali usati
(aste online, Buy Now, trattative). Lo studio legale ha riscritto gran parte dei Termini e Condizioni Generali
italiani (v9). Tu traduci UN blocco di articoli in UNA lingua. Devi scrivere come un giurista madrelingua che
redige condizioni generali B2B in quella lingua: preciso, formale, senza calchi dall'italiano.

Lavora SOLO nella cartella del worktree indicata nel prompt. Niente `cd` altrove, niente commit, nessun altro file toccato.
`LANG` e `kNN` sono quelli del prompt.

## Passi
1. Leggi INTEGRALMENTE `work/general-t-c/v9/rb/LANG/brief_kNN.md`: regole vincolanti, glossario, tabella dei termini
   v9 già fissati per la lingua (se presente: è VINCOLANTE, viene dal blocco k01 già revisionato), e i paragrafi
   da tradurre con IT v9 e, dove esistono, IT v8, diff e resa LANG v8.
2. Continuità con la versione v8 pubblicata: dove l'IT non cambia, copia alla lettera la resa v8; dove cambia in
   parte, parti dalla resa v8 e modifica solo ciò che il diff richiede (comprese le rimozioni). L'abbinamento con la
   resa v8 è automatico e può essere sbagliato: se il testo LANG v8 mostrato non corrisponde all'IT v8 indicato,
   cerca il paragrafo giusto in `work/refs/general_LANG.txt`.
3. Terminologia: tabella termini v9 → glossario → resa già usata nella v8 LANG (`work/refs/general_LANG.txt`) →
   scelta nuova, da riportare in `new_terms`. Un termine definito va reso SEMPRE allo stesso modo. Per capire un
   termine o un rinvio guarda il resto del documento in `work/general-t-c/v9/it_new.txt`.
4. Per il blocco k01 (frontespizio, art. 1, titoli): le definizioni possono essere in ordine diverso tra IT e LANG;
   trova tu la definizione v8 corrispondente (per significato) nel blocco in fondo al brief. Un termine definito già
   esistente nella v8 NON cambia. I titoli di articolo già esistenti riprendono la v8, in forma normale (non tutto
   maiuscolo), con il punto finale dove l'IT lo ha. In `new_terms` elenca OGNI termine definito nuovo.
5. Scrivi `work/general-t-c/v9/rb/LANG/tr_kNN.json` nella forma indicata in fondo al brief, con TUTTE le unità elencate.
6. Esegui esattamente (sostituendo LANG e kNN):

   python3 -m tcupdate.rebuild check --lang LANG --chunk kNN --family "General T&C" --from 8 --to 9 --draft "T&C/General T&C/Vers 9 - Multilanguage - Q4 2026/9_Termini_e_Condizioni_Generali_Fleequid_F0009_2026_BOZZA_STUDIO.docx"

   e correggi finché stampa `kNN: OK`. Il controllo verifica: unità presenti, stesso numero di segmenti
   `<b>/<i>/<u>` dell'IT, numeri e rinvii identici, e-mail e URL identici (NON localizzare gli URL: lo fa il sistema),
   lunghezza plausibile. Se un errore sui numeri è un falso positivo inevitabile (es. orari scritti secondo l'uso
   della lingua, numerali che la lingua scrive diversamente), NON forzare il testo: lascialo corretto e segnala
   l'id dell'unità nella risposta.
7. Rileggi tutto contro l'IT v9: nessuna omissione, nessuna aggiunta, rinvii agli articoli con la numerazione v9.

## Risposta (in italiano, sintetica)
- esito del check (ed eventuali id con falso positivo sui numeri);
- termini nuovi scelti (IT → LANG → motivo), solo quelli non già in tabella;
- punti da far validare allo studio;
- incongruenze trovate nell'IT.

## Letture obbligatorie aggiuntive
Prima di iniziare leggi anche `work/general-t-c/v9/rb/NOTE_COMUNI.md` (note valide per tutte le lingue) e, se esiste, `work/general-t-c/v9/rb/LANG/NOTE_LINGUA.md` (decisioni già prese per la tua lingua: vincolanti).
Nella risposta elenca le locuzioni ricorrenti non in tabella con la resa scelta: servono all'armonizzazione.
