---
name: aphrael-strategerium
description: "Optional Strategerium execution-contract and independent Rules Lawyer workflow. Invoke only when the user explicitly requests Strategerium or this skill; never automatically for ordinary tasks."
---

# Strategerium on Hermes

Read [the complete source workflow](source/WORKFLOW.md) before proceeding. All its
requirements remain binding, including exact-contract user approval, independent
strategy/review, evidence rules and terminal outcomes. Its role prompts are
preserved under [source/references](source/references/strategic_agent.md).

Hermes adapter: references to Codex mean the current Aphrael orchestrator. Use
Hermes `delegate_task` for isolated role passes, supplying the relevant complete
role prompt and only the needed artifacts. Never have the implementation worker
judge its own completion. Use actual available provider/model routing; do not
translate product model names into invented model identifiers. Native task
status and a role's self-report are not independent proof of external outcomes.

The existing explicit approval of an unchanged contract remains valid across
sessions; do not request it again merely because this skill was reloaded.
For durable work use the explicitly selected Aphrael Kanban board and separate
worker/reviewer homes provisioned by setup. Preserve compact artifacts and
evidence through that supported workflow rather than building another engine.
The source's relative references resolve within source/. If role isolation is
unavailable, report that specific limitation; do not impersonate independent
review and claim its gate passed.
