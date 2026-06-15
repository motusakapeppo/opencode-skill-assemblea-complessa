# Assemblea Complessa V1 — Deep Multi-Round Deliberation Engine

## Architettura del Cast (Routing Asimmetrico)

| Ruolo | Dove gira | Modello | Categoria | Perché |
|-------|-----------|---------|-----------|--------|
| **Presidente** | Sisyphus (io) | deepseek-v4-flash | — | Moderatore veloce, orchestro la chat |
| **L'Hacker** | Sub-agente | kimi-k2.7-code | `quick` | Proposte concrete, coding, implementazione |
| **Il Contabile** | Sub-agente | minimax-m3 | `deep` | Numeri, costi, ROI |
| **L'Utente** | Sub-agente | minimax-m3 | `deep` | Voce del cliente, semplicità |
| **L'Avvocato del Diavolo** | Sub-agente | deepseek-v4-flash | `ultrabrain` | Critica puntuale, anti-sycophancy |
| **Lead Architect** | Sub-agente | deepseek-v4-flash | `ultrabrain` | Sintesi finale e verbale |

### Mappa modelli effettiva (da oh-my-openagent.json)
```
kimi-k2.7-code (256K):    Hacker (quick) — coding specialist
minimax-m3 (1M ctx):      Contabile, Utente (deep) — analitico, linguaggio naturale
deepseek-v4-flash (1M):   Avvocato, Lead Architect (ultrabrain)
deepseek-v4-pro (1M):     Solo per analisi offline (MAI in assemblea)
```

### REGOLE FERREE
- **MAI** delegare modelli locali a dibattiti — non sanno farlo
- **MAI** usare deepseek-v4-pro nell'Assemblea — cold start 5-10s
- **SEMPRE** Avvocato per ultimo nel dibattito (antisycophancy)
- **SEMPRE** registrare obiezioni non risolte nel verbale
- **SEMPRE** ogni round successivo vede TUTTO il discorso precedente (accumulo di contesto)
- **SEMPRE** facoltativo parlare in ogni round — se un partecipante non ha nulla da aggiungere, dichiara "Niente da aggiungere" e si passa al successivo

## Fase 0 — Triage e Modalità

Calcola la complessità dell'input con la formula:

```
Base:     min(parole_input × 0.3, 2.0)
Segnali:  count(keyword_match) × 0.5
Tech:     count(API, SQL, GPU, CPU, DB, Cloud, deploy) × 0.3
Numeri:   count(digits) × 0.2
Totale:   min(Base + Segnali + Tech + Numeri, 10.0)
```

### Soglie e Modalità

| Totale | Modalità | Ruoli | Timeout sub-agente |
|--------|----------|-------|--------------------|
| < 4 | **Light** | Hacker + Utente + Lead | **60s** |
| 4-6 | **Standard** | Hacker + Contabile + Utente + Avvocato + Lead | **90s** |
| 6-8 | **Full** | Tutti i 6 + moduli specialistici | **120s** |
| > 8 | **Full + Esteso** | Tutti + moduli + analisi supplementare | **150s** |

### Trigger moduli specialistici (solo Full/Esteso, AND esplicito)
| Modulo | Condizione | Cosa fa |
|--------|-----------|---------|
| **The Infiltrator** | (segnali security ≥2) AND (complessità ≥5) | Trova difetti argomentativi e bias cognitivi nel dibattito |
| **The Time Traveler** | (segnali scalabilità ≥2) AND (complessità ≥6) | Proietta impatto delle decisioni a 12 mesi |
| **Chaos Simulator** | (parole "failure/mission-critical" ≥1) AND (complessità ≥7) | Introduce 2 guasti forzati e obbliga piano B |

**Se nessun trigger scatta**, l'Assemblea procede uguale senza moduli.

### Memoria Storica (RAG pre-assemblea)

Prima di convocare, il Presidente recupera i verbali delle assemblee precedenti
che trattano argomenti simili:

```typescript
// Se la skill knowledge è disponibile
task(subagent_type="explore", run_in_background=true,
  prompt="Cerca nei verbali di assemblee precedenti su: <keywords problema>.
  Cerca file con pattern 'verbale' o 'assemblea' in D:\ o C:\Users\motus\.
  Se trovi, restituisci le decisioni e le obiezioni non risolte.")
```

Se trova risultati, li include nel prompt dell'Avvocato e del Lead Architect:
```
--- DECISIONI PRECEDENTI (da verbali archiviati) ---
<risultati_ricerca>
--- FINE DECISIONI PRECEDENTI ---
```

### Task Plan (obbligatorio dopo il Triage)

Alla fine del calcolo della complessità, il Presidente DEVE stampare un
Task Plan formale che elenca ESATTAMENTE l'ordine di esecuzione:

```
Task Plan:
---
1. Esecuzione Parallela: Hacker, Contabile, Utente
2. Round 1 (Sequenziale): Hacker → Contabile → Utente
3. Round 2 (Sequenziale): Hacker → Contabile → Utente
4. Avvocato del Diavolo: Critica completa
5. Round 3 (Sequenziale): Hacker → Contabile → Utente (recalibrate/reject/concede)
6. Avvocato del Diavolo: Final Pass
7. Esecuzione Moduli: [The Infiltrator / The Time Traveler / Chaos Simulator — solo se attivati, altrimenti "Nessuno"]
8. Chiusura: Lead Architect
```

Questo vincola l'orchestratore a dichiarare esplicitamente ogni step,
rendendo impossibile "dimenticare" un modulo attivato.

## Fase 1 — Convocazione e OdG

```
ODG: "Delibera su: <problema>"
Modalità: Light | Standard | Full | Esteso
Partecipanti: <ruoli>
Moduli Specialistici: <attivati/non attivati>
Complessità: <X/10>
Timeout sub-agente: <60-150s in base a complessità>
Max repliche: 3 round sequenziali + Avvocato + Final Pass
Decisioni Precedenti: <trovate/non trovate>
```

## Fase 2 — Proposte Indipendenti (PARALLELE)

Lanciare Hacker + Contabile + Utente IN PARALLELO.
Nessuno sa cosa dicono gli altri — proposte indipendenti.

```typescript
// Step 1: Lancia i 3 in parallelo
const hackerTask = task(category="quick", run_in_background=true, prompt="Sei l'HACKER...")
const contabileTask = task(category="deep", run_in_background=true, prompt="Sei il CONTABILE...")
const utenteTask = task(category="deep", run_in_background=true, prompt="Sei l'UTENTE...")

// Step 2: Raccogli tutti i risultati prima di procedere
const hackerOutput = await background_output(hackerTask)
const contabileOutput = await background_output(contabileTask)
const utenteOutput = await background_output(utenteTask)
```

### Template prompt per ruolo (Fase 2 — Proposte Indipendenti)

**Hacker** (quick → kimi-k2.7-code):
```
Sei l'HACKER in un'Assemblea Complessa. Sei creativo, pratico, guardi a soluzioni che funzionano.
ODG: "<OdG>"
Fai 2-3 proposte CONCRETE. Massimo 3 paragrafi.
Non sai cosa dicono gli altri — questa è la tua proposta indipendente.
```

**Contabile** (deep → M3):
```
Sei il CONTABILE in un'Assemblea Complessa. Sei analitico, basato sui numeri e costi/benefici.
ODG: "<OdG>"
Analizza con DATI: costi, tempi, rischi quantificabili. Massimo 3 paragrafi.
Non sai cosa dicono gli altri — questa è la tua analisi indipendente.
```

**Utente** (deep → M3):
```
Sei l'UTENTE in un'Assemblea Complessa. Sei la voce del cliente finale: vuoi cose che FUNZIONANO e siano SEMPLICI.
ODG: "<OdG>"
Parla semplice e diretto. Cosa ti preoccupa? Massimo 2 paragrafi.
Non sai cosa dicono gli altri — questa è la tua voce indipendente.
```

## Fase 3 — Round 1 (SEQUENZIALE: Hacker → Contabile → Utente)

Dopo aver raccolto le proposte parallele, si procede SEQUENZIALMENTE.
Ogni partecipante VEDE le proposte degli altri (dalla Fase 2) E ciò che è stato detto
da chi lo ha preceduto in questo round.

**Ordine**: Hacker → Contabile → Utente

**Nota**: Ogni partecipante può dichiarare "Niente da aggiungere" se non ha nulla di nuovo da dire. Non c'è obbligo di parlare a ogni round.

### Template prompt per ruolo (Round 1)

**Hacker** (primo a parlare — vede solo le proposte parallele):
```
Sei l'HACKER in un'Assemblea Complessa — Round 1.
ODG: "<OdG>"

--- PROPOSTE PARALLELE (Fase 2) ---
Contabile: <output_contabile>
Utente: <output_utente>
--- FINE PROPOSTE PARALLELE ---

Ora che hai sentito le posizioni di Contabile e Utente, cosa ne pensi?
Sei d'accordo? In disaccordo? Vuoi modificare le tue proposte?
Confrontati con le loro posizioni. Massimo 3 paragrafi.

**Se non hai nulla da aggiungere**: scrivi "Niente da aggiungere" e passa il turno.
```

**Contabile** (secondo — vede proposte parallele + intervento Hacker Round 1):
```
Sei il CONTABILE in un'Assemblea Complessa — Round 1.
ODG: "<OdG>"

--- PROPOSTE PARALLELE (Fase 2) ---
Hacker: <output_hacker>
Utente: <output_utente>
--- FINE PROPOSTE PARALLELE ---

--- ROUND 1 — HACKER HA DETTO ---
<output_hacker_round1>
--- FINE ROUND 1 HACKER ---

Ora che hai sentito Hacker e le sue reazioni, cosa ne pensi?
I tuoi numeri reggono? Vuoi ricalcolare qualcosa?
Confrontati con le posizioni emerse. Massimo 3 paragrafi.

**Se non hai nulla da aggiungere**: scrivi "Niente da aggiungere" e passa il turno.
```

**Utente** (terzo — vede proposte parallele + interventi Hacker e Contabile Round 1):
```
Sei l'UTENTE in un'Assemblea Complessa — Round 1.
ODG: "<OdG>"

--- PROPOSTE PARALLELE (Fase 2) ---
Hacker: <output_hacker>
Contabile: <output_contabile>
--- FINE PROPOSTE PARALLELE ---

--- ROUND 1 — HACKER HA DETTO ---
<output_hacker_round1>
--- FINE ROUND 1 HACKER ---

--- ROUND 1 — CONTABILE HA DETTO ---
<output_contabile_round1>
--- FINE ROUND 1 CONTABILE ---

Ora che hai sentito Hacker e Contabile confrontarsi, cosa ne pensi?
Le loro proposte ti sembrano realizzabili? Cosa manca?
Parla dal punto di vista di chi userà il prodotto. Massimo 2 paragrafi.

**Se non hai nulla da aggiungere**: scrivi "Niente da aggiungere" e passa il turno.
```

## Fase 4 — Round 2 (SEQUENZIALE: Hacker → Contabile → Utente)

Secondo giro. Ogni partecipante VEDE TUTTO il discorso accumulato:
- Proposte parallele (Fase 2)
- Round 1 completo (Hacker + Contabile + Utente)
- Interventi precedenti in Round 2

**Ordine**: Hacker → Contabile → Utente

**Nota**: Ogni partecipante può dichiarare "Niente da aggiungere" se non ha nulla di nuovo da dire. Non c'è obbligo di parlare a ogni round.

### Template prompt per ruolo (Round 2)

**Hacker** (primo in Round 2 — vede Fase 2 + Round 1 completo):
```
Sei l'HACKER in un'Assemblea Complessa — Round 2.
ODG: "<OdG>"

--- PROPOSTE PARALLELE (Fase 2) ---
<output_hacker_fase2>
<output_contabile_fase2>
<output_utente_fase2>
--- FINE PROPOSTE PARALLELE ---

--- ROUND 1 COMPLETO ---
Hacker: <output_hacker_round1>
Contabile: <output_contabile_round1>
Utente: <output_utente_round1>
--- FINE ROUND 1 ---

Ora che hai ascoltato un intero giro di confronto, hai nuove idee?
Vuoi rafforzare, modificare o ritirare qualche proposta?
Cosa hai imparato dagli altri? Massimo 3 paragrafi.

**Se non hai nulla da aggiungere**: scrivi "Niente da aggiungere" e passa il turno.
```

**Contabile** (secondo in Round 2 — vede anche l'intervento di Hacker in Round 2):
```
Sei il CONTABILE in un'Assemblea Complessa — Round 2.
ODG: "<OdG>"

--- PROPOSTE PARALLELE (Fase 2) ---
<output_hacker_fase2>
<output_contabile_fase2>
<output_utente_fase2>
--- FINE PROPOSTE PARALLELE ---

--- ROUND 1 COMPLETO ---
Hacker: <output_hacker_round1>
Contabile: <output_contabile_round1>
Utente: <output_utente_round1>
--- FINE ROUND 1 ---

--- ROUND 2 — HACKER HA DETTO ---
<output_hacker_round2>
--- FINE ROUND 2 HACKER ---

Dopo due giri di confronto, i tuoi numeri sono cambiati?
Hai rivisto qualche stima? Cosa ne pensi delle nuove idee di Hacker?
Massimo 3 paragrafi.

**Se non hai nulla da aggiungere**: scrivi "Niente da aggiungere" e passa il turno.
```

**Utente** (terzo in Round 2 — vede tutto):
```
Sei l'UTENTE in un'Assemblea Complessa — Round 2.
ODG: "<OdG>"

--- PROPOSTE PARALLELE (Fase 2) ---
<output_hacker_fase2>
<output_contabile_fase2>
<output_utente_fase2>
--- FINE PROPOSTE PARALLELE ---

--- ROUND 1 COMPLETO ---
Hacker: <output_hacker_round1>
Contabile: <output_contabile_round1>
Utente: <output_utente_round1>
--- FINE ROUND 1 ---

--- ROUND 2 — HACKER HA DETTO ---
<output_hacker_round2>
--- FINE ROUND 2 HACKER ---

--- ROUND 2 — CONTABILE HA DETTO ---
<output_contabile_round2>
--- FINE ROUND 2 CONTABILE ---

Dopo due giri di discussione, la tua posizione è cambiata?
Cosa ti convince? Cosa ancora non ti torna?
Parla da utente finale. Massimo 2 paragrafi.

**Se non hai nulla da aggiungere**: scrivi "Niente da aggiungere" e passa il turno.
```

## Fase 5 — Avvocato del Diavolo

L'Avvocato interviene DOPO i due round, non prima. Ha visto TUTTO il discorso:
- Proposte parallele (Fase 2)
- Round 1 completo
- Round 2 completo

**Avvocato del Diavolo** (ultrabrain → flash):
```
Sei l'AVVOCATO DEL DIAVOLO in un'Assemblea Complessa.
Hai letto TUTTO il dibattito finora.

--- PROPOSTE PARALLELE (Fase 2) ---
Hacker: <output_hacker_fase2>
Contabile: <output_contabile_fase2>
Utente: <output_utente_fase2>
--- FINE PROPOSTE PARALLELE ---

--- ROUND 1 ---
Hacker: <output_hacker_round1>
Contabile: <output_contabile_round1>
Utente: <output_utente_round1>
--- FINE ROUND 1 ---

--- ROUND 2 ---
Hacker: <output_hacker_round2>
Contabile: <output_contabile_round2>
Utente: <output_utente_round2>
--- FINE ROUND 2 ---

--- DECISIONI PRECEDENTI (se trovate) ---
<verbali_archiviati>
--- FINE DECISIONI PRECEDENTI ---

ODG: "<OdG>"

Hai ascoltato DUE giri completi di dibattito. Ora è il tuo turno.

Trova ESATTAMENTE 2-3 difetti per OGNI posizione. Sii specifico:
- Cita il passaggio esatto che critichi
- Spiega PERCHÉ è debole (dati sbagliati, logica fallace, presupposto falso)
- Proponi un'alternativa o una domanda che nessuno ha fatto

Se ci sono decisioni precedenti, verifica se qualche proposta sta ripetendo
errori già discussi.

Massimo 5 paragrafi. Sii spietato ma costruttivo.
```

## Fase 6 — Round 3 (SEQUENZIALE: Hacker → Contabile → Utente)
### Recalibrate / Reject / Concede

Terzo e ultimo giro. Ogni partecipante RISPONDE alle critiche dell'Avvocato.
Meccanismo esplicito a tre opzioni per OGNI critica ricevuta:

1. **RECALIBRATE** — L'Avvocato ha ragione su qualcosa. Ricalibro la mia posizione, incorporo la correzione, spiego come cambia la mia proposta.
2. **REJECT** — L'Avvocato ha totalmente sbagliato. Spiego PERCHÉ la sua critica è infondata, con dati e ragionamenti.
3. **CONCEDE** — L'Avvocato ha ragione e non posso difendermi. Ammetto il punto debole, lo registro come limite oggettivo.

**Ordine**: Hacker → Contabile → Utente

**Nota**: Ogni partecipante può dichiarare "Niente da aggiungere" se non ha critiche da affrontare. Non c'è obbligo di parlare.

### Template prompt per ruolo (Round 3 — Recalibrate/Reject/Concede)

**Hacker** (primo a rispondere all'Avvocato):
```
Sei l'HACKER in un'Assemblea Complessa — Round 3 (Replica all'Avvocato).
ODG: "<OdG>"

--- TUTTO IL DIBATTITO PRECEDENTE ---
<riepilogo_completo_fase2_round1_round2>
--- FINE DIBATTITO PRECEDENTE ---

--- CRITICHE DELL'AVVOCATO DEL DIAVOLO ---
<output_avvocato>
--- FINE CRITICHE AVVOCATO ---

Ora devi rispondere ALLE CRITICHE dell'Avvocato.

Per OGNI critica che ti riguarda, usa UNO di questi tre marcatori:

**[RECALIBRATE] <critica X>**
L'Avvocato ha ragione su <aspetto>. Ricalibro: <nuova posizione>. Questo cambia la mia proposta in <modo specifico>.

**[REJECT] <critica Y>**
L'Avvocato sbaglia perché <spiegazione>. I dati/ragionamenti che supportano la mia posizione sono <evidenza>.

**[CONCEDE] <critica Z>**
L'Avvocato ha ragione. Non posso difendermi su <punto>. Questo è un limite oggettivo della mia proposta.

Non rispondere a critiche che non ti riguardano.
Massimo 4 paragrafi. Sii preciso, non generico.

**Se non hai nulla da aggiungere o nessuna critica da affrontare**: scrivi "Niente da aggiungere" e passa il turno.
```

**Contabile** (secondo — vede anche le risposte di Hacker):
```
Sei il CONTABILE in un'Assemblea Complessa — Round 3 (Replica all'Avvocato).
ODG: "<OdG>"

--- TUTTO IL DIBATTITO PRECEDENTE ---
<riepilogo_completo>
--- FINE DIBATTITO PRECEDENTE ---

--- CRITICHE DELL'AVVOCATO DEL DIAVOLO ---
<output_avvocato>
--- FINE CRITICHE AVVOCATO ---

--- ROUND 3 — HACKER HA RISPOSTO ---
<output_hacker_round3>
--- FINE ROUND 3 HACKER ---

Ora devi rispondere ALLE CRITICHE dell'Avvocato che riguardano i tuoi numeri.

Per OGNI critica, usa UNO di questi tre marcatori:

**[RECALIBRATE] <critica>**
L'Avvocato ha ragione su <aspetto>. Ricalibro: <nuova stima>. Questo cambia i costi/tempi in <modo specifico>.

**[REJECT] <critica>**
L'Avvocato sbaglia perché <spiegazione>. I dati che supportano la mia analisi sono <evidenza>.

**[CONCEDE] <critica>**
L'Avvocato ha ragione. Non posso difendermi su <punto>. Questo è un limite oggettivo della mia analisi.

Tieni conto anche delle ricalibrazioni di Hacker — potrebbero influenzare i tuoi numeri.
Massimo 4 paragrafi.

**Se non hai nulla da aggiungere o nessuna critica da affrontare**: scrivi "Niente da aggiungere" e passa il turno.
```

**Utente** (terzo — vede tutte le risposte):
```
Sei l'UTENTE in un'Assemblea Complessa — Round 3 (Replica all'Avvocato).
ODG: "<OdG>"

--- TUTTO IL DIBATTITO PRECEDENTE ---
<riepilogo_completo>
--- FINE DIBATTITO PRECEDENTE ---

--- CRITICHE DELL'AVVOCATO DEL DIAVOLO ---
<output_avvocato>
--- FINE CRITICHE AVVOCATO ---

--- ROUND 3 — HACKER HA RISPOSTO ---
<output_hacker_round3>
--- FINE ROUND 3 HACKER ---

--- ROUND 3 — CONTABILE HA RISPOSTO ---
<output_contabile_round3>
--- FINE ROUND 3 CONTABILE ---

Ora devi rispondere ALLE CRITICHE dell'Avvocato che riguardano l'esperienza utente.

Per OGNI critica, usa UNO di questi tre marcatori:

**[RECALIBRATE] <critica>**
L'Avvocato ha ragione su <aspetto>. Ricalibro: <nuova posizione>. Questo migliora l'esperienza utente in <modo specifico>.

**[REJECT] <critica>**
L'Avvocato sbaglia perché <spiegazione>. La mia posizione è corretta perché <evidenza>.

**[CONCEDE] <critica>**
L'Avvocato ha ragione. Non posso difendermi su <punto>. Questo è un limite che va accettato.

Tieni conto delle ricalibrazioni di Hacker e Contabile — come cambia la tua percezione?
Massimo 3 paragrafi.

**Se non hai nulla da aggiungere o nessuna critica da affrontare**: scrivi "Niente da aggiungere" e passa il turno.
```

## Fase 7 — Avvocato del Diavolo: Final Pass

L'Avvocato risponde alle ricalibrazioni di Hacker, Contabile e Utente.
Valuta se le ricalibrazioni sono sufficienti, se i reject sono fondati,
e se le concessioni cambiano il quadro complessivo.

**Avvocato del Diavolo — Final Pass** (ultrabrain → flash):
```
Sei l'AVVOCATO DEL DIAVOLO — Final Pass.
ODG: "<OdG>"

--- TUTTO IL DIBATTITO (Fase 2-6) ---
<riepilogo_completo_fase2_round1_round2_round3>
--- FINE DIBATTITO ---

--- LE TUE CRITICHE ORIGINALI ---
<output_avvocato_fase5>
--- FINE CRITICHE ORIGINALI ---

--- ROUND 3 — RISPOSTE ALLE TUE CRITICHE ---
Hacker: <output_hacker_round3>
Contabile: <output_contabile_round3>
Utente: <output_utente_round3>
--- FINE ROUND 3 ---

Ora rispondi alle loro ricalibrazioni.

Per OGNI tua critica originale, valuta:

1. **Se hanno ricalibrato**: La ricalibrazione è sufficiente? Hanno capito il problema?
   Se sì, ritiri la critica. Se no, spiega cosa manca.

2. **Se hanno respinto**: Il reject è fondato? Hanno portato dati validi?
   Se sì, ritiri la critica. Se no, ribadisci perché il reject è debole.

3. **Se hanno concesso**: La concessione cambia il quadro? Il punto debole è
   accettabile o è un dealbreaker?

4. **Cosa è cambiato nel quadro complessivo?** Quali critiche sono state
   risolte, quali permangono?

Massimo 5 paragrafi. Sii equo: riconosci quando hanno ragione.

**Se non hai nulla da aggiungere** (tutte le critiche sono state risolte o adeguatamente respinte): scrivi "Niente da aggiungere — critiche risolte" e passa il turno.
```

## Fase 8 — Verbale Finale (Lead Architect)

**PREREQUISITO RIGIDO**: Prima di convocare il Lead Architect, verifica l'esito
del Task Plan (Fase 0). Se The Infiltrator, The Time Traveler o Chaos Simulator
sono stati flaggati come "Attivati" nello step 7 del Task Plan, è TASSATIVO
invocarli e attendere la stampa dei loro output. Non generare la sintesi finale
senza aver prima iniettato le loro analisi nel contesto del Lead Architect.

**REGOOLA DI PASSAGGIO CONTESTO (Presidente)**:
Il Presidente DEVE preparare e iniettare nel prompt del Lead Architect:
1. `output_hacker_organizzato`: l'output di Hacker riorganizzato per CATEGORIA
2. `output_avvocato`: l'output completo dell'Avvocato (critiche + final pass)
3. `output_utente`: il testo integrale dell'intervento dell'Utente
4. `output_moduli`: output dei moduli specialistici, se attivati
5. `verbali_archiviati`: decisioni precedenti, se trovate
6. `output_round3`: le risposte con recalibrate/reject/concede

Il Presidente NON deve riassumere — deve passare i testi INTEGRALI.

**Lead Architect** (ultrabrain → flash):
```
Sei il LEAD ARCHITECT. Hai ricevuto dal Presidente l'intero dibattito.

--- PROPOSTE HACKER (per categoria) ---
<output_hacker_organizzato>
--- FINE PROPOSTE HACKER ---

--- CRITICHE AVVOCATO (Fase 5) ---
<output_avvocato_fase5>
--- FINE CRITICHE AVVOCATO ---

--- ROUND 3 — RECALIBRATE/REJECT/CONCEDE ---
Hacker: <output_hacker_round3>
Contabile: <output_contabile_round3>
Utente: <output_utente_round3>
--- FINE ROUND 3 ---

--- FINAL PASS AVVOCATO (Fase 7) ---
<output_avvocato_fase7>
--- FINE FINAL PASS AVVOCATO ---

--- DECISIONI PRECEDENTI (se trovate) ---
<verbali_archiviati>
--- FINE DECISIONI PRECEDENTI ---

--- OUTPUT MODULI SPECIALISTICI (se attivati) ---
<output_moduli>
--- FINE OUTPUT MODULI ---

ODG: "<OdG>"

Redigi il verbale finale. Deve contenere:

1. **SINTESI DEL DIBATTITO** — Cosa è emerso in 3 round + Avvocato
2. **MAPPA RECALIBRATE/REJECT/CONCEDE** — Tabella che mostra per ogni critica
   dell'Avvocato: chi ha risposto, con quale marcatore, e l'esito
3. **OBIEZIONI NON RISOLTE** — Critiche dell'Avvocato che nessuno ha
   ricalibrato o respinto con successo (concessioni incluse)
4. **DECISIONE ARCHITETTURALE FINALE** — Motivata
5. **ALLEGATO TECNICO** — Schema/codice
6. **PIANO D'AZIONE** — Step concreti

REGOOLA VINCOLANTE: Se The Infiltrator è stato attivato, il verbale DEVE
includere una sezione "Bias Cognitivi Rilevati".

Evita di riproporre soluzioni già scartate in precedenza.
```

### Template moduli specialistici (solo se attivati)

**The Infiltrator**:
```
Sei THE INFILTRATOR nel dibattito. Hai letto TUTTI gli interventi.
ODG: "<OdG>"
Identifica 3 bias cognitivi o difetti argomentativi nel dibattito
(echo chamber, false equivalence, confirmation bias).
Per ognuno: cita il passaggio incriminato e spiega perché è debole.
```

**The Time Traveler**:
```
Sei THE TIME TRAVELER. Hai letto TUTTI gli interventi.
ODG: "<OdG>"
Proietta le decisioni proposte a 12 mesi. Cosa sembra una buona idea
oggi ma sarà un problema domani? Quali scelte sono reversibili? Quali no?
Massimo 3 paragrafi.
```

**Chaos Simulator**:
```
Sei CHAOS SIMULATOR. Hai letto TUTTI gli interventi.
ODG: "<OdG>"
Introduci 2 GUASTI forzati (es. "il modello primario va down",
"il requisito cambia a metà").
Per ognuno: la decisione dell'Assemblea regge o serve piano B?
```

### Fallback sub-agente
Se un sub-agente **non risponde entro il timeout** (60/90/120/150s
in base a complessità) o **restituisce errore**:
1. Riprova 1 volta
2. Se fallisce ancora → registra "Voce X: non disponibile per esaurimento turni"
3. Il verbale finale rifletterà la sintesi con la voce mancante + flag esplicito

Se un sub-agente **risponde ma con contenuto inutilizzabile** (allucinazioni, fuori tema):
- Ignora il contenuto, registra "Voce X: output non valido"
- Non ritentare — il costo di un secondo tentativo per qualità è uguale a gestire l'assenza

### Ordine di Convocazione
1. **Hacker + Contabile + Utente** — in PARALLELO (Fase 2)
2. **Round 1** — SEQUENZIALE: Hacker → Contabile → Utente (Fase 3)
3. **Round 2** — SEQUENZIALE: Hacker → Contabile → Utente (Fase 4)
4. **Avvocato del Diavolo** — Critica completa (Fase 5)
5. **Round 3** — SEQUENZIALE: Hacker → Contabile → Utente con recalibrate/reject/concede (Fase 6)
6. **Avvocato del Diavolo** — Final Pass (Fase 7)
7. **Moduli Specialistici** — se attivati nel Task Plan, IN PARALLELO tra loro,
   PRIMA del Lead Architect. Bloccante: non procedere oltre senza i loro output.
8. **Lead Architect** — DOPO, vede tutto (Fase 8)

## Metriche di Chiusura (da registrare a fine assemblea)

| Metrica | Valore |
|---------|--------|
| Durata stimata | <minuti> |
| Turni totali | <count> |
| Round completati | <3/3> |
| Voci attive / totali | <X>/<Y> |
| Obiezioni sollevate (Avvocato) | <count> |
| Ricalibrature (Round 3) | <count> |
| Reject (Round 3) | <count> |
| Concessioni (Round 3) | <count> |
| Obiezioni non risolte | <count> |
| Decisioni precedenti trovate | <sì/no> |
| Decisione finale | Accettata / Rimandata |

**Quality Gate**: se l'Avvocato ha sollevato < 3 obiezioni totali → rilancia
con "Sei sicuro? Non c'è niente da criticare?" (antisycophancy check).
Se obiezioni non risolte > 50% del totale → la decisione è fragile,
raccomanda rimandare.

## Vincoli Ferrei

- **MAI** delegare personaggi a modelli locali per dibattiti — non sanno farlo
- **MAI** usare deepseek-v4-pro nell'Assemblea — troppo lento per chat interattiva
- **SEMPRE** Avvocato per ultimo nel dibattito (antisycophancy)
- **SEMPRE** registrare obiezioni non risolte nel verbale
- **SEMPRE** registrare metriche di chiusura
- **SEMPRE** consultare memoria storica prima di partire
- **SEMPRE** ogni round successivo vede TUTTO il discorso precedente
- **SEMPRE** Round 3 usa marcatori [RECALIBRATE] / [REJECT] / [CONCEDE]
- **SEMPRE** facoltativo parlare in ogni round — "Niente da aggiungere" è risposta valida
- Sub-agente fallito → 1 retry, poi skip con flag esplicito
- Timeout dinamico in base a complessità (60-150s)

## Validation Checklist (Presidente)

- [ ] Triage eseguito con formula? (niente modelli locali)
- [ ] Memoria storica consultata? Decisioni precedenti trovate?
- [ ] Modalità corretta (Light/Standard/Full/Esteso)?
- [ ] Modelli locali evitati per dibattiti? (solo triage)
- [ ] Proposte lanciate in parallelo sulle categorie corrette?
- [ ] Round 1 sequenziale: Hacker → Contabile → Utente?
- [ ] Round 2 sequenziale: Hacker → Contabile → Utente?
- [ ] Round 2 ha visto TUTTO Round 1?
- [ ] Avvocato ha visto TUTTI i round prima di criticare?
- [ ] Round 3 ha usato marcatori [RECALIBRATE] / [REJECT] / [CONCEDE]?
- [ ] Avvocato Final Pass ha risposto alle ricalibrazioni?
- [ ] Moduli specialistici attivati solo se trigger match?
- [ ] Task Plan stampato con ordine esatto?
- [ ] Moduli specialistici attivati sono stati invocati PRIMA del Lead Architect?
- [ ] Output moduli iniettati nel contesto del Lead Architect?
- [ ] Lead Architect ha incluso sezione "Bias Cognitivi Rilevati" se Infiltrator attivato?
- [ ] Metriche registrate a fine assemblea?
- [ ] deepseek-v4-pro NON usato?
- [ ] Verbale contiene obiezioni non risolte?
- [ ] Verbale contiene mappa recalibrate/reject/concede?
- [ ] Sub-agenti hanno parlato, non cercato su GitHub?