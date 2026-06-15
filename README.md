# opencode-skill-assemblea-complessa

**Assemblea Complessa V1 — Deep Multi-Round Deliberation Engine**

Multi-agente per dibattiti **profondi e strutturati** su OpenCode, con 3 round sequenziali, meccanismo **Recalibrate/Reject/Concede**, Avvocato Final Pass, e verbale con mappa RRC. Pensata per problemi complessi che richiedono iterazione e maturazione graduale delle posizioni.

> Rispetto all'[Assemblea standard](https://github.com/motusakapeppo/opencode-skill-assemblea), questa variante ha 3 round invece di 2, un meccanismo strutturato di risposta alle critiche, e un Final Pass dell'Avvocato. Più potente, ma più lunga.

---

## Indice

- [Quick Start](#quick-start)
- [Differenze dall'Assemblea Standard](#differenze-dallassemblea-standard)
- [Il Cast](#il-cast)
- [Meccanismo Recalibrate/Reject/Concede](#meccanismo-recalibraterejectconcede)
- [Flusso di Esecuzione](#flusso-di-esecuzione-8-fasi)
- [Triage e Modalità](#triage-e-modalità)
- [Moduli Specialistici](#moduli-specialistici)
- [Metriche di Chiusura](#metriche-di-chiusura)
- [Quando Usare Quale Assemblea](#quando-usare-quale-assemblea)
- [Esempi](#esempi)
- [Fallback Python](#fallback-python)
- [Requisiti](#requisiti)
- [Limitazioni](#limitazioni)

---

## Quick Start

Invocazione su OpenCode (OhMyOpenCode):

```
Assemblea complessa: dobbiamo riscrivere da zero il sistema di trading
o fare refactoring incrementale? Budget 6 mesi, 3 dev, rischio downtime.
```
```
Dibattito approfondito: Kafka o RabbitMQ per il nuovo sistema di eventi?
Abbiamo esperienza RabbitMQ ma Kafka sembra più scalabile.
```
```
Assemblea complessa su: strategia di migrazione da monolite a microservizi.
30 servizi, 5 team, deadline 18 mesi.
```

L'Assemblea Complessa esegue 8 fasi: proposte parallele → Round 1 → Round 2 → Avvocato → Round 3 (RRC) → Final Pass → Moduli → Verbale.

---

## Differenze dall'Assemblea Standard

| Caratteristica | Assemblea (standard) | Assemblea Complessa |
|---------------|---------------------|---------------------|
| Round di dibattito | 2 giri + controreplica Avvocato | **3 round sequenziali** |
| Avvocato del Diavolo | Dopo le proposte parallele | Dopo **Round 2** (ha visto 2 round di confronto) |
| Meccanismo di risposta | Replica libera | **[RECALIBRATE] / [REJECT] / [CONCEDE]** strutturato |
| Final Pass Avvocato | Solo controreplica | **Final Pass** dedicato che valuta le ricalibrazioni |
| Verbale | Sintesi standard | Include **Mappa Recalibrate/Reject/Concede** |
| Opt-out facoltativo | Non previsto | "Niente da aggiungere" permesso a ogni round |
| Durata stimata | 60-150s | **2-5 minuti** (più lungo, più approfondito) |
| Modalità Esplorazione | ✅ | ❌ (sempre convergente) |

---

## Il Cast

| Ruolo | Modello | Categoria | Competenza |
|-------|---------|-----------|------------|
| **Presidente** | deepseek-v4-flash | — | Moderatore, orchestra il dibattito |
| **L'Hacker** | kimi-k2.7-code | `quick` | Proposte concrete, coding |
| **Il Contabile** | minimax-m3 | `deep` | Numeri, costi, ROI |
| **L'Utente** | minimax-m3 | `deep` | Voce del cliente, semplicità |
| **L'Avvocato del Diavolo** | deepseek-v4-flash | `ultrabrain` | Critica puntuale, anti-sycophancy |
| **Lead Architect** | deepseek-v4-flash | `ultrabrain` | Sintesi finale e verbale |

---

## Meccanismo Recalibrate/Reject/Concede

Il cuore dell'Assemblea Complessa. Al Round 3, ogni partecipante risponde alle critiche dell'Avvocato con **marcatori espliciti**:

| Marcatore | Significato | Impatto sul Verbale |
|-----------|------------|---------------------|
| `[RECALIBRATE]` | L'Avvocato ha ragione, ricalibro la mia posizione | Proposta evolve positivamente, critica potenzialmente risolta |
| `[REJECT]` | L'Avvocato sbaglia, porto dati a sostegno | Posizione si rafforza, critica respinta |
| `[CONCEDE]` | L'Avvocato ha ragione, non posso difendermi | Limite oggettivo registrato, critica non risolta |

L'Avvocato nel **Final Pass** (Fase 7) valuta ogni risposta:
- **Ricalibrate sufficiente?** → Ritira la critica
- **Reject fondato?** → Ritira o ribadisce
- **Concessione cambia il quadro?** → Decide se è dealbreaker

La **Mappa RRC** nel verbale finale documenta ogni critica, la risposta, e l'esito.

---

## Flusso di Esecuzione (8 Fasi)

```
Triage → Calcolo Complessità → Selezione Modalità
    ↓
Convocazione (OdG + Task Plan)
    ↓
  FASE 2: Hacker + Contabile + Utente (PARALLELO — proposte indipendenti)
    ↓
  FASE 3: Round 1 (SEQUENZIALE: Hacker → Contabile → Utente)
         Ogni partecipante vede le proposte parallele degli altri
    ↓
  FASE 4: Round 2 (SEQUENZIALE: Hacker → Contabile → Utente)
         Ogni partecipante vede Round 1 completo + interventi Round 2
    ↓
  FASE 5: Avvocato del Diavolo (critica completa su TUTTO il dibattito)
         Cita passaggi esatti, 2-3 difetti per posizione
    ↓
  FASE 6: Round 3 (SEQUENZIALE: Recalibrate/Reject/Concede)
         Risposta strutturata alle critiche
    ↓
  FASE 7: Avvocato Final Pass (valuta le ricalibrazioni)
         Decide se ritirare o mantenere ogni critica
    ↓
  FASE 8: Lead Architect → Verbale Finale con mappa RRC
```

### Regole Chiave

- **Accumulo di contesto**: ogni round successivo vede TUTTO il discorso precedente
- **Opt-out facoltativo**: "Niente da aggiungere" è risposta valida a ogni round
- **Avvocato sempre ultimo**: prima a criticare (Fase 5), ultimo a parlare (Fase 7)

---

## Triage e Modalità

### Formula di Complessità

```
Base:     min(parole_input × 0.3, 2.0)
Segnali:  count(keyword_match) × 0.5
Tech:     count(API, SQL, GPU, CPU, DB, Cloud, deploy) × 0.3
Numeri:   count(digits) × 0.2
Totale:   min(Base + Segnali + Tech + Numeri, 10.0)
```

### Soglie

| Punteggio | Modalità | Partecipanti | Timeout |
|-----------|----------|-------------|---------|
| < 4 | **Light** | Hacker + Utente + Lead | 60s |
| 4-6 | **Standard** | Hacker + Contabile + Utente + Avvocato + Lead | 90s |
| 6-8 | **Full** | Tutti e 6 + moduli specialistici | 120s |
| > 8 | **Full + Esteso** | Tutti + moduli + analisi supplementare | 150s |

> L'Assemblea Complessa **non include** la Modalità Esplorazione — è sempre convergente e strutturata.

---

## Moduli Specialistici

| Modulo | Trigger | Funzione |
|--------|---------|----------|
| **The Infiltrator** | ≥ 2 segnali security E complessità ≥ 5 | Identifica 3 bias cognitivi o difetti argomentativi nel dibattito |
| **The Time Traveler** | ≥ 2 segnali scalabilità E complessità ≥ 6 | Proietta l'impatto delle decisioni a 12-24 mesi |
| **Chaos Simulator** | "failure/mission-critical" E complessità ≥ 7 | Introduce 2 guasti forzati e obbliga piano B |

---

## Metriche di Chiusura

| Metrica | Descrizione |
|---------|-------------|
| Durata stimata | Tempo totale in minuti |
| Turni totali | Numero di interventi |
| Round completati | 3/3 |
| Voci attive / totali | Partecipanti che hanno parlato |
| Obiezioni sollevate | Critiche dell'Avvocato |
| Ricalibrature | `[RECALIBRATE]` nel Round 3 |
| Reject | `[REJECT]` nel Round 3 |
| Concessioni | `[CONCEDE]` nel Round 3 |
| Obiezioni non risolte | Critiche rimaste senza risposta adeguata |
| Decisione finale | Accettata / Rimandata |

**Quality Gate**: se l'Avvocato solleva < 3 obiezioni → anti-sycophancy check. Obiezioni non risolte > 50% → decisione fragile, rimandare.

---

## Quando Usare Quale Assemblea

| Scenario | Assemblea V5 | Assemblea Complessa |
|----------|-------------|---------------------|
| Decisione rapida (< 2 minuti) | ✅ | ❌ |
| Problema con dati numerici precisi | ✅ | ✅ |
| Brainstorming creativo | ✅ (modalità Esplorazione) | ❌ |
| Scelta controversa con opinioni divergenti | ❌ | ✅ |
| Decisione con rischio alto | ❌ | ✅ |
| Piano di migrazione complesso | ❌ | ✅ |
| Tracciabilità delle decisioni | ❌ | ✅ (mappa RRC) |
| Team diviso su una scelta | ❌ | ✅ |

**Regola pratica**: se pensi "questa decisione merita più di 2 minuti di discussione", usa l'Assemblea Complessa.

---

## Esempi

### Esempio 1: Decisione Architetturale Critica (Full)

```
Utente: "Assemblea complessa: dobbiamo decidere se riscrivere da zero
il sistema di trading o fare refactoring incrementale. Budget: 6 mesi,
3 sviluppatori, rischio di downtime durante la migrazione."

Output: 3 round di discussione, Avvocato critica ogni posizione,
Round 3 con recalibrate/reject/concede, verbale finale con mappa RRC.
```

### Esempio 2: Scelta Tecnologica Controversa (Standard)

```
Utente: "Dibattito approfondito: usiamo Kafka o RabbitMQ per il nuovo
sistema di eventi? Abbiamo già esperienza con RabbitMQ ma Kafka
sembra più scalabile."

Output: Proposte parallele, 2 round di confronto, critica Avvocato,
ricalibrazione finale, decisione con mapping rischi/benefici.
```

### Esempio 3: Piano di Migrazione (Full + Esteso)

```
Utente: "Assemblea complessa su: strategia di migrazione da
monolite a microservizi. 30 servizi, 5 team, deadline 18 mesi.
Possibili rotture: API breaking changes, DB sharding, auth centralizzato."

Output: Chaos Simulator attivato, 2 guasti forzati introdotti,
piani B discussi, verbale completo con bias cognitivi rilevati.
```

---

## Fallback Python

`debate_orchestrator.py` è uno script Python standalone per ambienti **senza OpenCode**. Supporta l'opt-out ("Niente da aggiungere") e la struttura a 8 fasi.

```bash
# Prerequisito
export OLLAMA_API_KEY="la-tua-chiave"

# Uso base
python debate_orchestrator.py "Riscrittura sistema di caching: Redis Cluster vs Dragonfly"

# Con timeout personalizzato
python debate_orchestrator.py "Refactoring modulo pagamenti" --timeout 90

# Con contesto di codice
python debate_orchestrator.py "Analisi architettura pagamenti" --code src/payments/service.py
```

---

## Struttura del Repository

```
opencode-skill-assemblea-complessa/
├── README.md                               # Documentazione
├── SKILL.md                                # Skill definition OpenCode
├── debate_orchestrator.py                  # Fallback Python standalone
└── .gitignore
```

---

## Requisiti

- **OpenCode** (OhMyOpenCode) — per l'uso principale via sub-agenti cloud
- **Python 3.10+** — solo per il fallback standalone
- **Variabile d'ambiente** `OLLAMA_API_KEY` — solo per il fallback standalone
- **Modelli cloud**: kimi-k2.7-code, minimax-m3, deepseek-v4-flash

---

## Limitazioni

1. **Fallback Python sequenziale** — le proposte parallele girano in sequenza. 3-4× più lento dell'esecuzione OpenCode nativa.
2. **Nessuna Modalità Esplorazione** — l'Assemblea Complessa è sempre convergente e strutturata.
3. **deepseek-v4-pro escluso** — cold start 5-10s, non adatto a chat interattive.
4. **Niente modelli locali** — i modelli locali non producono dibattiti di qualità. Usare solo cloud.

---

## Licenza

Apache 2.0