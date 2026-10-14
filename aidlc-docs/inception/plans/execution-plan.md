# Execution Plan

## Detailed Analysis Summary

### Transformation Scope

This is a **brownfield evolution** of an existing Python prototype toward the target architecture in `docs/sdd/sdd_orquestrador_agentes_v5.md`. The current runtime is a learning ReAct flow under `application/`; the immediate implementation increment is R1, a Maker-Checker flow with validated input/output schemas.

### Change Impact Assessment

- **User-facing impact:** Moderate. The system will evolve from a demo question-answer runtime into an automated CI/CD support workflow.
- **Structural impact:** High. The orchestrator, specialist agents, and validation flow will need new event-driven and governance layers.
- **Data model impact:** High. New structured event, findings, patch, QA, and approval contracts are needed.
- **API impact:** High. The current local Python module interfaces will expand to include pipeline-event handling and policy-aware execution.
- **NFR impact:** High. Security, auditability, determinism, and resilience are central requirements.
- **Application layer impact:** High. The current prototype will need additional worker orchestration, validation logic, and policy-aware action handling.
- **Infrastructure layer impact:** Medium to High. The project may eventually require webhook exposure, CI/CD triggers, and controlled execution environments.

### Key Components Affected

- `application/agente.py` — runtime loop, session state, metrics, execution persistence
- `application/orquestrador.py` — orchestration of specialist tasks and flow coordination
- `application/especialistas.py` — specialist agents and contract definitions
- `application/ferramentas.py` — local tool registry and tool execution contracts
- `application/config.py` — provider, token, and runtime configuration
- `docs/sdd/sdd_orquestrador_agentes_v5.md` — consolidated target architecture and governance model

### Risk Assessment

**Risk level: High**

Reasons:
- The project changes the runtime’s purpose from a local demo to a governed CI/CD healing workflow.
- Multiple technical concerns intersect: event intake, diagnostics, patch proposal, QA, policy, and audit trail.
- The system impacts operational trust and production safety, so deterministic gates and human approval matter.

## Workflow Visualization

```mermaid
flowchart TD
    A([Start]) --> B[Workspace Detection]
    B --> C[Reverse Engineering]
    C --> D[Requirements Analysis]
    D --> E[User Stories]
    E --> F[Workflow Planning]
    F --> G{Application Design}
    G -->|EXECUTE| H[Application Design]
    G -->|SKIP| I[Units Generation]
    H --> I
    I --> J{Functional Design}
    J -->|EXECUTE| K[Functional Design]
    J -->|SKIP| L[NFR Requirements]
    K --> L
    L --> M{NFR Design}
    M -->|EXECUTE| N[NFR Design]
    M -->|SKIP| O[Infrastructure Design]
    N --> O
    O --> P[Code Generation]
    P --> Q[Build and Test]
    Q --> R([End])
```

## Phases to Execute

### INCEPTION PHASE

- [x] Workspace Detection — completed; repository includes a brownfield Python prototype and SDD target architecture.
- [x] Reverse Engineering — completed; current runtime and target-state differences were documented.
- [x] Requirements Analysis — completed; requirements were captured around event-driven diagnosis, patching, testing, and governance.
- [x] User Stories — completed; stories cover diagnosis, patching, validation, and governance concerns.
- [x] Workflow Planning — completed; execution plan generated and ready for review.
- [x] Application Design — generated and approved as the basis for incremental work; aligned to v5 and R1.
- [x] Units Generation — generated and approved; U1 is Maker-Checker and schema contracts, using R0 as existing baseline.

### CONSTRUCTION PHASE

- [ ] Functional Design — U1 required; current checkpoint is awaiting user review.
- [ ] NFR Requirements — U1 required to select schema validation approach and set local runtime constraints.
- [ ] NFR Design — U1 required only for patterns needed by the selected NFR requirements.
- [ ] Infrastructure Design — skipped for local R1; reconsider for webhook, CI/CD, sandbox, or external integrations.
- [ ] Code Generation — required once the design is approved.
- [ ] Build and Test — required after implementation.

### OPERATIONS PHASE

- [ ] Operations — placeholder for future deployment, monitoring, and production-readiness workflows.

## Recommended Package / Component Update Sequence

1. **R1 — Maker-Checker contracts** — add validated structured inputs/outputs to the current specialist flow; no external actions.
2. **R2 — Authorization and guardrails** — add deterministic controls outside the LLM.
3. **R3 — Failure intake and diagnosis** — implement validated CI/CD events and evidence-backed diagnosis.
4. **R4 — Patch proposal and isolated QA** — introduce bounded patch/worktree workflow and regression testing.
5. **R5 — CI/CD and non-production promotion** — add PR integration and gated DEV/STAGING.
6. **R6 — Production governance** — add human approval tied to an immutable artifact and audit evidence.

## Estimated Timeline

- **Inception and planning:** 1-2 days
- **Architecture design and unit decomposition:** 1-2 days
- **Core implementation of diagnosis + patch + QA pipeline:** 3-5 days
- **Regression testing and governance hardening:** 2-3 days
- **Total effective timeline:** 1-2 weeks for a controlled first milestone

## Success Criteria

The project succeeds when:

- the current prototype is clearly evolved toward the SDD-driven architecture,
- the orchestration flow can model a CI/CD failure and produce structured diagnosis,
- patch proposals and QA are gated before promotion,
- auditability and controls are traceable,
- and the basic project progression is supported by regression tests and milestone reviews.

## Status

**Approval:** User approved the inception artifacts on 2026-10-14 and authorized alignment to SDD v5 and continuation into Construction.

**Current stage:** Functional Design for U1 (Maker-Checker and Schema Contracts); awaiting approval before NFR Requirements.
