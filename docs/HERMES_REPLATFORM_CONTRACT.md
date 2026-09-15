# Draft Execution Contract — Aphrael Hermes Replatform v1.0

## Request Reference

Clifton's complete request is `C:/Users/Zero/.codex/attachments/815a0f77-f7c3-415a-8872-06f72806707c/pasted-text.txt`. It controls interpretation. Existing repository: `denni1cd/aphreal`, `C:/Users/Zero/python_projects/ai/aphreal`. Inspected baseline: `08dbf7e98f8272e8d44fff173d6bb75ac7ae59d5` (2026-09-12), all 29 tracked files and the seven-commit history. The current request supersedes conflicting foundation-era sequencing; the previous foundation approval does not approve this migration.

## Objective / Goals

Deliver working Aphrael on native Windows with Hermes Agent as its underlying runtime. Evolve this existing repository into a versioned, installable Hermes Profile Distribution with Aphrael identity, supported configuration, skills, narrowly necessary extensions, setup/start automation, tests and documentation. Preserve useful foundation guarantees without maintaining a second agent platform.

## Deliverables

- D1: Supported Aphrael profile distribution, isolated private runtime, real configured provider and usable interactive startup.
- D2: Supported tools, memory, nonblocking delegation, durable work and independently grounded verification, with the smallest necessary Aphrael guardrails.
- D3: Safe migration/update/rollback path, retired obsolete production runtime, updated vision, manifesto and operational documentation.
- D4: Reproducible tests and actual execution evidence, independent Adeptus Necroneerium and Strategerium completion evaluation, and concise implementation handoff.

## Constraints

- C1: Strategerium contract review precedes Clifton's explicit approval of this exact version. Stop after presenting the reviewed contract. No implementation, installation, migration branch creation, runtime configuration or destructive migration before that approval. Material revisions require fresh review and approval.
- C2: Hermes is the runtime. Use supported profiles/distributions, providers, skills, plugins/hooks, tools/toolsets, delegation, Kanban, MCP and APIs where appropriate. No parallel generic orchestration platform. No fork/vendor copy unless a concrete requirement demonstrably cannot be met through supported interfaces; such a material change returns through contract review and Clifton approval.
- C3: Native Windows using official Hermes installation/configuration; no WSL, Linux, Docker, Kubernetes, virtual machine or separate always-on cloud server prerequisites. No new paid service. No inferior local-model fallback to manufacture passing tests.
- C4: No Twilio, SIP, PSTN, tunnels, telephone infrastructure or repeated local STT/TTS experiments. Preserve natural remote voice as product direction and telephone only as a possible future adapter. Optional supported Desktop/local voice evaluation must be straightforward with existing services and cannot block or expand migration acceptance.
- C5: Never read, print, report or place raw auth tokens in Git. Prefer supported existing Codex/ChatGPT OAuth reuse/import. If interactive OAuth is unavoidable, first finish all independent preparation and give exactly one concise manual authorization step. Mutable state and secrets remain outside Git.
- C6: Preserve a recoverable pre-Hermes Git baseline and create a clearly named migration branch before destructive changes. Do not merge into `main` during implementation. Do not delete old production runtime before replacement checks pass. Use Git history, not permanent duplicate production code, as the archive.

## Assumptions

- A1: A supported native Windows text surface is sufficient for this milestone; Desktop is preferred only when it meets the same proof and startup requirements without extra infrastructure. Voice is not required for acceptance.
- A2: Existing foundation history remains recoverable in its original private runtime directory and Git baseline. Importing old task records into Hermes is not required; migration must not erase them or represent them as new Hermes work.
- A3: A single trusted Windows user is the deployment boundary. Native local tool access is not an OS security sandbox. Programmatic restrictions and verification must protect the approved action paths against untrusted worker/content authority without claiming protection against a malicious same-user process. Supported shared-root OAuth resolution is permitted intentionally; profile isolation does not mean copying or sandboxing refresh tokens.
- A4: Existing account access may be usable, but no login or model availability is assumed proven. Provider unavailability leaves required real-model criteria incomplete.

## Existing Foundation and Architectural Decisions

The baseline has one FastAPI/Uvicorn process, a deterministic worker, five bounded read-only capabilities and SQLite task state. Core, not worker output, owns deep-copied operation evidence. Real tests cover cancellation races, interrupted-running/queued restart behavior, Windows junctions/hardlinks, denied operations and private runtime paths. `docs/VERIFICATION.md` records a prior independent 34-test pass and Necroneerium COMPLETE; that is historical evidence, not a new test run or proof of Hermes integration. There is no existing model conversation, voice provider or personal-memory integration to preserve.

Proposed decisions:

1. Use the official current Hermes runtime, with a recorded tested version/revision and supported native Windows installation. The Aphrael repository distributes project assets; it does not contain Hermes source or user state.
2. Install a named isolated Aphrael profile through the supported distribution mechanism from a local checkout at a recorded commit. Use an explicit `distribution_owned` allowlist and Aphrael-namespaced skills/plugins; preserve unrelated assets. Reconcile required security defaults with user config deliberately: updates preserve config, whereas force install/reset can overwrite it. Never use delete-and-recreate as safe reinstall. Versioned defaults and user-owned state must have distinct ownership; updates must not overwrite memory, sessions, credentials or user customization silently.
3. Put durable identity/personality in `SOUL.md` within documented SOUL scope. Procedures belong in skills, operational controls in supported configuration/extensions, and development-only repository instructions in `.hermes.md` only if useful. Personality is never a security or completion authority.
4. Use Hermes providers/model routing and standard tools/toolsets. Add no generic model registry, filesystem/shell/browser/search framework, queue, database or task manager.
5. Use Hermes isolated delegation for ephemeral work and Hermes Kanban for durable work. Current model-facing top-level `delegate_task` runs in the background on surfaces supporting later delivery; orchestrator children and stateless endpoints can remain synchronous. Prefer stock asynchronous delegation and prove parent overlap. The public subagent lifecycle API is an additional supported extension point, not a mandatory custom replacement; its handles cannot reconnect after process exit. Use separate durable worker/reviewer profile homes and an explicitly selected Aphrael Kanban board/state root on every participating surface; fail startup on invalid/missing board selection rather than falling back to the shared default.
6. Use Hermes reviewer/Kanban workflow for independent verification. Native `complete_task` can mark work done without generic external proof; completion hooks observe a committed transition and cannot veto it. Therefore distinguish native lifecycle `done` from trusted verified outcome through a narrow supported plugin/tool/reviewer mechanism. Bind independent observations to the requested action/task and protect verification authority against worker forgery/replay. Required guards must fail closed and startup must detect missing/disabled guards; Python callback exceptions alone are not fail-closed enforcement. No parallel task engine.
7. Keep Strategerium and Adeptus Necroneerium optional invokable specialist workflows through supported skills or specialist profiles. Do not inject their orchestration into every ordinary task. MCP configuration is included only for an actually used integration.

These choices follow the official repository inspected on 2026-09-14 at Hermes `0.21.2`, commit `49c6d4a9e0dddc64d6333c5b1fcc9d911463a8fd`, not integration claims. [Current research matrix](HERMES_RESEARCH.md) records all mandatory topics and source links. Key primary sources: [distribution implementation](https://github.com/NousResearch/hermes-agent/blob/49c6d4a9e0dddc64d6333c5b1fcc9d911463a8fd/hermes_cli/profile_distribution.py), [public asynchronous lifecycle](https://github.com/NousResearch/hermes-agent/blob/49c6d4a9e0dddc64d6333c5b1fcc9d911463a8fd/website/docs/developer-guide/subagent-lifecycle-api.md), [native Windows](https://github.com/NousResearch/hermes-agent/blob/49c6d4a9e0dddc64d6333c5b1fcc9d911463a8fd/website/docs/user-guide/windows-native.md). Official Git Bash on native Windows is allowed; WSL remains excluded. Desktop/TUI are supported candidates; dashboard embedded terminal chat is not supported on Windows. Defaults should deliberately use manual high-risk approvals and deny unattended unsafe operations, not the default auxiliary-model smart approval as proof of permission.

## Files / Components to Retain, Replace or Remove

| Existing files | Proposed disposition after approval |
| --- | --- |
| `LICENSE` | Retain unchanged. |
| `VISION.md`, `MANIFESTO.md` | Retain and update: Aphrael identity/system principles, voice aspiration, no mandatory telephone prerequisite. |
| `README.md`, `ARCHITECTURE.md`, `PROJECT_PLAN.md` | Rewrite current guidance around demonstrated Hermes operation; retire superseded custom-platform and telephone-first prescriptions to Git history. |
| `FOUNDATION_CONTRACT.md`, `docs/APPROVAL.md`, `docs/VERIFICATION.md` | Preserve identifiable historical foundation contract, approval and evidence; clearly distinguish the new contract/approval/verification. |
| `docs/FOUNDATION.md` | Replace current-use guide with Hermes setup/use/state/recovery documentation; historical guide remains at baseline. |
| `SETUP_APHRAEL.ps1`, `START_APHRAEL.ps1` | Rewrite as thin official-install/profile setup/update and supported-surface launch automation. |
| `.gitignore`, `.env.example`, `pyproject.toml` | Retain only supported needed configuration/test packaging; remove obsolete variables/dependencies/entry point, strengthen private-state exclusions. No empty compatibility packaging. |
| `src/aphrael/__init__.py`, `__main__.py`, `app.py`, `index.html` | Remove obsolete custom service/browser harness after replacement proof. |
| `src/aphrael/core.py`, `storage.py`, `workers.py`, `commands.py`, `config.py` | Remove old queue, persistence, worker, command and generic model-profile machinery after guarantee mapping and proof. |
| `src/aphrael/capabilities.py` | Replace generic capabilities with Hermes tools; preserve only demonstrably necessary Aphrael policy/evidence logic through supported extensions. |
| `tests/test_capabilities.py`, `test_engine.py`, `test_lifecycle.py`, `test_process.py` | Carry forward useful behavior/adversarial scenarios as Hermes/Aphrael tests; remove tests coupled solely to deleted runtime after replacements pass. Preserve historical assertions in Git. |
| New supported assets | `distribution.yaml`, `SOUL.md`, configuration defaults, skills, only necessary plugins/guardrails, setup tests and execution evidence. `.hermes.md` and MCP configuration only when actually needed. |

## Migration Sequence

1. After explicit approval, record approval, create `codex/hermes-replatform` (or an equally clear collision-free name), and preserve the full pre-migration commit through a named baseline tag/reference. Keep existing private foundation state intact. Recheck official Hermes compatibility against researched behavior before using a changed upstream version.
2. Establish the official native Windows runtime and isolated test/profile boundary. Implement distribution and thin setup/start scripts; resolve provider access through supported OAuth mechanisms with the single manual step rule if needed.
3. Prove identity, real conversation, real read and controlled write, memory and update preservation. Enable only the toolsets and approvals needed for the approved capabilities.
4. Prove concurrent parent/delegated conversation and durable Kanban lifecycle. Exercise independent review and negative evidence/policy cases; add the smallest supported guardrail required by those outcomes. Integrate specialist workflows.
5. Map and pass replacement checks before removing obsolete runtime. Update project documents and execute final setup/start/update/regression checks on the resulting tree. Preserve baseline rollback and private state.
6. Submit actual evidence and diff for independent Necroneerium and Strategerium completion review. Repair failures within the approved contract and re-run affected verification; report blockers honestly. Do not merge `main`.

## Acceptance Criteria

Every condition below is binding. Referenced constraints, decisions, file dispositions and migration ordering are part of the criterion citing them. Static inspection supports but never substitutes for required observable execution.

- **AC-1 — Authorization, current research and scope:** Independent Strategerium review and Clifton's explicit approval of this exact contract are recorded before implementation. The complete mandatory Hermes research covers native Windows, profiles/distributions, SOUL/project context, providers/Codex OAuth, memory, tools/toolsets, plugins/hooks, approvals/security, delegation, Kanban/review, background processes, API/TUI gateway, Desktop/dashboard, skills/agentskills.io, MCP, update semantics and state locations. It identifies current official source revisions/links, limitations and decisions rather than relying on remembered behavior. C1–C6 and exclusions remain satisfied. Material incompatibility requires a reviewed contract revision rather than a quiet scope reduction or unsupported fork.
  Covers: D1–D4, C1–C6.
  Evidence: dated official-source research record, review and approval record, dependency/configuration/diff inspection and execution timeline.

- **AC-2 — Native Windows setup and startup:** `SETUP_APHRAEL.ps1` uses official supported mechanisms to install/verify Hermes and safely install/update Aphrael without manual component assembly. `START_APHRAEL.ps1` launches the isolated profile in a supported interactive surface. Native Windows health/doctor checks pass for required functionality; optional unavailable capabilities are identified separately. Launch/relaunch and actionable failure messages work. No prohibited prerequisites or new paid service are introduced.
  Covers: D1/D3, C3/C4, A1.
  Evidence: execute exact setup and start commands on this Windows machine; record Hermes/runtime versions, actual surface, doctor outcomes, exits and relaunch result.

- **AC-3 — Supported distribution and private state:** The versioned repository actually installs an isolated Aphrael Hermes profile through supported profile distribution or a comparably clean documented current mechanism. Required assets and decisions 1–7 are implemented, with no second generic platform, placeholder integration or unused MCP. Validate explicitly owned namespaced assets, selected Kanban board/root and separate worker/reviewer homes; supported intentional OAuth sharing follows A3. Resolved runtime paths for memory, sessions, auth, keys, databases, logs and other personal state are outside both checkout and Git. Other profiles and existing foundation state are not modified inadvertently.
  Covers: D1/D2/D3, C2/C5, A2/A3.
  Evidence: execute installation into an isolated profile, inspect nonsecret resolved path/ownership metadata, verify profile isolation with synthetic markers and inspect repository/dependency diff.

- **AC-4 — Identity and real provider conversation:** Starting Aphrael yields Aphrael's identity rather than the stock Hermes persona and supports a normal multi-turn text conversation with a real configured model, including a context-dependent follow-up. Identity uses SOUL only within documented scope. Provider/model configuration uses Hermes routing; no fabricated provider or silent inferior fallback. Supported existing OAuth/import is preferred; raw auth tokens are never inspected, printed, reported or committed. If necessary, only one concise manual OAuth action is requested after all possible independent work.
  Covers: D1, C2/C3/C5, A4.
  Evidence: actual multi-turn interaction, sanitized identity/context observations, provider/model name and supported auth-method metadata, setup record without credential contents.

- **AC-5 — Real tools and action verification:** Aphrael uses supported Hermes tools to inspect real workstation and repository state and accurately reports it, including a direct independently compared repository observation. It performs a harmless authorized write/action in a disposable workspace and an independent observer/reviewer checks the actual resulting state against the requested outcome. Failures and empty results are distinguishable. Existing useful filesystem read/list/search and workstation/repository inspection scenarios are covered by supported tools rather than reconstructed generic infrastructure.
  Covers: D2, C2, foundation real-action guarantees.
  Evidence: actual model-driven tool runs, direct ground-truth comparisons, disposable artifact before/after checks and reviewer evidence linked to the request.

- **AC-6 — Memory and nondestructive update:** An explicitly nonsecret memory survives a genuinely new session and remains outside Git. Live observation wins in an exercised stale-memory conflict. Profile update and reinstall are executed with existing memory, sessions, usable credentials and a user customization in place; none is erased or silently replaced. Distribution-owned changes take effect through documented ownership/conflict behavior. Interrupted/failed update leaves a usable prior state or a tested recoverable backup; no credentials need be printed to prove preservation.
  Covers: D1/D2/D3, C5/C6, decisions 2/3.
  Evidence: new-session recall, stale-memory/live-tool demonstration, before/after synthetic state and metadata, post-update/reinstall session retrieval and real authenticated model use, harmless update failure/recovery exercise.

- **AC-7 — Nonblocking isolated delegation:** A real isolated delegated task runs through supported Hermes mechanisms while the parent Aphrael conversation accepts and answers an unrelated follow-up before that task finishes. The task's scope/context isolation and eventual result/status are inspectable. Sequential execution disguised by status text does not pass. Background processes alone are not durable-task proof.
  Covers: D2, C2, decision 5, conversation/execution separation.
  Evidence: timed real parent and child interaction showing overlap and isolated child context/result; supported mechanism/version recorded.

- **AC-8 — Durable tasks and honest lifecycle:** A real task uses Hermes Kanban or its supported current durable-work primitive; unique task identity, objective, status/progress, result/error and review/evidence remain inspectable after a new conversation and a relevant worker/runner process interruption/restart. Active interrupted work resolves honestly under documented recovery rules, queued work has tested recovery behavior, completed evidence survives, and failed/blocked work is never presented as completed. Cancellation reaches supported task execution and cannot later be overwritten with success; retries must not blindly repeat a controlled external action.
  Covers: D2, C2/C6, durable-state/recovery/control guarantees.
  Evidence: actual create/run/retrieve sequence and process-boundary exercise; controlled queued/active/terminal records, failure/blocked and cancellation cases, preserved task IDs/results/evidence and observed post-restart states.

- **AC-9 — Independent verified outcomes:** The actual configured Aphrael workflow distinguishes worker assertion, tool-reported result, independently observed outcome, uncertainty and failed/blocked state. A real task goes through Hermes reviewer/Kanban workflow; success requires evidence of the requested outcome judged outside its worker. Programmatic supported guardrails/reviewer authority prevent worker text or worker-supplied approval/evidence from granting verified status. Missing, failed, mismatched or fabricated evidence is rejected; a real verified write passes. A worker's lifecycle `done` alone must not be displayed/reported as verified completion. No new parallel task engine is created.
  Covers: D2, C2, decision 6, grounded-completion guarantee.
  Evidence: real reviewer execution with artifact observation, persisted review decision/evidence linkage, behavioral negative cases for each listed evidence defect and attempted worker self-approval. Test both immediate action reporting and durable-work completion paths.

- **AC-10 — Deliberate security and privacy:** Allowed capability/workspace boundaries and approval rules are documented and enforced outside model persona on parent and delegated paths. Dangerous host actions are not globally auto-approved. A harmless approval-required fixture is denied without trusted authorization, rejection prevents execution, and inspected content/worker arguments cannot authorize it. Approved low-risk operations remain usable. Private runtime/credential paths and boundary escapes (including traversal, Windows junction/link and alternate-path cases applicable to enabled tools) cannot be read or written through the enabled action paths without appropriate authorization. Inspection output is bounded, unnecessary private-data collection is avoided, and evidence uses synthetic fixtures. Native same-user limitations are stated honestly.
  Covers: D2/D3, C5, A3, existing external-policy/privacy guarantees.
  Evidence: actual harmless allowed/denied operations with assertions that denied effects do not occur, untrusted-content/worker tests, path-boundary tests and public evidence inspection; configuration alone is insufficient.

- **AC-11 — Optional specialist workflows:** Both installed Strategerium and Adeptus Necroneerium are evaluated for supported skills/specialist profiles and remain available as optional named workflows rather than requirements for ordinary requests. Preserve their explicit invocation, approval and independent-review boundaries while adapting Codex-specific orchestration references to supported Hermes capabilities. Demonstrate supported invocation; any workflow deferred must have a proven technical incompatibility with the exact mechanism, observed failure and a specifically bounded next step, as allowed by the request. Do not label unexecuted configuration an integrated workflow.
  Covers: D2/D3, C2, decision 7.
  Evidence: actual supported invocation and output, or reproducible incompatibility evidence with narrowly bounded follow-up and truthful integration status.

- **AC-12 — Cutover and rollback:** Before destructive migration, a clearly named branch and identifiable recoverable pre-Hermes Git reference are created, and existing private foundation state is preserved. File dispositions and migration order above are followed: old runtime is removed only after AC-2–AC-11 replacement checks pass (including the expressly permitted AC-11 bounded-incompatibility outcome). Each custom subsystem retained states the specific Aphrael requirement current Hermes cannot provide. No obsolete duplicate production platform remains. The rollback procedure restores a runnable baseline and its intact private state without overwriting Hermes user state; its feasibility is demonstrated in an isolated checkout/test state. The migration is not merged into `main`.
  Covers: D3, C2/C6, A2.
  Evidence: Git refs/diff and dated replacement checks before deletion, component-to-guarantee mapping, isolated baseline launch/health rollback rehearsal and preserved private-state metadata.

- **AC-13 — Product and operating documentation:** VISION/MANIFESTO reflect Aphrael as the assistant and Hermes as runtime, preserve natural remote voice aspiration and telephone as only a possible future adapter, and remove mandatory ordinary-phone/first-transport language. Preserve local-first action, model-independent identity, delegation, continuity, reasonable recovery, privacy, user authority and evidence-based completion. README, architecture, plan and use guide describe the actual resulting system, exact setup/start/test commands, provider path without credentials, state/update/recovery behavior, installed configuration and limits. Retain license and identifiable foundation evidence. Development context contains only repository-relevant development instructions. C4 remains an explicit milestone boundary.
  Covers: D3/D4, C4/C5/C6, decisions/file dispositions.
  Evidence: documentation diff checked against actual executed commands and observed behavior, complete principle/telephone-language review.

- **AC-14 — Real proof and independent closeout:** Tests and actual execution evidence cover every binding criterion with exact commands, versions, outcomes, exit codes and pass/fail/skip totals where applicable. Mocks/source inspection alone, skipped behavior, historical foundation results and unexecuted Hermes feature descriptions do not establish success. Independently invoke Adeptus Necroneerium against this approved contract, repository diff, actual execution evidence, VISION and MANIFESTO; repair failures and re-run evaluation. Independent Strategerium completion review evaluates every criterion and intent fidelity. Report any blocker as incomplete. The concise final report includes resulting architecture; removed/retained components and reasons; exact Hermes/profile configuration; exact setup/start commands; configured provider/model path without credentials; tests and exact outcomes; Kanban/delegation/memory/tool demonstrations; verification evidence; Necroneerium's final judgment; limitations; and the smallest sensible next milestone.
  Covers: D1–D4, C1–C6, truthful handoff.
  Evidence: sanitized criterion-by-criterion execution package, independent review/repair records and final report; completion only after all mandatory criteria pass.

## Risks / False-Completion Traps

- R1: Current upstream interfaces may differ from documentation or between versions. Record tested versions and verify actual Windows behavior; do not silently weaken requirements.
- R2: Subagent delegation may block the parent on a chosen surface. Require actual overlapping interaction through a supported mechanism; do not build a second scheduler to hide it.
- R3: Kanban `done` or reviewer text may not mean independently verified external success. AC-9 requires evidence authority and negative tests, not a persuasive prompt alone.
- R4: Native host tools may exceed the old bounded read-only policy. Enforce the approved broader write surface deliberately; denying private-path access in only one tool while shell/delegates bypass it does not satisfy AC-10.
- R5: Distribution update semantics may overwrite defaults or omit extension files. Exercise ownership, plugin installation, reinstall and recovery against populated state before cutover.
- R6: Account authorization, model availability or native feature incompatibility may block required proof. Complete independent preparation, request only the narrow OAuth step if applicable and retain the old runtime; do not invent success or add a paid dependency.
- R7: Deleting old code first or treating 34 historical tests as Hermes proof loses known guarantees. AC-12 makes cutover conditional on replacement evidence and recoverable baseline.

## Verification Approach

Use synthetic nonsecret fixtures and disposable workspaces for writes, policy denial, bad evidence, memory and recovery tests. Exercise the real model/provider and chosen interactive surface for conversation, tools, delegation and reviewer flow. Exercise real Hermes state and relevant process/session boundaries for Kanban and memory. Keep sensitive runtime artifacts private; version only sanitized reproducible evidence. Carry forward useful existing behavioral tests without preserving obsolete architecture. Independent reviewers judge observations, not worker assertions. AC-14 governs final review.

## Rollback Strategy

Before cutover, retain the pre-Hermes Git reference, original foundation private directory and documented baseline launch prerequisites. Keep Hermes installation/profile state separate. If installation/update or any mandatory replacement check fails, leave or return to the functioning baseline; do not delete or replay old task records. Use a separate checkout at the baseline and appropriate private test-state copy for a rollback rehearsal. Restore profile-owned configuration only through a tested backup/recovery path, preserving user memories, sessions and credentials. Never merge the migration into `main` in this session. AC-6/AC-12 supply the required proof.

## Non-Goals / Out of Scope

- O1: Telephone/PSTN, Twilio/SIP, tunnels, new voice providers, local STT/TTS experiments, voice as a cutover prerequisite.
- O2: A second agent framework, custom generic queue/model/tool engine, Hermes fork/vendor copy without the reviewed exception, placeholder integrations or mandatory specialist orchestration on every task.
- O3: New paid services, WSL/Linux/container/VM/cloud-server prerequisites, remote exposure, unrelated email/calendar/financial integrations, universal desktop automation, automatic login startup and a new custom UI product.
- O4: Importing historical foundation task records into Hermes, perfect persona determinism or a hostile-same-user security sandbox. Historical state must nevertheless remain recoverable.

## Specialist Use

Forward Strategic Agent independently inspected the entire existing tracked repository and history, current official repository/docs and installed Strategerium/Necroneerium instructions. These workflows are portable procedure text but include Codex-specific orchestration references; supported adaptation and actual invocation remain to be proven. Focused current official Hermes research informs supported-interface choices and unresolved implementation proof; research does not authorize execution or judge acceptance.

## Contract Status

**DRAFT v1.0 — awaiting independent Strategerium Rules Lawyer review.** Once reviewed, present the entire exact contract and stop for Clifton's explicit approval. **Execution is awaiting your explicit approval of this exact contract.** No implementation is authorized by this document or by the original request.
