# Requirements Analysis

## Intent Analysis Summary

- **User request:** Start the project using the IA-DLC methodology and ground the work in the SDD documents under `docs/sdd/`.
- **Request type:** New project evolution from an existing brownfield prototype.
- **Scope estimate:** System-wide transformation across the current ReAct prototype and the target Self-Healing architecture.
- **Complexity estimate:** Complex.

## Context

The current repository contains a learning prototype in `application/` that demonstrates an orchestrator-workers runtime and specialist agents. The target architecture described in `docs/sdd/sdd_orquestrador_agentes_v2.md` defines an event-driven Self-Healing pipeline with:

1. webhook-triggered pipeline failure events,
2. diagnostic workers for logs + repo context,
3. developer workers that propose narrow code fixes,
4. QA workers that execute isolated regression tests,
5. deterministic quality gates for promotion,
6. human approval or strict deterministic gate for Production.

The prototype does not yet implement those capabilities; it is a Step 1 runtime exercise. This project should evolve it deliberately toward the architecture-aligned target while preserving the current learning context and documentation.

## Functional Requirements

1. **Project foundation and architecture traceability**
   - The project must be grounded in the architecture described in `docs/sdd/sdd_orquestrador_agentes_v2.md`.
   - The prototype in `application/` must be treated as the current baseline, not as the target production state.

2. **Event-driven failure intake**
   - The system must accept CI/CD pipeline failure signals as inputs.
   - The event payload should include identifiers such as pipeline ID, commit hash, repository URL, branch, stage, and raw error logs.

3. **Diagnostic workflow**
   - The orchestrator must analyze failure logs and repository context to identify likely root cause(s).
   - It must produce structured findings with severity, location, rationale, and remediation hints.

4. **Developer patch workflow**
   - A specialist or worker must propose a focused code patch limited to the root cause.
   - The workflow must distinguish between a proposed fix and actual repository mutation, enforcing deterministic authorization before any change is applied.

5. **Regression testing workflow**
   - The system must run isolated validation after a patch proposal.
   - Failures must surface as structured QA results and be used in promotion gates.

6. **Quality gate and promotion control**
   - The system must gate progression from diagnosis to patch, QA, DEV/STAGING, and PROD through deterministic checks.
   - Promotion to Production must require human-in-the-loop approval or a strict deterministic policy decision.

7. **Operational auditability**
   - The system must keep a durable execution record for failures, decisions, patches, tests, and approvals.
   - The flow should support later inspection of provenance and decision chain.

## Non-Functional Requirements

1. **Security and governance**
   - Apply deny-by-default policies for mutation and environment promotion.
   - Redact or prevent leakage of secrets, API keys, and sensitive PII in logs and outputs.
   - Distinguish model reasoning from deterministic control plane decisions.

2. **Reliability and resilience**
   - Limit iterations per agent and cap long-running work via token and runtime constraints.
   - Handle failures explicitly instead of silently proceeding.
   - Ensure failed tests or invalid output stop progression.

3. **Maintainability and observability**
   - Keep the current prototype and future target-state modules separated clearly in documentation and code artifacts.
   - Log metrics and execution state to support analysis and debugging.

4. **Testability**
   - Add or adapt regression tests for each execution stage that changes behavior.
   - Validate the flow with targeted automated checks from `application/tests`.

5. **Determinism**
   - Quality gates and authorization decisions must be explicit, inspectable, and not left to model discretion alone.

## Key Constraints

- The repository is currently a learning prototype and not yet a production-ready self-healing platform.
- The project must preserve the distinction between the implemented runtime and the target SDD architecture.
- Future work should evolve the current ReAct orchestrator incrementally toward the target design in a controlled, testable manner.
- The app should remain compatible with the existing developer workflow in `application/` and the standard test command: `python -m pytest tests -q`.

## Success Criteria

The project is successful when the repository clearly demonstrates a path from the current ReAct prototype to a controlled Self-Healing pipeline that includes:

- failure event intake,
- diagnosis,
- patch proposal,
- isolated QA,
- quality gates,
- audit and governance artifacts,
- and explicit production approval.

## Summary

This is a brownfield modernization effort with a clear architectural target. The team should progress incrementally from the current runtime into the target SDD-driven orchestration model while maintaining traceability, testability, and governance.
