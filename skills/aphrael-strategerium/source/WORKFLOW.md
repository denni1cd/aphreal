---
name: strategerium
description: "Run the Strategerium v0 workflow for an explicitly requested complex task: independently define a minimal verifiable Execution Contract, obtain contract review and explicit user approval before work, then independently verify completion. Do not use for ordinary direct tasks unless the user asks for Strategerium."
---

# Strategerium

## Mission and invocation

Use this skill only when the user explicitly asks for Strategerium (including `$strategerium`). Its purpose is to separate definition of success, execution, and completion judgment. The user remains the authority that authorizes execution.

The required lifecycle is:

```text
USER REQUEST → STRATEGIC AGENT → DRAFT EXECUTION CONTRACT
→ RULES LAWYER CONTRACT REVIEW → CONTRACT APPROVED
→ USER APPROVAL GATE → WORK PROCESS → READY FOR REVIEW
→ RULES LAWYER COMPLETION REVIEW → COMPLETE | REPAIR REQUIRED | BLOCKED | CONTRACT DEFECT
```

Use normal capable Codex as the default Work Process. Do not invoke or require Adeptus Necroneerium unless the user separately and explicitly requests it.

## Role separation

Treat the Strategic Agent, optional Specialist, Rules Lawyer, and Work Process as separate responsibilities. Use isolated role passes or subagents when the environment supports them; do not let the Work Process define its own success standard or judge its own completion. Pass only the artifacts needed across boundaries, never private reasoning.

- **Strategic Agent** controls *what* must be achieved. It creates the smallest complete, implementation-neutral Execution Contract. Read [the strategic role prompt](references/strategic_agent.md) before this pass.
- **Specialists** are optional, isolated, and advisory. Use one only when a focused question would materially improve the contract. They expand knowledge, not authority. Read [the specialist prompt](references/specialist.md) when one is used.
- **Rules Lawyer** is independent of both strategy and execution. It reviews the contract before execution and the result afterward. Read [the Rules Lawyer prompt](references/rules_lawyer.md) for either review.
- **Work Process** controls *how* approved outcomes are achieved. It has broad discretion over architecture, research, tools, supporting scripts, tests, infrastructure, assets, and subagents that reasonably serve the approved criteria.

## Contract and review gate

1. Preserve the original user request and supplied context as authoritative.
2. Have the Strategic Agent issue a versioned **Draft Execution Contract**. Every required deliverable, explicit constraint, and material implied success condition must appear in its acceptance criteria. The contract defines product outcomes, not incidental implementation means.
3. Have the independent Rules Lawyer issue a contract review. If it returns `CONTRACT REVISION REQUIRED`, route only the necessary correction back to the Strategic Agent and repeat review.
4. When the Rules Lawyer returns `CONTRACT APPROVED`, present the complete current Execution Contract. Do not omit or summarize any acceptance criterion, constraint, assumption, or scope boundary. State clearly: **Execution is awaiting your explicit approval of this exact contract.**
5. **Stop.** Do not inspect, plan, edit, research, delegate execution, run implementation commands, or otherwise begin the Work Process at this point.

The original task request, silence, continuation of the session, lack of objections, and `CONTRACT APPROVED` are not execution authorization. Begin work only after the user explicitly approves the current exact contract. If the contract changes materially, return it through contract review and obtain fresh explicit approval.

## Execution and review

After explicit approval, give the Work Process the original request, the approved contract, recorded approval, and any targeted repair report. It may not add a new user-facing outcome, feature, deliverable, strategic goal, or quality target. If such an outcome appears necessary, report `POTENTIAL CONTRACT DEFECT` rather than silently expanding scope.

When it believes the approved criteria are met, it submits a **Review Package** with artifacts, criterion-by-criterion evidence, known blockers, and any potential contract defect, ending in `READY FOR REVIEW`. It never declares `COMPLETE`.

The independent Rules Lawyer then evaluates every acceptance criterion with exactly one of `PASS`, `FAIL`, `BLOCKED`, or `NOT PROVEN`, and separately checks whether the contract still fulfills the original request.

- `COMPLETE`: every criterion passes, evidence is sufficient, and intent fidelity passes.
- `REPAIR REQUIRED`: return only the smallest useful deficiencies to the Work Process; preserve passed work. No new user approval is needed if the approved contract is unchanged.
- `BLOCKED`: name the external blocker and the narrowest resolution.
- `CONTRACT DEFECT`: return the defect to the Strategic Agent. The corrected contract must pass review and receive fresh user approval before execution resumes.

## Evidence rule

**Absence of evidence is not evidence of completion.** When a criterion concerns observable runtime or interactive behavior that can reasonably be exercised, a pass requires direct execution, interaction, an automated behavioral test, end-to-end run, or equivalent evidence that actually exercises the claimed behavior. Static source inspection, metadata, syntax checks, or a passing test whose assertions do not demonstrate the criterion are not sufficient substitutes. Keep verification proportional to the task; do not create bureaucracy for claims that cannot reasonably benefit from it.

## Boundaries

Do not create councils, voting, critic swarms, mandatory specialists, permanent orchestration infrastructure, token machinery, or a state machine. Do not perform a Rules Lawyer repair yourself. Do not treat a preferred architecture or optional enhancement as a requirement. Targeted repair is preferred over restarting unaffected work.
