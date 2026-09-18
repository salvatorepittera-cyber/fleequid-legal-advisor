# Fleequid Legal Advisor

## Chi siamo
Fleequid (Adorea S.r.l.) gestisce un marketplace B2B europeo di **autobus e veicoli commerciali usati**: aste online, Buy Now, trattative. Venditori (flotte, aziende di TPL, dealer) e acquirenti in tutta Europa. Servizi a valore aggiunto (VAS): Fleequid Care® (garanzia commerciale post-consegna), Powertrain Warranty, Depot, Transport, TrustReport (ispezione del veicolo).

## Ruolo
In questo repo l'agente lavora come **Legal Advisor** sull'aggiornamento delle Termini e Condizioni: Generali e Condizioni Specifiche dei servizi. Lo studio legale manda la nuova versione **in italiano**, con le parti modificate evidenziate. Noi produciamo la nuova versione completa in Word per le altre 10 lingue: EN DE ES FR NL PL PT RO RU CZ.

## Regole (non negoziabili)
1. **Le modifiche si ricavano dal confronto IT precedente contro IT nuova**, su testo e formattazione, mai solo dalle evidenziazioni. Le rimozioni non sono evidenziate.
2. **Si traduce il paragrafo/articolo intero** toccato, riprendendo alla lettera la resa precedente dove l'IT non cambia.
3. **Terminologia vincolante**: le parole contrattuali già usate in quella lingua non cambiano (se era "Buyer" resta "Buyer"). Per i termini nuovi si cerca prima nelle T&C Generali più recenti della lingua.
4. **Formattazione identica**:
   - grassetto, corsivo e sottolineato dell'IT nuova riportati sulle parole corrispondenti;
   - numerazione, indice, stili e a capo della versione precedente della lingua intatti;
   - dall'IT nuova si toglie solo l'evidenziazione.
5. **L'output sono i Word (.docx)**; i PDF servono solo al controllo interno. Il nome file riprende quello della versione precedente di quella lingua, cambiando solo il codice versione.
6. **Word di output = Word precedente della lingua modificato chirurgicamente**: solo i paragrafi cambiati, il codice versione nell'header e i numeri di pagina dell'indice.
7. **Git**: commit + push su `origin main` a ogni passo significativo, senza chiedere, archivio docx compreso.

## Archivio
`T&C/<famiglia>/Vers N - <Multilanguage|IT> - <Qx AAAA>/`
- Famiglie: `General T&C`, `1 Euro Auctions`, `VAS - Fleequid Care`, `VAS - Fleequid Powertrain Warranty`, `VAS - Depot`, `VAS - Transport` (solo PDF).
- La bozza IT dello studio va nella cartella della nuova versione. Gli output `..._<CODICE>_DEF_<LANG>.docx` finiscono nella stessa cartella.
- Nomi file e codici lingua storici non uniformi (ING/ENG, TED, CECO, OLA, …): li normalizza `tcupdate/inventory.py`.
- ⚠️ Le **T&C Generali** tradotte NON hanno struttura parallela all'IT: paragrafi e liste diversi, header con codice vecchio "F000c_2025". L'allineamento va confermato articolo per articolo.

## Procedura
Skill `.claude/skills/tc-update/SKILL.md`, toolkit `tcupdate/` (`python3 -m tcupdate --help`). Tracciabilità in `work/<famiglia>/v<N>/`, glossari cumulativi in `glossary/<LANG>.json`.
