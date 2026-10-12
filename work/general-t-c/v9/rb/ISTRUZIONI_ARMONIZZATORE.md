# Istruzioni per l'armonizzazione finale di una lingua (T&C Generali Fleequid v8 → v9)

Contesto: i Termini e Condizioni Generali Fleequid v9 sono stati tradotti in LANG da dieci traduttori diversi, uno per
blocco di articoli (k01…k10), e ogni blocco è già stato revisionato, tranne k10. Sei il revisore legale madrelingua
che rende il documento UNO SOLO: stessa terminologia, stesse formule, stessa tipografia dall'inizio alla fine.

Lavora SOLO nella cartella del worktree indicata nel prompt. Niente `cd` altrove, niente commit.
Puoi modificare soltanto i file `work/general-t-c/v9/rb/LANG/tr_kNN.json`.

## File
- `work/general-t-c/v9/rb/LANG/tr_k01.json` … `tr_k10.json`: le traduzioni (leggi TUTTI i file per intero, compresi
  `new_terms`, `notes`, `review`);
- `work/general-t-c/v9/rb/LANG/terms.json`: termini definiti e titoli fissati in k01 (vincolanti);
- `work/general-t-c/v9/it_new.txt`: IT v9 completo (le chiavi [x.y] corrispondono alle unità: vedi `work/general-t-c/v9/units.json`
  per l'abbinamento id → chiave);
- `work/refs/general_LANG.txt`: LANG v8 pubblicata;
- `work/general-t-c/v9/rb/LANG/brief_k10.md`: brief del blocco k10.

## Cosa fare
1. **Termini definiti**: ogni termine di terms.json deve essere reso allo stesso modo in tutti i blocchi (forme flesse
   ammesse dove la lingua lo richiede). Correggi gli scostamenti.
2. **Locuzioni ricorrenti non definite**: i traduttori hanno scelto ciascuno la propria resa per formule che ricorrono
   in più articoli (es. "fatto salvo il risarcimento del maggior danno", "a titolo di penale", "dolo o colpa grave",
   "manlevare e tenere indenne", "clausola risolutiva espressa", "interessi moratori", "buon fine dell'operazione",
   "pavimento economico", "soglia minima", "presa in carico", "comunicazione di messa a disposizione",
   "intestazione", "effetti restitutori", "disservizi", "acquisto da stock", "regime cauzionale/di garanzia",
   "comma/periodo", "Modello di Vendita Dealer Sales", "archiviazione del reclamo"…). Raccogli le varianti dai
   `new_terms` e dal testo, scegli UNA resa per ciascuna (priorità: resa già presente nella LANG v8; poi la più
   corretta giuridicamente) e applicala ovunque.
3. **Rinvii e citazioni interne**: dove un articolo richiama o riassume un'altra clausola (in particolare l'elenco
   finale delle clausole approvate specificamente ex artt. 1341-1342 c.c. nel blocco k10, e i rinvii tipo "ai sensi
   dell'art. 8.11"), la formulazione deve riprendere quella dell'articolo richiamato così come è stato tradotto.
4. **Revisione piena del blocco k10** (non ancora revisionato): equivalenza con l'IT v9, nessuna omissione o aggiunta,
   continuità con la v8 dove l'IT non cambia.
5. **Tipografia uniforme** in tutto il documento secondo l'uso della lingua e della v8: virgolette, forma delle
   elencazioni e dei rinvii ("lett. a)", "art./artt."), formato di importi, valute e riferimenti normativi,
   maiuscole dei termini definiti, spazi.
6. NON riscrivere ciò che è già corretto e coerente: intervieni solo per uniformare o correggere errori.
   Non cambiare i termini di terms.json; se uno ti sembra sbagliato segnalalo.

Dopo le modifiche esegui (sostituendo LANG) finché TUTTI i blocchi risultano OK:

    python3 -m tcupdate.rebuild check --lang LANG --family "General T&C" --from 8 --to 9 --draft "T&C/General T&C/Vers 9 - Multilanguage - Q4 2026/9_Termini_e_Condizioni_Generali_Fleequid_F0009_2026_BOZZA_STUDIO.docx"

Aggiungi in `tr_k10.json` una lista `harmonization` con voci "locuzione IT: resa scelta (varianti eliminate; blocchi toccati)".

## Risposta (in italiano, sintetica)
- esito del check;
- tabella delle locuzioni uniformate (IT → resa scelta);
- correzioni sostanziali al blocco k10;
- punti da far validare allo studio (massimo dieci, i più rilevanti di tutta la lingua, comprese le scelte sui
  termini definiti nuovi e gli eventuali errori preesistenti della v8 corretti).

## Letture obbligatorie aggiuntive
Prima di iniziare leggi anche `work/general-t-c/v9/rb/NOTE_COMUNI.md` (note valide per tutte le lingue) e, se esiste, `work/general-t-c/v9/rb/LANG/NOTE_LINGUA.md` (decisioni già prese per la tua lingua: vincolanti).
Nella risposta elenca le locuzioni ricorrenti non in tabella con la resa scelta: servono all'armonizzazione.

## Modo di lavoro obbligatorio (per non andare in timeout)
Lavora a PICCOLI PASSI, salvando su file a ogni passo. Non riscrivere mai i JSON a mano per intero: applica le
modifiche con brevi script Python (carica il JSON, sostituisci il testo delle unità interessate, salva con
`ensure_ascii=False, indent=1` conservando l'ordine delle chiavi), una locuzione o un piccolo gruppo per volta.
Per trovare le varianti usa ricerche mirate (grep / script) sui dieci `tr_kNN.json` invece di ricopiare i testi
nella risposta. Dopo ogni gruppo di modifiche lancia il check. Tieni brevi le risposte intermedie.
Ordine: (1) decisioni vincolanti di `LANG/NOTE_LINGUA.md`; (2) punti "da uniformare"; (3) revisione piena di k10 e
allineamento dell'elenco delle clausole ex artt. 1341-1342 agli articoli richiamati; (4) tipografia; (5) lista
`harmonization` e `new_terms`.
