# Istruzioni: correzioni chirurgiche dello studio (9/10/2026) da riportare in una lingua

Contesto: i Termini e Condizioni Generali Fleequid v9 sono già tradotti, revisionati e armonizzati in LANG. Lo studio
legale ha corretto 35 paragrafi dell'italiano. Devi riportare nella traduzione LANG SOLO quelle correzioni: intervento
chirurgico, tutto il resto resta identico carattere per carattere.

Lavora SOLO nella cartella del worktree indicata nel prompt. Niente `cd` altrove, niente commit.
Puoi modificare soltanto i file `work/general-t-c/v9/rb/LANG/tr_kNN.json` (campo `translations` delle unità elencate)
e creare `work/general-t-c/v9/rb/LANG/defdef.json`.

## File
- `work/general-t-c/v9/rb/DEFDEF_CORREZIONI.md`: le 35 unità con il diff IT precedente → IT corretta e le note (LEGGILO TUTTO);
- `work/general-t-c/v9/rb/LANG/tr_kNN.json`: traduzioni attuali (il file di ogni unità è indicato nel titolo della voce);
- `work/general-t-c/v9/rb/LANG/NOTE_LINGUA.md` e `terms.json`: terminologia vincolante della lingua;
- `work/general-t-c/v9/it_new.txt`: IT v9 corretta completa (chiavi [x.y]) per il contesto.

## Regole
1. Per ogni unità cambia nella traduzione solo ciò che il diff IT richiede (aggiunte, sostituzioni, rimozioni), con la
   terminologia già usata nel documento LANG (cerca nei `tr_kNN.json` come sono resi altrove gli stessi termini: es.
   «giorni di calendario», «profilo», «Condizioni particolari di vendita», «CG», «danneggiamento»). Non migliorare,
   non riformulare, non toccare il resto del paragrafo.
2. Se la traduzione attuale dice GIÀ ciò che dice l'IT corretta (capita: alcune ambiguità dell'IT erano state sciolte in
   traduzione nello stesso senso, o la correzione è solo di punteggiatura italiana), NON cambiarla.
3. Tag `<b>/<i>/<u>`: stesso numero di segmenti dell'IT corretta (attenzione a u286, che acquista il grassetto sulla rubrica).
4. Numeri, importi, rinvii, URL ed e-mail identici all'IT (gli URL NON si localizzano: lo fa il sistema).
5. Applica le modifiche con brevi script Python (carica il JSON, sostituisci una sottostringa esatta nel testo
   dell'unità verificando che compaia una sola volta, salva conservando la formattazione esistente del file:
   stessa indentazione, `ensure_ascii=False`), poche unità per volta. Non riscrivere i file a mano. Script in
   `<scratchpad>/defdef_LANG/`, lanciati con `PYTHONPATH=. python3 <script>` come comando singolo (niente && né heredoc).
6. Scrivi `work/general-t-c/v9/rb/LANG/defdef.json`: un oggetto `{ "uNNN": "cosa hai cambiato (prima → dopo)" oppure "invariata: motivo" }`
   con TUTTE le 35 unità.
7. Alla fine esegui (sostituendo LANG) finché tutti i blocchi risultano OK:

       python3 -m tcupdate.rebuild check --lang LANG --family "General T&C" --from 8 --to 9 --draft "T&C/General T&C/Vers 9 - Multilanguage - Q4 2026/9_Termini_e_Condizioni_Generali_Fleequid_F0009_2026_BOZZA_STUDIO.docx"

   Se resta un errore sui numeri che è un falso positivo inevitabile, non forzare il testo: segnalalo.

## Risposta (in italiano, breve)
- esito del check;
- unità modificate / lasciate invariate (solo i numeri) e, per quelle invariate, il motivo in una riga;
- eventuali dubbi di resa (massimo cinque).
