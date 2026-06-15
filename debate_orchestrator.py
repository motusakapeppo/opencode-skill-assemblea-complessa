"""
ASSEMBLEA COMPLESSA V1 — Deep Multi-Round Deliberation Engine (Fallback)
=======================================================================
ATTENZIONE: Questo script Python e' un FALLBACK.
Il metodo PRINCIPALE per l'Assemblea Complessa e' via sub-agenti cloud su OpenCode.

Usa questo script SOLO se non puoi lanciare agenti su cloud.
I modelli locali SONO LENTI per dibattiti (1/5 della velocita cloud).

PREREQUISITO: Impostare la variabile d'ambiente OLLAMA_API_KEY.

FLOW:
1. Triage (complessita)
2. Proposte Parallele: Hacker + Contabile + Utente
3. Round 1 (Sequenziale): Hacker -> Contabile -> Utente
4. Round 2 (Sequenziale): Hacker -> Contabile -> Utente
5. Avvocato del Diavolo: Critica completa
6. Round 3 (Sequenziale): Hacker -> Contabile -> Utente (recalibrate/reject/concede)
7. Avvocato del Diavolo: Final Pass
8. Lead Architect: Verbale Finale
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error
import time
import re

# USARE IL CLOUD, non modelli locali
CLOUD_API_URL = "https://ollama.com/v1/chat/completions"
CLOUD_API_KEY = os.environ.get("OLLAMA_API_KEY")
if not CLOUD_API_KEY:
    print(
        "ERRORE: Imposta la variabile d'ambiente OLLAMA_API_KEY.",
        file=sys.stderr,
    )
    sys.exit(1)

CLOUD_MODEL = "deepseek-v4-flash"  # MAI usare v4-pro (troppo lento per chat)

# Segnali per triage
SIGNALS = {
    "security": {
        "keywords": [
            "api",
            "login",
            "password",
            "database",
            "auth",
            "token",
            "crypt",
            "gdpr",
            "privacy",
            "encrypt",
            "hash",
            "injection",
            "xss",
            "csrf",
            "oauth",
            "jwt",
        ],
        "module": "The Infiltrator",
        "min_complexity": 4,
    },
    "future": {
        "keywords": [
            "migraz",
            "scalabil",
            "architettur",
            "cloud",
            "microservizi",
            "deploy",
            "kubernetes",
            "docker",
            "serverless",
            "caching",
        ],
        "module": "The Time Traveler",
        "min_complexity": 5,
    },
    "chaos": {
        "keywords": [
            "runtime",
            "mission critical",
            "production",
            "failover",
            "disaster recovery",
            "uptime",
            "sla",
            "high availability",
            "outage",
            "downtime",
        ],
        "module": "Chaos Simulator",
        "min_complexity": 6,
    },
}


def calculate_complexity(topic: str) -> float:
    words = len(topic.split())
    complexity = min(words * 0.5, 3.0)
    all_keywords = set()
    for s in SIGNALS.values():
        all_keywords.update(s["keywords"])
    signal_matches = sum(1 for kw in all_keywords if kw.lower() in topic.lower())
    complexity += signal_matches * 0.8
    tech_keywords = len(
        re.findall(
            r"\b(API|SQL|NoSQL|REST|gRPC|HTTP|TCP|GPU|CPU|RAM|DB|VM|AWS|GCP|Azure|Crypto|Blockchain|Microservizi|Kubernetes|Docker)\b",
            topic,
            re.IGNORECASE,
        )
    )
    complexity += tech_keywords * 0.5
    numbers = len(re.findall(r"\d+", topic))
    complexity += numbers * 0.3
    return min(round(complexity, 1), 10.0)


def detect_signals(topic: str) -> list:
    active = []
    topic_lower = topic.lower()
    for signal_name, signal_config in SIGNALS.items():
        for kw in signal_config["keywords"]:
            if kw.lower() in topic_lower:
                active.append(signal_name)
                break
    return active


def get_cast(complexity: float) -> list:
    if complexity < 4:
        return ["Hacker (Flash cloud)", "Utente (Flash cloud)"]
    elif complexity <= 6:
        return [
            "Hacker (Flash cloud)",
            "Contabile (Flash cloud)",
            "Utente (Flash cloud)",
            "Avvocato del Diavolo (Flash cloud)",
        ]
    else:
        return [
            "Hacker (Flash cloud)",
            "Contabile (Flash cloud)",
            "Utente (Flash cloud)",
            "Avvocato del Diavolo (Flash cloud)",
            "Lead Architect (Flash cloud)",
        ]


def chat(model: str, prompt: str, max_tokens: int = 1500, timeout: int = 60) -> str:
    """Invia richiesta al cloud Ollama (deepseek-v4-flash)."""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": max_tokens},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        CLOUD_API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {CLOUD_API_KEY}",
        },
        method="POST",
    )
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed = time.time() - start
            result = json.loads(resp.read().decode("utf-8"))
            print(f"    [OK cloud in {elapsed:.1f}s]", file=sys.stderr)
            return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        elapsed = time.time() - start
        print(f"    [FAIL dopo {elapsed:.1f}s: {e}]", file=sys.stderr)
        raise


def call_role(role: str, prompt: str, timeout: int = 60) -> str:
    """Chiama un ruolo e gestisce l'opt-out."""
    result = chat(CLOUD_MODEL, prompt, timeout=timeout)
    # Se il risultato contiene "Niente da aggiungere", lo registra come opt-out
    if "niente da aggiungere" in result.lower():
        print(f"    [{role}] Niente da aggiungere (opt-out)", file=sys.stderr)
    return result


def main():
    print("=" * 70, file=sys.stderr)
    print(
        " [*] ASSEMBLEA COMPLESSA V1 — FALLBACK (via cloud deepseek-v4-flash)",
        file=sys.stderr,
    )
    print(
        " [*] ATTENZIONE: Il metodo PRINCIPALE e' via sub-agenti OpenCode su cloud.",
        file=sys.stderr,
    )
    print(" [*] Questo script e' un fallback piu lento.", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    parser = argparse.ArgumentParser(description="Assemblea Complessa V1 (Fallback)")
    parser.add_argument("topic", type=str, help="Il problema da risolvere")
    parser.add_argument(
        "--timeout", type=int, default=60, help="Timeout per chiamata (sec)"
    )
    parser.add_argument(
        "--code", type=str, default=None, help="File di codice per context-slimming"
    )
    args = parser.parse_args()
    topic = args.topic
    timeout = args.timeout

    code_context = ""
    if args.code and os.path.exists(args.code):
        with open(args.code, "r", encoding="utf-8") as f:
            lines = f.readlines()
        code_context = "\n".join(
            line
            for line in lines
            if any(
                line.strip().startswith(p)
                for p in [
                    "def ",
                    "class ",
                    "struct ",
                    "import ",
                    "from ",
                    "fn ",
                    "pub ",
                    "func ",
                ]
            )
        )[:3000]

    full_topic = topic
    if code_context:
        full_topic += f"\n\nCODICE (slimmed):\n{code_context}"

    # FASE 0 — Triage
    print(f"\n[FASE 0] TRIAGE...", file=sys.stderr)
    complexity = calculate_complexity(full_topic)
    signals = detect_signals(full_topic)
    active_modules = [
        SIGNALS[s]["module"]
        for s in signals
        if complexity >= SIGNALS[s]["min_complexity"]
    ]
    cast = get_cast(complexity)
    print(
        f" [Complessita: {complexity}/10] [Segnali: {signals}] [Moduli: {active_modules}]",
        file=sys.stderr,
    )
    print(f" [Cast: {len(cast)} personaggi]", file=sys.stderr)

    print(f"\nTask Plan:", file=sys.stderr)
    print(f"  1. Esecuzione Parallela: Hacker, Contabile, Utente", file=sys.stderr)
    print(f"  2. Round 1 (Sequenziale): Hacker -> Contabile -> Utente", file=sys.stderr)
    print(f"  3. Round 2 (Sequenziale): Hacker -> Contabile -> Utente", file=sys.stderr)
    print(f"  4. Avvocato del Diavolo: Critica completa", file=sys.stderr)
    print(
        f"  5. Round 3 (Sequenziale): Hacker -> Contabile -> Utente (recalibrate/reject/concede)",
        file=sys.stderr,
    )
    print(f"  6. Avvocato del Diavolo: Final Pass", file=sys.stderr)
    print(
        f"  7. Moduli: {active_modules if active_modules else 'Nessuno'}",
        file=sys.stderr,
    )
    print(f"  8. Chiusura: Lead Architect", file=sys.stderr)

    # FASE 2 — Proposte Parallele
    print(f"\n[FASE 2] PROPOSTE PARALLELE...", file=sys.stderr)
    proposals = {}
    for c in cast:
        if "Lead" in c or "Avvocato" in c:
            continue
        print(f" {c}...", file=sys.stderr)
        prop = call_role(
            c,
            f"Sei: {c}. Problema: '{topic}'. La TUA proposta in 4-5 frasi. Non sai cosa dicono gli altri.",
            timeout=timeout,
        )
        proposals[c] = prop
        print(f"  -> {prop[:200]}...\n", file=sys.stderr)

    # FASE 3 — Round 1 (Sequenziale)
    print(f"\n[FASE 3] ROUND 1 (Sequenziale)...", file=sys.stderr)
    round1 = {}
    for c in cast:
        if "Lead" in c or "Avvocato" in c:
            continue
        context_parts = []
        for other in cast:
            if other == c or "Lead" in other or "Avvocato" in other:
                continue
            context_parts.append(f"{other}: {proposals.get(other, '')[:300]}")
            if other in round1:
                context_parts.append(f"{other} (Round 1): {round1[other][:300]}")
        others_text = "\n\n".join(context_parts)
        prompt = (
            f"Sei: {c}. Round 1 su '{topic}'.\n"
            f"Proposte e interventi finora:\n{others_text}\n\n"
            f"La TUA reazione. Se non hai nulla da aggiungere, scrivi 'Niente da aggiungere'. Massimo 4 frasi."
        )
        print(f" {c} (Round 1)...", file=sys.stderr)
        round1[c] = call_role(c, prompt, timeout=timeout)
        print(f"  -> {round1[c][:200]}...\n", file=sys.stderr)

    # FASE 4 — Round 2 (Sequenziale)
    print(f"\n[FASE 4] ROUND 2 (Sequenziale)...", file=sys.stderr)
    round2 = {}
    for c in cast:
        if "Lead" in c or "Avvocato" in c:
            continue
        context_parts = []
        for other in cast:
            if other == c or "Lead" in other or "Avvocato" in other:
                continue
            context_parts.append(
                f"{other} (Proposta): {proposals.get(other, '')[:200]}"
            )
            if other in round1:
                context_parts.append(f"{other} (Round 1): {round1[other][:200]}")
            if other in round2:
                context_parts.append(f"{other} (Round 2): {round2[other][:200]}")
        others_text = "\n\n".join(context_parts)
        prompt = (
            f"Sei: {c}. Round 2 su '{topic}'.\n"
            f"Dibattito completo finora:\n{others_text}\n\n"
            f"Dopo due giri, hai nuove idee? Vuoi modificare la tua posizione? "
            f"Se non hai nulla da aggiungere, scrivi 'Niente da aggiungere'. Massimo 4 frasi."
        )
        print(f" {c} (Round 2)...", file=sys.stderr)
        round2[c] = call_role(c, prompt, timeout=timeout)
        print(f"  -> {round2[c][:200]}...\n", file=sys.stderr)

    # FASE 5 — Avvocato del Diavolo
    print(f"\n[FASE 5] AVVOCATO DEL DIAVOLO...", file=sys.stderr)
    devil_key = next((c for c in cast if "Avvocato" in c), None)
    if devil_key:
        all_text = "\n\n".join(
            f"{k} (Proposta): {proposals.get(k, '')[:300]}\n"
            f"{k} (Round 1): {round1.get(k, '')[:300]}\n"
            f"{k} (Round 2): {round2.get(k, '')[:300]}"
            for k in proposals
        )
        prompt = (
            f"Sei: {devil_key}. Hai ascoltato TUTTO il dibattito su '{topic}'.\n\n{all_text}\n\n"
            f"Trova 2-3 difetti per OGNI posizione. Cita passaggi esatti. "
            f"Sii spietato ma costruttivo. Massimo 5 paragrafi."
        )
        devil_critique = call_role(devil_key, prompt, timeout=timeout)
        print(f"  -> {devil_critique[:300]}...\n", file=sys.stderr)
    else:
        devil_critique = ""

    # FASE 6 — Round 3 (Recalibrate/Reject/Concede)
    print(f"\n[FASE 6] ROUND 3 (Recalibrate/Reject/Concede)...", file=sys.stderr)
    round3 = {}
    for c in cast:
        if "Lead" in c or "Avvocato" in c:
            continue
        context_parts = []
        for other in cast:
            if other == c or "Lead" in other or "Avvocato" in other:
                continue
            context_parts.append(
                f"{other} (Proposta): {proposals.get(other, '')[:200]}"
            )
            if other in round1:
                context_parts.append(f"{other} (Round 1): {round1[other][:200]}")
            if other in round2:
                context_parts.append(f"{other} (Round 2): {round2[other][:200]}")
            if other in round3:
                context_parts.append(f"{other} (Round 3): {round3[other][:200]}")
        others_text = "\n\n".join(context_parts)
        prompt = (
            f"Sei: {c}. Round 3 su '{topic}' — Replica all'Avvocato.\n\n"
            f"Dibattito:\n{others_text}\n\n"
            f"Critiche dell'Avvocato:\n{devil_critique[:500]}\n\n"
            f"Per OGNI critica che ti riguarda, usa UNO di:\n"
            f"[RECALIBRATE] L'Avvocato ha ragione, ricalibro.\n"
            f"[REJECT] L'Avvocato sbaglia, spiego perche'.\n"
            f"[CONCEDE] L'Avvocato ha ragione, non posso difendermi.\n\n"
            f"Se non hai nulla da aggiungere o nessuna critica da affrontare, scrivi 'Niente da aggiungere'. Massimo 4 paragrafi."
        )
        print(f" {c} (Round 3)...", file=sys.stderr)
        round3[c] = call_role(c, prompt, timeout=timeout)
        print(f"  -> {round3[c][:200]}...\n", file=sys.stderr)

    # FASE 7 — Avvocato Final Pass
    print(f"\n[FASE 7] AVVOCATO FINAL PASS...", file=sys.stderr)
    if devil_key:
        all_round3 = "\n\n".join(
            f"{k} (Round 3): {round3.get(k, '')[:400]}" for k in round3
        )
        prompt = (
            f"Sei: {devil_key} — Final Pass su '{topic}'.\n\n"
            f"Le tue critiche originali:\n{devil_critique[:400]}\n\n"
            f"Risposte ricevute:\n{all_round3}\n\n"
            f"Valuta ogni critica: le ricalibrazioni sono sufficienti? "
            f"I reject sono fondati? Le concessioni cambiano il quadro? "
            f"Se non hai nulla da aggiungere (tutte le critiche risolte), scrivi 'Niente da aggiungere'. Massimo 5 paragrafi."
        )
        devil_final = call_role(devil_key, prompt, timeout=timeout)
        print(f"  -> {devil_final[:300]}...\n", file=sys.stderr)
    else:
        devil_final = ""

    # FASE 8 — Verbale Finale
    print(f"\n[FASE 8] VERBALE FINALE (Lead Architect)...", file=sys.stderr)
    context = "\n\n".join(
        f"### {k}\nPROPOSTA: {proposals.get(k, '')}\n"
        f"ROUND 1: {round1.get(k, '')}\n"
        f"ROUND 2: {round2.get(k, '')}\n"
        f"ROUND 3: {round3.get(k, '')}"
        for k in proposals
    )
    verdict = chat(
        CLOUD_MODEL,
        f"Lead Architect. Verbale Finale su '{topic}'.\n\n{context}\n\n"
        f"Critiche Avvocato:\n{devil_critique}\n\n"
        f"Final Pass Avvocato:\n{devil_final}\n\n"
        f"Redigi: 1) Sintesi 2) Mappa Recalibrate/Reject/Concede "
        f"3) Obiezioni non risolte 4) Decisione 5) Allegato Tecnico 6) Piano Azione. Markdown.",
        max_tokens=2000,
        timeout=timeout * 2,
    )

    print(f"\n{'=' * 70}")
    print(verdict)
    print(f"{'=' * 70}")

    # Metriche di chiusura
    total_objections = (
        devil_critique.count("critica") + devil_critique.count("difetto")
        if devil_critique
        else 0
    )
    recalibrates = sum(1 for r in round3.values() if "[RECALIBRATE]" in r)
    rejects = sum(1 for r in round3.values() if "[REJECT]" in r)
    concessions = sum(1 for r in round3.values() if "[CONCEDE]" in r)
    opt_outs = sum(
        1
        for r in list(round1.values()) + list(round2.values()) + list(round3.values())
        if "niente da aggiungere" in r.lower()
    )

    print(f"\n [*] ASSEMBLEA COMPLESSA CONCLUSA.", file=sys.stderr)
    print(
        f" [*] {len(proposals)} proposte, 3 round completati, {opt_outs} opt-out",
        file=sys.stderr,
    )
    print(
        f" [*] Ricalibrature: {recalibrates} | Reject: {rejects} | Concessioni: {concessions}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
