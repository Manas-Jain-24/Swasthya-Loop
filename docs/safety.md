# Clinical AI Safety & Privacy Policy — SwasthyaLoop

## 1. Zero Medical Hallucination Principle
SwasthyaLoop does not provide autonomous clinical diagnoses, nor does it recommend changes to patient medications or dosages. All clinical care plans originate from licensed medical practitioners.

## 2. Traceability & Source Rules
Black-box AI risks patient trust and clinical adoption. Every follow-up flag generated in SwasthyaLoop includes:
- An explicit **Reason Code** (e.g. `READING_TASK_OVERDUE`).
- An audited **Source Rule ID** (e.g. `rule-missing-reading-v1`).
- Recommended outreach protocol.

Clinical measurement rules remain disabled by default until formally reviewed and ratified by an authoritative clinical panel.

## 3. Privacy & Synthetic Data Isolation
- This prototype operates entirely on synthetic fictional patients (`patient-001`, `patient-002`).
- No personal identifiers, phone numbers, or real clinical records are collected, transmitted, or stored.
- When calling external AI models, only anonymized structured counts and numbers are provided.

## 4. Deterministic Offline Fallback
Healthcare software must be resilient. SwasthyaLoop continues functioning with 100% feature availability when offline or without cloud LLM keys through its built-in deterministic fact-assembly engine.
