# Aphrael Project Plan

## Current milestone: working local foundation

Execution Contract v1.0 was independently reviewed and explicitly authorized by Clifton with “Go ahead and execute.” [FOUNDATION_CONTRACT.md](FOUNDATION_CONTRACT.md) defines acceptance. This milestone replaces the former Phase-0-only next action and does not require completing the telephone roadmap first.

The implemented scope is native Windows setup/startup, a local browser harness and API, real bounded read-only capabilities, persistent tasks with one deterministic worker, profile selection, enforced policy, independently grounded evidence, and honest cancellation/restart handling. [Foundation guide](docs/FOUNDATION.md) describes the actual behavior and commands.

Foundation closeout passed: 34 automated tests, observed Windows/browser operation and restart persistence, public-repository hygiene, and independent Adeptus Necroneerium evaluation. Both review findings were repaired and rechecked. See [verification evidence and assessment](docs/VERIFICATION.md) for the acceptance results and documented limits.

No paid accounts or hosted dependencies, voice implementation, local speech downloads, unrestricted shell/write tools, external integrations, long-term memory, recurring scheduler, or automatic Windows startup are included. The next product milestone should be chosen after foundation evaluation against the enduring [manifesto](MANIFESTO.md) and [vision](VISION.md).

## Preserved future roadmap

**Everything below is the original roadmap retained as historical research and future options.** Its phase order, original MVP definition, technology choices, and final “Phase 0 only” next-action instruction are superseded for the current milestone. They do not authorize new work or require paid services. Future voice/provider choices require fresh evaluation and explicit scope approval. Development review processes remain development tools, not runtime requirements.

---
# Aphrael Project Plan

**Status:** Initial implementation plan

This plan turns the Aphrael manifesto, vision, and architecture into an ordered implementation path. The project should prove the hardest user-facing risks early: real phone access, natural conversation, local-computer action, and separation of conversation from longer work.

The plan intentionally avoids building a large agent platform before those fundamentals are proven.

## Development Workflow

Every substantial milestone follows the same implementation process:

1. **Strategerium** reviews the repository, project documents, and milestone request.
2. Strategerium produces goals, non-goals, acceptance criteria, risks, and a concrete implementation strategy.
3. **User approval is a hard gate.** The worker does not begin implementation until the strategic plan is approved.
4. The implementation worker completes the approved scope.
5. Automated tests and milestone acceptance checks run.
6. **Adeptus Necroneerium** independently reviews the delivered state against the approved acceptance criteria and project rules.
7. Any defects are returned to the worker for correction.
8. The milestone closes only when acceptance criteria are evidenced or explicitly waived by the user.

Strategerium and Adeptus Necroneerium are implementation agents. Aphrael does not need them as runtime dependencies unless a later runtime use case specifically benefits from them.

---

# Phase 0 — Foundation and Repository Bootstrap

## Goal

Create the smallest maintainable local Python project that can support the first telephone experiment without prematurely implementing the rest of the architecture.

## Scope

- establish Python project and dependency management;
- establish source/test layout;
- configuration loading;
- structured local logging;
- `.gitignore` and `.env.example`;
- local health command/endpoint;
- basic pytest setup;
- preserve the foundation documents as authoritative project inputs.

## Important constraint

Do not generate empty modules for every future subsystem. Add only enough structure to cleanly support the next milestone.

## Acceptance criteria

- project installs/runs natively on Windows;
- no WSL or Docker dependency;
- `pytest` runs successfully;
- `aphrael --help` or equivalent CLI entry point works;
- a health check reports that Aphrael is running;
- secrets are excluded from Git;
- README contains local setup instructions;
- the project can be cloned to another Windows location and started from documented steps.

## Exit condition

The repository is a functioning application skeleton rather than documentation alone.

---

# Phase 1 — Realtime Voice on the Local Computer

## Goal

Prove Aphrael can hold a natural realtime spoken conversation while the orchestration process runs on the local Windows machine.

This phase should begin without telephone integration so realtime-agent configuration can be debugged locally with minimum moving parts.

## Scope

- OpenAI Agents SDK realtime session;
- Aphrael base persona prompt;
- configured voice selection;
- realtime interruption behavior;
- local microphone/speaker or SDK sample transport for development;
- local transcript/event logging with sensitive-data controls;
- configurable realtime model profile.

## Acceptance criteria

- Aphrael can begin a realtime conversation from the PC;
- user speech produces streamed spoken responses;
- the user can interrupt Aphrael while it is speaking;
- Aphrael correctly continues from the interruption rather than finishing an obsolete response;
- persona instructions visibly influence style without being required for correctness;
- voice/model settings come from configuration rather than hard-coded model names;
- failures are surfaced clearly rather than hanging indefinitely.

## Exit condition

Realtime conversation quality is sufficient to justify attaching the telephone layer.

---

# Phase 2 — Telephone Vertical Slice

## Goal

Make Aphrael reachable from an ordinary phone call while the Aphrael process runs only on the local PC.

This is the first major proof of the project concept.

## Primary implementation path

- Twilio voice-capable telephone number;
- Twilio Elastic SIP Trunking;
- OpenAI Realtime SIP connection;
- local incoming-call webhook endpoint;
- public HTTPS exposure through an outbound tunnel;
- verified OpenAI webhook signatures;
- local Aphrael process attaches to the incoming `call_id`;
- caller allowlist/baseline authentication before meaningful tools are enabled.

## Acceptance criteria

- call the configured number from the approved phone;
- Aphrael answers;
- Aphrael and the caller can hold a multi-turn natural conversation;
- interruptions work over the real telephone connection;
- the local Aphrael process can observe call start/end and session errors;
- invalid webhook signatures are rejected;
- unapproved callers do not receive privileged local-computer access;
- turning off Aphrael locally causes an honest unavailable/failure state rather than false success;
- no raw router port-forwarding is required.

## Stretch acceptance criterion

Aphrael recognizes the caller and uses an appropriate greeting without relying on caller identification as the sole authorization for sensitive actions.

## Exit condition

A normal phone call reaches a live Aphrael process on the user's computer reliably enough for repeated testing.

---

# Phase 3 — First Real Local Action

## Goal

Prove the complete end-to-end loop:

**phone -> Aphrael -> local PC tool -> verified result -> spoken response**

## Scope

Start with intentionally safe, read-only tools.

Recommended first tools:

- system uptime;
- CPU/RAM/GPU status where practical;
- disk space;
- selected process status;
- repository status for the Aphrael repo;
- current working environment information.

## Example acceptance conversation

> “Aphrael, is Codex running on my computer?”

Aphrael checks actual local process state and answers from the result.

> “How much free disk space do I have?”

Aphrael queries the workstation and reports the actual value.

## Acceptance criteria

- at least three read-only local tools are callable from the telephone conversation;
- results are derived from real machine state;
- tool failures are distinguishable from negative results;
- Aphrael does not invent a result if the tool errors;
- each tool call produces structured evidence/log information;
- the realtime conversation remains responsive after tool execution.

## Exit condition

Aphrael is no longer merely a phone chatbot; it can inspect the actual computer and accurately discuss what it observes.

---

# Phase 4 — Persistent Task System and Asynchronous Delegation

## Goal

Separate long-running work from the realtime conversation.

This is the second major proof of the project concept.

## Scope

- local SQLite task storage;
- task IDs and states;
- task creation from the realtime agent;
- worker queue;
- initially one heavy active worker at a time;
- progress events;
- cancellation;
- stored final result and evidence;
- voice tools for task creation/status/cancellation;
- restart handling for tasks left in an active state.

## Demonstration task

Use a harmless delegated task that takes long enough to prove conversation separation, such as repository analysis or web research.

## Acceptance criteria

During a phone call:

1. user asks Aphrael to start a nontrivial task;
2. Aphrael creates a persistent task and immediately returns to conversation;
3. user asks an unrelated question and receives a normal response while the worker continues;
4. user asks for task status and receives the actual stored state;
5. task completion persists outside the call session;
6. a later call can retrieve the task result;
7. task failure is preserved as failure rather than silently converting to completion;
8. cancelling a task updates the real worker and the stored task state.

## Exit condition

Long-running execution is genuinely independent from the voice conversation.

---

# Phase 5 — Worker and Model Routing

## Goal

Make Aphrael a multi-model system rather than a hard-coded wrapper around one model.

## Scope

Create a model/worker registry with named profiles.

Initial profiles should include:

- realtime voice;
- fast/general worker;
- deep reasoning worker;
- coding worker;
- local worker.

Exact provider/model names live in configuration.

## Coding worker

Integrate Codex behind an Aphrael worker adapter. Prefer workspace-scoped execution and capture observable results such as diffs, tests, command output, and worker status.

## Local worker

Add an adapter for LM Studio or another OpenAI-compatible local endpoint. Do not assume tool capabilities unsupported by the selected local model.

## Acceptance criteria

- user can explicitly select a worker/profile for a delegated task;
- default routing works when no override is supplied;
- changing the delegated worker does not disrupt the active realtime call;
- configured model names can be changed without editing routing code;
- a Codex worker can complete a bounded repository task and return evidence;
- a local worker can complete at least one supported task through the configured local endpoint;
- unsupported local-model features fail clearly instead of being silently emulated.

## Exit condition

Aphrael's identity and orchestration are demonstrably independent from any one worker model.

---

# Phase 6 — Work-Class Local Toolset

## Goal

Expand Aphrael from a proof of concept into something that can perform useful workstation tasks.

Capabilities are added in reliability order, not spectacle order.

## 6A — Files, Shell, and Development Tools

Add:

- controlled filesystem read/write/search;
- PowerShell and process execution;
- Python execution;
- Git status/diff/branch/worktree operations;
- test execution;
- repository-aware Codex work;
- risk classification and approval handling.

### Acceptance criteria

Aphrael can be asked to inspect a repository, delegate a bounded code change, run relevant tests, and report the observed outcome with a diff/test evidence trail.

## 6B — Browser Automation

Add Playwright with an Aphrael-owned persistent browser profile.

Capabilities:

- navigation;
- page inspection;
- structured clicking/form filling;
- downloads;
- authenticated sessions established specifically for Aphrael;
- screenshots/evidence where useful.

### Acceptance criteria

Aphrael can complete a real multi-page browser task from a phone request and accurately report success/failure without visual desktop automation.

## 6C — MCP and External APIs

Add a registry for local/remote MCP servers and direct API integrations as actual use cases require them.

Potential early integrations:

- GitHub;
- email;
- calendar;
- selected web services.

### Acceptance criteria

At least one external service integration can be used by a delegated task with policy-controlled permissions and verified outcomes.

## Exit condition

Aphrael can perform a meaningful subset of the activities for which ChatGPT Work is useful, using supported local/API mechanisms rather than depending on private ChatGPT UI functionality.

---

# Phase 7 — Approval, Authentication, and Secret Handling

## Goal

Make expanding capabilities safe enough for regular use.

Baseline protections already exist earlier; this phase makes them systematic.

## Scope

- tool risk classes;
- automatic approval for clearly low-risk operations;
- explicit approval for consequential actions;
- stronger confirmation mechanism than caller ID for sensitive actions;
- approval/cancellation through voice;
- persistent audit events;
- secret redaction from logs;
- migrate important secrets from development `.env` storage toward Windows-backed credential storage where practical;
- defend authorization boundaries against prompt injection from external content.

## Acceptance criteria

- a read-only request proceeds without needless confirmation;
- a configured sensitive action cannot execute without the required approval;
- rejecting an action prevents it from executing;
- external webpage/document text cannot independently grant permission to a tool;
- secrets do not appear in normal logs or Git history;
- resuming an approved/rejected task preserves the decision correctly.

## Exit condition

Aphrael can possess useful write-capable tools without every action being either unrestricted or constantly blocked.

---

# Phase 8 — Continuity and Memory

## Goal

Allow Aphrael to maintain useful continuity across calls without treating memory as authoritative reality.

## Scope

- persistent conversation sessions where useful;
- recent task history;
- project context records;
- user preferences explicitly appropriate for persistence;
- task/result retrieval across calls;
- model/profile preferences;
- bounded context assembly for workers;
- clear distinction between remembered context and live observed state.

## Acceptance criteria

- Aphrael can answer “what happened with the task I asked for yesterday?” from stored task state;
- a new phone call can continue relevant project context without replaying an enormous transcript;
- stale memory does not override current tool observations;
- project context can be updated without editing prompts;
- memory/state can be inspected and corrected.

## Exit condition

Aphrael feels continuous across calls while remaining grounded in real stored/observed state.

---

# Phase 9 — Supporting Output Channels

## Goal

Avoid forcing speech to carry information that is better viewed than heard.

## Scope

Begin with the simplest useful channel rather than building a custom mobile application.

Likely first option:

- SMS through the existing telephone provider for links, short summaries, identifiers, and artifact locations.

Possible later options:

- lightweight local/web task dashboard;
- push notification provider;
- dedicated mobile surface only if real usage justifies it.

## Acceptance criteria

- during a call Aphrael can send a requested link or concise result to the user's phone;
- the verbal conversation explains what was sent without reading long machine-oriented content aloud;
- sending externally is governed by the appropriate approval/policy rules.

## Exit condition

Voice remains primary without becoming an obstacle for visual information.

---

# Phase 10 — Desktop Control Fallback

## Goal

Handle useful Windows applications that provide no reliable API, CLI, MCP, or browser automation path.

## Scope

- screenshot capture;
- application/window awareness;
- mouse/keyboard input;
- local computer-use agent integration;
- focus and screen-state checks;
- evidence capture;
- strict policy boundaries.

## Constraints

Desktop control may require an unlocked interactive Windows session and will inherently be less reliable than structured integrations.

It must remain the fallback rather than becoming the default mechanism for applications that have better interfaces.

## Acceptance criteria

- one selected Windows application can be controlled for a bounded, repeatable task;
- Aphrael verifies post-action screen/application state where practical;
- loss of desktop access produces an explicit blocked state;
- a failed GUI action does not automatically trigger destructive blind retries.

## Exit condition

Aphrael gains a practical escape hatch for otherwise inaccessible software without making the entire project depend on brittle GUI automation.

---

# Phase 11 — Reliability, Persona Evaluation, and Daily-Use Hardening

## Goal

Turn the working system into something that can be left running and used regularly.

## Scope

- Windows automatic startup using an appropriate interactive-user mechanism;
- graceful shutdown/restart handling;
- health monitoring;
- recovery of interrupted tasks;
- configurable retention of logs/transcripts;
- usage and cost accounting;
- persona regression suite;
- voice conversation regression tests;
- tool/evidence acceptance tests;
- failure-injection tests for network/API/tool errors;
- installation/update documentation.

## Persona suite

Create representative test conversations covering at least:

- greeting;
- casual question;
- interruption;
- correction;
- disagreement;
- uncertainty;
- task failure;
- worker progress;
- request cancellation;
- user frustration;
- concise response;
- detailed explanation;
- humor where appropriate.

The suite evaluates tendencies rather than pretending personality can be perfectly deterministic.

## Acceptance criteria

- Aphrael starts automatically after the expected Windows login/startup condition;
- the health interface distinguishes voice/provider/tool failures;
- interrupted tasks are marked honestly after restart;
- usage/cost is locally inspectable;
- persona regression results can be compared across prompt/model changes;
- no known milestone acceptance test is silently skipped;
- setup and recovery procedures are documented.

## Exit condition

Aphrael is suitable for routine personal use rather than demonstration-only operation.

---

# MVP Definition

The **minimum viable Aphrael** is reached at the end of Phase 4, not at the end of the entire roadmap.

MVP means all of the following are true:

1. a real phone call reaches Aphrael;
2. the conversation is realtime and interruptible;
3. Aphrael can inspect actual local computer state;
4. Aphrael can perform at least one safe local action;
5. Aphrael can create a longer-running task;
6. that task runs separately from the active phone conversation;
7. Aphrael can report the real task status;
8. the task result survives the end of the call;
9. completion claims are backed by observable evidence.

If these are achieved, the fundamental project concept is proven.

Everything after the MVP expands useful capability, safety, continuity, and reliability.

---

# Implementation Priorities

When scope conflicts arise, prioritize in this order:

1. **Correctness and truthful state**
2. **Phone conversation quality**
3. **Reliable local action**
4. **Conversation/task separation**
5. **Security appropriate to the current capability**
6. **Useful tool breadth**
7. **Model flexibility**
8. **Continuity and convenience**
9. **GUI fallback capability**
10. **Novelty features**

A feature should not advance merely because it is impressive if it makes the first four priorities less reliable.

---

# Explicitly Deferred Work

The following should not be pulled into early milestones unless they become necessary to satisfy an acceptance criterion:

- paid always-on cloud hosting;
- custom mobile application;
- cloned/custom voice training;
- multiple simultaneous heavy workers;
- complex distributed queues;
- Redis/PostgreSQL infrastructure;
- microservices;
- home automation;
- autonomous recurring scheduling;
- broad financial actions;
- universal GUI automation;
- replacing every existing integration with a custom MCP server.

---

# Near-Term Next Action

The next implementation run should be **Phase 0 only**.

Strategerium should first review:

- `MANIFESTO.md`;
- `VISION.md`;
- `ARCHITECTURE.md`;
- this project plan;
- the current repository state.

It should then produce the Phase 0 implementation strategy and acceptance criteria for user approval before any source-code implementation begins.
