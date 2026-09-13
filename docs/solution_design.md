# Solution Design

## Objective

Create a controlled finance-exception workflow that uses deterministic rules for detection and classification, then uses an AI-assistant pattern to reduce investigation effort without weakening finance governance.

## Design principles

1. **Controls before AI** — factual exception detection is performed by deterministic logic.
2. **Evidence before narrative** — the assistant receives a structured evidence packet rather than raw unrestricted context.
3. **Explainability** — every classification records the triggering rule, variance, ageing and owner.
4. **Human authority** — sensitive finance actions require review and approval.
5. **Least privilege** — an AI assistant should not receive direct posting or payment-release permissions by default.
6. **Auditability** — source facts, rule outputs, assistant output and human decisions should be retained separately.

## Processing architecture

```mermaid
flowchart LR
    A[ERP / CRM / Bank / Billing feeds] --> B[Data validation]
    B --> C[Exception rule engine]
    C --> D[Severity & ownership]
    D --> E[Evidence packet builder]
    E --> F[AI assistant]
    F --> G[Human review queue]
    G --> H[Approved action]
    H --> I[Audit log & management MI]
```

## Implemented prototype components

- `exception_management_engine.py` — validation, classification, materiality, routing and reporting.
- `ai_assistant.py` — structured evidence packet, deterministic offline summary and review-control flags.
- `sample_finance_exceptions.csv` — synthetic multi-process finance cases.
- `example_exception_actions.csv` — review queue with evidence and assistant summary.
- `example_management_summary.csv` — process/severity management view.

## Why the public repository uses an offline assistant

A public portfolio should not require API credentials or pretend that an uncontrolled model is authoritative. The deterministic assistant stub makes the interface and governance boundary visible. In production, `create_assistant_summary()` could be replaced by a governed enterprise LLM call while leaving classification, severity and approval logic under deterministic control.

## Production extensions

A production solution could add event-driven ingestion, policy-specific thresholds, case workflow, approval matrices, evidence attachments, prompt/version logging, model evaluation, role-based access, feedback capture and closed-loop reporting.