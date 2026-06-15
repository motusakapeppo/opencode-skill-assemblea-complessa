# opencode-skill-assemblea-complessa

**Assemblea Complessa V1 — Deep Multi-Round Deliberation Engine**

Un sistema multi-agente per dibattiti **profondi e strutturati** tra modelli AI, con 3 round sequenziali, critica dell'Avvocato del Diavolo, meccanismo Recalibrate/Reject/Concede, e Final Pass. Rispetto all'Assemblea standard ("assemblea"), questa variante è pensata per problemi complessi che richiedono **iterazione e maturazione graduale delle posizioni**.

> Questa skill è **nativamente pensata per OpenCode**: il metodo principale d'esecuzione è via sub-agenti cloud. Lo script Python `debate_orchestrator.py` è un **fallback** per ambienti senza OpenCode.

---

## Differenze Rispetto all'Assemblea Standard

| Caratteristica | Assemblea (standard) | Assemblea Complessa |
|---------------|---------------------|---------------------|
| Round di dibattito | 2 giri + controreplica Avvocato | **3 round sequenziali** |
| Avvocato del Diavolo | Dopo le proposte parallele | Dopo **Round 2** (ha visto 2 round di confronto) |
| Meccanismo di risposta | Replica libera | **[RECALIBRATE] / [REJECT] / [CONCEDE]** strutturato |
| Final Pass Avvocato | Solo controreplica | **Final Pass** dedicato che valuta le ricalibrazioni |
| Verbale | Sintesi standard | Include **Mappa Recalibrate/Reject/Concede** |
| Opt-out facoltativo | Non previsto | "Niente da aggiungere" permesso a ogni round |
| Durata stimata | 60-150s | **2-5 minuti** (più lungo, ma più approfondito) |

---

## Architettura

### Il Cast

| Ruolo | Modello | Categoria | Competenza |
|-------|---------|-----------|------------|
| **Presidente** | deepseek-v4-flash | — | Moderatore, orchestra il dibattito |
| **L'Hacker** | kimi-k2.7-code | `quick` | Proposte concrete, coding |
| **Il Contabile** | minimax-m3 | `deep` | Numeri, costi, ROI |
| **L'Utente** | minimax-m3 | `deep` | Voce del cliente, semplicità |
| **L'Avvocato del Diavolo** | deepseek-v4-flash | `ultrabrain` | Critica puntuale, anti-sycophancy |
| **Lead Architect** | deepseek-v4-flash | `ultrabrain` | Sintesi finale e verbale |

### Flusso di Esecuzione (8 Fasi)

```
Triage → Calcolo Complessità → Selezione Modalità
    ↓
Convocazione (OdG + Task Plan)
    ↓
FASE 2: Hacker + Contabile + Utente (PARALLELO — proposte indipendenti)
    ↓
FASE 3: Round 1 (SEQUENZIALE: Hacker → Contabile → Utente)
    ↓
FASE 4: Round 2 (SEQUENZIALE: Hacker → Contabile → Utente)
    ↓
FASE 5: Avvocato del Diavolo (critica completa su TUTTO il dibattito)
    ↓
FASE 6: Round 3 (SEQUENZIALE: Recalibrate/Reject/Concede)
    ↓
FASE 7: Avvocato Final Pass (valuta le risposte)
    ↓
FASE 8: Lead Architect → Verbale Finale con mappa RRC
```

---

## Meccanismo Recalibrate/Reject/Concede

Il cuore dell'Assemblea Complessa. Al Round 3, ogni partecipante risponde alle critiche dell'Avvocato con **marcatori espliciti**:

| Marcatore | Significato | Impatto |
|-----------|------------|---------|
| `[RECALIBRATE]` | L'Avvocato ha ragione, ricalibro la mia posizione | La proposta evolve positivamente |
| `[REJECT]` | L'Avvocato sbaglia, porto dati a sostegno | La posizione si rafforza |
| `[CONCEDE]` | L'Avvocato ha ragione, non posso difendermi | Limite oggettivo registrato nel verbale |

L'Avvocato nel Final Pass valuta ogni risposta e decide se ritirare la critica o mantenerla.

---

## Triage e Modalità

Formula di complessità identica all'Assemblea standard:

```
Base:     min(parole_input × 0.3, 2.0)
Segnali:  count(keyword_match) × 0.5
Tech:     count(API, SQL, GPU, CPU, DB, Cloud, deploy) × 0.3
Numeri:   count(digits) × 0.2
Totale:   min(Base + Segnali + Tech + Numeri, 10.0)
```

### Soglie

| Punteggio | Modalità | Partecipanti |
|-----------|----------|-------------|
| < 4 | **Light** | Hacker + Utente + Lead |
| 4-6 | **Standard** | 5 personaggi |
| 6-8 | **Full** | 6 + moduli specialistici |
| > 8 | **Full + Esteso** | 6 + moduli + analisi supplementare |

**Nota:** L'Assemblea Complessa non include la Modalità Esplorazione (divergente) — è sempre convergente e strutturata.

---

## Moduli Specialistici

| Modulo | Trigger | Funzione |
|--------|---------|----------|
| **The Infiltrator** | Security ≥ 2 + complessità ≥ 5 | Trova bias cognitivi e difetti argomentativi |
| **The Time Traveler** | Scalabilità ≥ 2 + complessità ≥ 6 | Proietta impatto decisioni a 12-24 mesi |
| **Chaos Simulator** | "failure/mission-critical" + complessità ≥ 7 | Introduce 2 guasti forzati, obbliga piano B |

---

## Esempi d'Uso

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

Output: Prop往来 parallele, 2 round di confronto, critica Avvocato,
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

`debate_orchestrator.py` è uno script Python standalone che esegue l'Assemblea Complessa via chiamate dirette all'API cloud (senza OpenCode).

```bash
# Prerequisito: impostare la variabile d'ambiente
export OLLAMA_API_KEY="la-tua-chiave"

# Esecuzione
python debate_orchestrator.py "Riscrittura sistema di caching: Redis Cluster vs Dragonfly" --timeout 90

# Con contesto di codice
python debate_orchestrator.py "Refactoring modulo pagamenti" --code src/payments/service.py
```

---

## Quando Usare Quale Assemblea

| Scenario | Usa Assemblea | Usa Assemblea Complessa |
|----------|---------------|------------------------|
| Decisione rapida (< 5 minuti) | ✅ | ❌ |
| Problema con dati numerici precisi | ✅ | ✅ |
| Scelta controversa con team diviso | ❌ | ✅ |
| Esplorazione creativa (brainstorming) | ✅ (modalità Esplorazione) | ❌ |
| Decisione con rischio alto | ❌ | ✅ |
| Piano di migrazione complesso | ❌ | ✅ |
| Necessità di tracciabilità delle decisioni | ❌ | ✅ (mappa RRC) |

---

## Requisiti

- **Python 3.10+** (per il fallback)
- **OpenCode** (OhMyOpenCode) con configurazione cloud per l'uso principale
- **Variabile d'ambiente** `OLLAMA_API_KEY` per il fallback Python
- Modelli cloud accessibili: kimi-k2.7-code, minimax-m3, deepseek-v4-flash

---

## Struttura del Repository

```
opencode-skill-assemblea-complessa/
├── README.md                          # Questo file
├── SKILL.md                           # Skill definition completa (724 righe)
├── debate_orchestrator.py             # Fallback Python (standalone)
└── .gitignore
```

---

## Limitazioni Note

1. Il fallback Python è **sequenziale**, non parallelo
2. Il fallback Python supporta l'opt-out ("Niente da aggiungere") ma non la piena efficienza del parallelismo nativo OpenCode
3. deepseek-v4-pro è esplicitamente bandito (cold start troppo lento)
4. I modelli locali non supportano dibattiti di qualità

---

## Licenza

Apache 2.0