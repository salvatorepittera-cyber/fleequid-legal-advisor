---
name: tc-update
description: Aggiorna una T&C Fleequid (Generali o di servizio) a una nuova versione in tutte le lingue partendo dalla bozza italiana dello studio legale. Usala quando arriva una nuova versione IT con parti evidenziate da localizzare nelle altre 10 lingue.
---

# Aggiornamento T&C multilingua

Argomenti attesi: famiglia (es. "Fleequid Care", "General T&C"), versione precedente e nuova. Se mancano, ricavali da `python3 -m tcupdate inventory`. La bozza IT deve stare in `T&C/<famiglia>/Vers <N> - .../`.

Variabili: `F="<famiglia>" A=<prev> B=<new>`. Tutti i comandi si lanciano dalla root del repo. Dopo ogni passo che produce file: `git add -A && git commit -m "..." && git push`.

## 1. Discovery e diff
```
python3 -m tcupdate inventory
python3 -m tcupdate diff --family "$F" --from $A --to $B
```
Leggi `work/<famiglia>/v<B>/diff_report.md` e controlla:
- ogni modifica è **dal confronto prima/dopo**; le righe "Cambiati ma non evidenziati" (tipicamente le rimozioni) sono modifiche vere;
- "Evidenziati ma identici": avvisa l'utente;
- modifiche strutturali (paragrafi o articoli inseriti/rimossi): se cambia la numerazione, cerca i rinvii interni ("art. X.Y") in tutto il documento IT e segnala quelli da aggiornare;
- codice versione nell'header;
- possibili refusi.

**Checkpoint con l'utente** (AskUserQuestion) per:
- conferma dell'elenco modifiche;
- quali refusi correggere nell'IT. Le correzioni vanno in `work/.../it_fixes.json` come `[{"key","old","new"}]`.

## 2. IT pulita
```
python3 -m tcupdate clean-it --family "$F" --from $A --to $B
```
Toglie solo le evidenziazioni e applica `it_fixes.json`. Tutto il resto resta com'è.

## 3. Allineamento, glossario, brief
```
python3 -m tcupdate prepare --family "$F" --from $A --to $B
```
- Se una lingua riporta "DA CONFERMARE", apri `alignment_<LANG>.md`, verifica gli abbinamenti leggendo IT e lingua. Correggi `alignment_<LANG>.json` impostando `confidence: "key"` solo dopo la verifica. Tipico per le T&C Generali, che non hanno struttura parallela.
- Poi rilancia l'iniezione con `--no-strict` solo per le lingue confermate.

## 4. Traduzione (10 subagenti in parallelo, uno per lingua)
Prompt standard (sostituisci LANG, lingua, famiglia):

> Sei un traduttore legale senior (IT→LANG) per Fleequid (Adorea S.r.l.), marketplace B2B europeo di autobus usati. Stiamo aggiornando <documento> dalla versione A alla B.
> 1. Leggi INTEGRALMENTE `work/<fam>/v<B>/briefs/LANG.md` (regole, glossario, paragrafi con IT prev/new/diff/LANG prev, articoli di contesto).
> 2. Per termini nuovi cerca prima in `work/refs/general_LANG.txt` e nel documento LANG precedente, e riusa quella resa.
> 3. Traduci l'INTERO paragrafo: dove l'IT non cambia copia alla lettera la resa precedente; recepisci aggiunte e RIMOZIONI.
>    - `<b>/<i>/<u>` con lo stesso numero di segmenti dell'IT nuova.
>    - Refusi solo italiani: resa precedente identica.
> 4. Scrivi `work/<fam>/v<B>/translations/LANG.json` (lang, translations{cNN}, new_terms, notes).
> 5. `python3 -m tcupdate.checktr work/<fam>/v<B> LANG "<IT nuova pulita>"`, da ripetere finché stampa OK.
> 6. Rileggi contro l'IT nuova. Nessun commit. Rispondi con esito, new_terms e fonte, dubbi.

## 5. Revisione (subagenti revisori, uno per lingua)
Il revisore riceve brief e JSON e controlla paragrafo per paragrafo:
- significato equivalente all'IT nuova;
- nessuna omissione né aggiunta;
- rimozioni recepite;
- termini identici alla versione precedente o al glossario;
- registro legale;
- tag B/I/U sulle parole giuste.

Corregge direttamente il JSON, rilancia `checktr` e riporta ogni correzione motivata.

## 5-bis. Correzioni fuori diff (difetti preesistenti della lingua)
Solo se approvate dall'utente.
- **Paragrafo già modificato nella nuova versione:** correggi direttamente `translations/<LANG>.json` e annota la correzione in `review`.
- **Paragrafo non toccato:** usa `work/.../post_fixes/<LANG>.json` con la forma `[{"key","old","new","why"}]`, una voce per occorrenza.
  - Il testo nuovo eredita il formato del primo run: se una sostituzione attraversa un cambio di corsivo o grassetto, spezzala in due voci.
  - `inject` le applica e `verify` le riconosce.

## 6. Iniezione, indice, verifica
```
python3 -m tcupdate inject --family "$F" --from $A --to $B
python3 -m tcupdate toc    --family "$F" --from $A --to $B   # Word via AppleScript: numeri pagina indice + PDF in work/.../pdf
python3 -m tcupdate verify --family "$F" --from $A --to $B
```
- `verify` deve essere verde per IT e per tutte le lingue.
- Word non risponde (timeout AppleEvent)? Di solito c'è una finestra di dialogo aperta: chiedi all'utente di chiuderla.
- Controllo visivo a campione sui PDF: indice, numerazione dei paragrafi modificati, grassetti.

## 7. Chiusura
- Aggiungi i `new_terms` approvati a `glossary/<LANG>.json`.
- Commit + push.
- Report all'utente:
  - file prodotti;
  - modifiche applicate;
  - termini nuovi introdotti per lingua;
  - punti da far validare allo studio.

---

# Runbook: com'è andata su Fleequid Care v2 (2026-09-15)

Sequenza esatta, da ripetere uguale. `F="Fleequid Care" A=1 B=2`.

```
python3 -m tcupdate inventory
python3 -m tcupdate diff     --family "$F" --from $A --to $B     # 16 modifiche, 2 non evidenziate
# checkpoint utente: conferma modifiche + refusi -> work/fleequid-care/v2/it_fixes.json
python3 -m tcupdate clean-it --family "$F" --from $A --to $B
python3 -m tcupdate prepare  --family "$F" --from $A --to $B     # 10 brief + glossari + allineamenti "key"
# 10 subagenti traduttori in parallelo (prompt al § 4), poi commit dello stato pre-revisione
# 10 subagenti revisori in parallelo (prompt al § 5)
python3 -m tcupdate inject   --family "$F" --from $A --to $B
python3 -m tcupdate toc      --family "$F" --from $A --to $B
python3 -m tcupdate verify   --family "$F" --from $A --to $B
```

Tempi: traduttori e revisori circa 3 minuti ciascuno, tutti in parallelo. Il resto è immediato.

## Prompt revisore (§ 5), versione usata
> Sei il REVISORE legale madrelingua LANG delle T&C Fleequid. Leggi tutto `briefs/LANG.md` e rivedi `translations/LANG.json`.
> 1. Equivalenza con l'IT nuova: nessuna omissione né aggiunta, rimozioni recepite.
> 2. Dove l'IT non cambia, il testo deve essere la copia letterale della versione precedente. Scostamenti ammessi solo se richiesti dal diff, se correggono un refuso evidente o se allineano B/I/U all'IT nuova. Ogni altra riscrittura va annullata.
> 3. Priorità terminologica: (1) termine già usato nella v1 di QUESTO documento, anche nello stesso paragrafo; (2) T&C Generali della lingua; (3) scelta nuova. Ripristina le sostituzioni indebite.
> 4. Registro, grammatica, tipografia. 5. Tag B/I/U sulle parole giuste.
> Correggi il JSON, aggiungi la lista `review` con "cNN: prima → dopo, perché", rilancia `checktr` fino a OK. Nessun commit. Riporta correzioni e punti da far validare allo studio.

## Cose imparate, da non riscoprire
- **Le evidenziazioni non bastano**: in Care v2 due rimozioni (artt. 1487 e 1176 c.c.) non erano evidenziate. Vale il diff.
- **Nome file**: si riprende quello della versione precedente di quella lingua cambiando solo il codice versione. Su Care sono stati normalizzati due refusi dei vecchi nomi (`.docx.docx` del PL, spazio invece di underscore nel DE).
- **Output = docx.** I PDF servono solo al controllo e restano in `work/<fam>/v<N>/pdf/`.
- **Indice**: lo ricalcola Word. Nella v1 polacca tutte le voci puntavano a pagina 1, ed è stato corretto qui.
- **Word/AppleScript**: `open` non restituisce il documento, serve `active document`; i percorsi vanno passati come POSIX e i file temporanei devono stare nel container di Word. Se va in timeout, c'è una finestra di dialogo da chiudere a mano.
- **I traduttori tendono a preferire i termini delle T&C Generali**: il revisore deve riportarli a quelli della v1 del documento (successo su NL "koopovereenkomst" e CZ "závada").
- **Difetti preesistenti**: si correggono solo su richiesta dell'utente, con `post_fixes` (§ 5-bis) e annotati nel report.
