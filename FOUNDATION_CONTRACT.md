# Execution Contract — Aphrael Foundation v1.0

## Request Reference

Clifton's original request: `C:/Users/Zero/.codex/attachments/471fb996-8691-4d84-9bb3-264d38fe743f/pasted-text.txt`. Repository: `denni1cd/aphreal`, existing checkout `C:/Users/Zero/python_projects/ai/aphreal`, baseline `e6a7534`. All six existing tracked files were read: README, MANIFESTO, VISION, ARCHITECTURE, PROJECT_PLAN, and LICENSE.

## Objective

Deliver the first real Windows-native Aphrael foundation: simple local startup, real safe capabilities, persistent asynchronous tasks, independently grounded completion evidence, and replaceable interaction/worker boundaries. This milestone advances the enduring vision without implementing voice or requiring paid services.

## Deliverables

- D1: Executable local application, setup/start launcher, minimal developer interface.
- D2: Persistent task engine, working deterministic worker, configurable profiles, safe tool registry, policy and verification boundaries.
- D3: Automated tests, observed Windows execution/restart evidence, independent evaluation and concise handoff.
- D4: Updated documentation and public-repository hygiene.

## Constraints

- C1: Work directly in the existing repository. Before implementation, independently review this draft under Strategerium and obtain Clifton's explicit approval of the reviewed contract. Review approval, silence, and the original request do not authorize implementation.
- C2: No new paid account, usage-based API, subscription, cloud compute, telephone number, paid hosting or tunnel dependency. No voice implementation or local speech experimentation/downloads.
- C3: Native Windows, normal Python environment; no Docker, WSL/Linux installation, Kubernetes, Redis, PostgreSQL, RabbitMQ, microservices, virtual machines or distributed scheduler. Use Python 3.12+, FastAPI and SQLite unless a material technical obstacle warrants a reviewed contract revision.
- C4: Keep the core provider-independent; permissions and proof of completion are not controlled by worker assertions. Protect private information and preserve existing project principles/research.

## Assumptions

- A1: The newer request supersedes the old Phase-0-only and voice-first sequencing in PROJECT_PLAN. Telephone access remains a future product goal, not this milestone's acceptance requirement.
- A2: A deterministic worker executing explicitly selected, bounded safe capabilities satisfies real task execution; natural-language reasoning and paid/local model integration are not required. Unconfigured profiles must remain honestly unavailable.
- A3: One local user, one active worker and a local browser development page are sufficient. Cancellation of this milestone's cooperative worker is practical and required. No automatic re-execution of interrupted work is necessary if interruption is recorded honestly.

## Strategy

Build one complete vertical path from a small local interaction surface through a provider-neutral core to immediate tools or queued work, then through policy-controlled capabilities and evidence verification to durable results. Start with executable tests and the smallest working slice; extend that same codebase to all acceptance criteria. Use a lightweight browser page over the local API, a single worker queue, SQLite, and a deterministic safe-tool worker. Validate real Windows operation and restart survival, then run independent Adeptus Necroneerium evaluation and repair failures. Do not build placeholder future integrations.

## Acceptance Criteria

- AC-1 — Approval and scope: Implementation begins only after Strategerium's independent contract review and Clifton's explicit approval of this version (or a reviewed successor). Work remains in the existing checkout, uses appropriate available Astra capabilities, and obeys C2/C3 and the complete exclusions below. Only working, necessary components are added; no empty future subsystem scaffolding. Strategerium and Necroneerium are development processes, not runtime dependencies.
  Covers: D1–D4, C1–C4.
  Evidence: Approval/review record; repository diff and dependency/setup inspection.

- AC-2 — Installation and startup: The documented normal Python environment installs and runs natively on Windows. A command as simple as `./START_APHRAEL.ps1` starts Aphrael from the existing repository without repeated file editing or manual component assembly. Setup automates safe dependency/environment preparation; any unavoidable missing prerequisite or administrative action receives one clear actionable instruction. Startup failures are understandable.
  Covers: D1, C2/C3, reduced babysitting.
  Evidence: Execute documented setup and launcher on Windows; record exact commands, runtime version and startup outcome.

- AC-3 — Real service health: The local service binds to loopback and exposes structured health/status checking the running application, reachable persistence, operational task executor and tool registry. A failed required subsystem cannot be reported healthy. Health and task queries remain responsive while delegated work is active.
  Covers: D1/D2, C4, conversation/execution separation.
  Evidence: Live HTTP checks during real task execution; automated degraded-subsystem checks.

- AC-4 — Durable task data: Each task durably records a unique ID, user objective, creation/update timestamps, selected worker/profile, status, progress/events, result, error and verification/evidence. SQLite-backed history, events and results survive a real process restart and are retrievable by ID and recent-task listing.
  Covers: D2, continuity.
  Evidence: Persistence tests plus create/execute/retrieve, stop process, restart and retrieve the same task and evidence.

- AC-5 — Actual lifecycle: Real queued work progresses through QUEUED and RUNNING to COMPLETED, FAILED or CANCELLED as appropriate. A single active worker services the queue; failures preserve useful error information and do not prevent subsequent work. Queued cancellation prevents execution; running cancellation reaches the cooperative worker and prevents a later completion overwrite. Restart handling resolves previously active tasks into an honest documented state rather than leaving them forever RUNNING or falsely complete; queued work has a documented, tested recovery behavior.
  Covers: D2, truthful state, recovery and user control.
  Evidence: Automated lifecycle, failure, cancellation/race and restart tests exercising real storage/executor; observed progress events.

- AC-6 — Workers and profiles: A replaceable worker interface has at least one working deterministic worker that performs real registered safe-tool work. Default and explicit task profile selection work. Configuration supports aliases `voice`, `fast`, `general`, `deep`, `coding`, `local`; provider/model selections are configuration data, not names scattered through core logic. Unknown, unsupported or unconfigured profiles return explicit unavailable/error states without crashing the application or silently impersonating a functioning provider. No hosted worker is fabricated.
  Covers: D2, C4, model flexibility.
  Evidence: Actual default/override worker execution and automated configuration, unavailable-profile and worker-failure tests; interface/configuration inspection.

- AC-7 — Real capabilities: An extensible registry exposes validated structured inputs/results and real tools for (a) workstation hostname, OS, CPU information/usage where practical, memory and relevant process information; (b) actual Aphrael repository branch, clean/dirty state, changed files and current commit; (c) constrained filesystem list, read and search. Tool failures are distinguishable from empty/negative results. Unavailable optional machine metrics are identified honestly.
  Covers: D2, useful real action.
  Evidence: Invoke all capabilities against this workstation/repository, compare Git output with direct Git observations, and execute deterministic registry/tool tests including error results.

- AC-8 — Enforced policy and file boundary: Tool metadata distinguishes safe read-only, state-changing and approval-required actions. A policy boundary external to the worker mediates immediate and delegated calls; worker input or inspected file text cannot grant permission or reclassify a tool. Safe authorized tools need no repeated approvals. Unknown/disallowed tools and approval-required actions without trusted approval cannot execute. Filesystem access stays within explicitly allowed roots, including traversal and link/junction escape handling, with bounded inspection output. No dangerous write tool is added to prove policy.
  Covers: D2, C4, privacy and user control.
  Evidence: Tests execute both call paths and denied calls using harmless test capabilities, assert denied handlers do not run, and exercise allowed/escaping filesystem paths and untrusted-content permission attempts.

- AC-9 — Grounded completion: COMPLETED requires recorded evidence of the requested supported operation, produced from actual capability execution and evaluated outside the worker's success claim. Results/evidence identify the operation and observed structured outcome. Missing, unsuccessful or unrelated evidence cannot turn a worker's “success” into verified completion; failure and cancellation remain honest. No broad arbitrary-command runner is required.
  Covers: D2, C4, fundamental verification principle.
  Evidence: Real successful system/Git tasks with persisted evidence and adversarial tests for success text without evidence, failed tool output and mismatched evidence.

- AC-10 — Usable development harness: A small local browser control page lets Clifton see health, invoke safe capabilities, create a task with an optional worker/profile, view recent tasks, observe status/progress, inspect result/evidence/errors and cancel queued/running work. Controls show actual backend state and understandable errors; no final-UI or frontend-design project is introduced.
  Covers: D1/D2, manual-effort goal.
  Evidence: Actual browser interaction covering each action against the running service, including task completion and cancellation; record the short user walkthrough.

- AC-11 — Future adapter boundary: A documented provider-neutral core/API boundary supports Aphrael/system status, immediate safe tools, delegated task creation with model/worker preference, task querying/cancellation and result retrieval. The development adapter uses that boundary; core/task/capability behavior does not depend on voice-provider types, SDKs, prompts or personality. Adding a future conversation/voice adapter need not redesign those components.
  Covers: D1/D2/D4, C4, extensibility.
  Evidence: Boundary/dependency review and executed API tests for every enumerated operation; document how a future adapter calls them without implementing voice.

- AC-12 — Public repository and private runtime data: Runtime databases, logs, secrets, browser profiles, `.env` values and personal memory/data remain outside the repository/source control. `.gitignore` guards against accidental inclusion; `.env.example` contains only actual supported configuration names and harmless example values. No credentials, tokens, passwords or private output are committed or included in public evidence. Filesystem/logging defaults avoid unnecessary private-data collection or exposure; milestone runtime needs no external data transmission.
  Covers: D4, C2/C4, privacy.
  Evidence: Runtime-path and ignore checks; final tracked/staged diff and example/log inspection using synthetic sensitive fixtures where needed.

- AC-13 — Documentation: Keep README concise and useful, with install/start/test instructions and links to deeper documentation for interface usage, runtime-data location, implemented/deferred capabilities and future adapter attachment. Update ARCHITECTURE and PROJECT_PLAN to make the approved foundation the current milestone and paid telephone/realtime research future options, preserving that research and the enduring MANIFESTO/VISION principles. Documentation matches actual commands/configuration and retains the license.
  Covers: D4, C4.
  Evidence: Documentation diff and execution of the documented setup/start/test/verification walkthrough.

- AC-14 — Automated and end-to-end proof: Add tests from the beginning and run the complete suite successfully, covering persistence, lifecycle, workers, registry, policy, evidence, configuration/profiles, practical deterministic system/repository behavior and service health. At least one acceptance test begins at the exposed API/interface, creates real safe work, executes the real worker/tool/policy/verification/storage path and retrieves the persisted verified result; mocks alone cannot satisfy it. Actual Windows application execution also proves startup, workstation/Git inspection, observable task transitions, result/evidence retrieval and history survival after restart. Required acceptance behavior is not silently skipped.
  Covers: D1–D3, full definition of success.
  Evidence: Reproducible test commands with exact pass/fail/skip totals and exit codes, acceptance output and observed application/restart record; substantive skips cannot substitute for criterion evidence.

- AC-15 — Independent closeout: After implementation and tests, invoke installed Adeptus Necroneerium to independently inspect the delivered repository against this approved contract, MANIFESTO, VISION, relevant architecture and actual execution/test evidence, without relying on the worker summary. Correct failures and repeat verification until criteria pass or a specific unavoidable blocker is demonstrated. The final concise report states what was built/tested, exact test results, Necroneerium's final assessment, remaining limitations, exact startup command, the click/type walkthrough and any remaining manual action. A blocker is reported as incomplete, never as accepted completion.
  Covers: D3/D4, C1, truthful delivery.
  Evidence: Independent assessment and repair/recheck record plus final report with traceable execution evidence.

## False-Completion Traps / Risks

- F1: Old Phase 0 language could yield only scaffolding; AC-4–AC-14 require a working integrated foundation.
- F2: Deterministic work could be mislabeled reasoning or fake evidence; AC-6/AC-9 require honest capability limits and independently grounded outcomes.
- F3: Queue/cancellation/restart races could lose state or claim success; AC-4/AC-5 require direct lifecycle/recovery proof.
- F4: Provider abstractions could be empty interfaces or coupled to HTTP/voice; AC-11 requires an exercised, documented boundary.
- F5: Local read access could expose private paths or runtime artifacts; AC-8/AC-12 require enforced boundaries and public-repository checks.
- F6: Machine prerequisites and launcher behavior could leave Clifton assembling the system; AC-2/AC-10/AC-14 require actual Windows and browser execution.

## Out of Scope

- O1: Selecting/implementing final voice, paid voice providers, PSTN/telephone calling/numbers, Twilio, OpenAI Realtime, Gemini Live, local STT/TTS, speech models/stacks (including Fish Speech/Whisper), custom/cloned voices or speech experiments.
- O2: Email, calendar, PowerSchool, financial integrations, home automation, arbitrary desktop-control AI, unrestricted model PowerShell, long-term personal memory, simultaneous heavy workers, mobile apps, production remote networking/tunnels, elaborate plugin marketplaces and distributed architecture.
- O3: Hosted/Codex/LM Studio runtime worker integration, autonomous recurring scheduling, automatic Windows login startup, general shell/write tools and full conversation/persona systems. Future extension is documented; these implementations are unnecessary for this foundation.

## Specialist Use

- None. The request and six repository documents supply sufficient scope evidence; no narrow external investigation is needed to define this foundation.

## Contract Status

DRAFT — v1.0. Awaiting independent Strategerium Rules Lawyer review, then Clifton's explicit approval. Implementation is not authorized yet.
