# Verification Report

Date: 2026-09-12. Independent completion review under Strategerium Rules Lawyer and the explicitly requested Adeptus Necroneerium Shade evaluation role. The reviewer inspected the original request, approved contract, source, test assertions, manifesto, vision, architecture, and usage documentation; the reviewer did not implement repairs.

## Executed evidence

- Independently executed from this checkout: `.\SETUP_APHRAEL.ps1`, exit 0, editable installation successful. Runtime: Python 3.13.12 on Windows.
- Final independent `.\.venv\Scripts\python.exe -m pytest -q`: **34 passed, 0 failed, 0 skipped, 2 warnings in 6.15 seconds; exit 0**. Warnings concern upstream Starlette/httpx and AnyIO deprecations; they did not prevent execution.
- Inspected assertions exercise the actual API, queue, worker, capability, policy, verification, SQLite, Windows junctions, process termination, and process restart. The process test starts a real server, kills it with completed/running/queued work, starts another process, and checks exact completed-record survival, honest interruption, and queued recovery.
- Independent additional API execution invoked all five real capabilities, compared repository branch and changed-file output with direct Git, retrieved schemas/profiles, and confirmed immediate inspection did not create task history. The subsequent Git whitespace repair was rechecked with an exact ` M file.txt` assertion and the final complete suite.
- Observed Work Process browser/launcher evidence was supplied as concrete interaction records, not an implementation claim: all five tools invoked through the page; unavailable `voice` profile rejected; queued and running work cancelled; repository task states and evidence inspected. Final launcher started on port 8765, all four health checks were ready, and a newly created repository task visibly moved RUNNING to COMPLETED with QUEUED/RUNNING/COMPLETED events and verified evidence. After terminating the server, Refresh displayed unavailable; after invoking the launcher again, the same selected task, result, and evidence remained unchanged and health returned ready. Older task history also survived. Private workstation output is intentionally omitted here.
- Post-setup source-control inventory and ignore checks found only intended source, tests, configuration examples, and documentation; runtime databases, logs, environment values, browser profiles, and build metadata are excluded. `git diff --check` completed without whitespace errors.

## Criterion Results

- **AC-1: PASS.** Exact contract and explicit “Go ahead and execute” approval are recorded in `APPROVAL.md`. Work uses the existing checkout; dependency/source inventory respects exclusions and contains working components rather than empty future subsystems.
- **AC-2: PASS.** Setup ran successfully on native Windows; observed `START_APHRAEL.ps1` launches and relaunches served the documented loopback page. Missing prerequisites and conflicts have actionable messages.
- **AC-3: PASS.** Live health remained responsive during queued work; degraded persistence, executor, and registry tests require nonhealthy/503 responses. Browser disconnection was visibly reported.
- **AC-4: PASS.** API and real-process tests assert durable IDs, objectives, timestamps, profile, events, terminal result/error/evidence, and exact completed-record survival after restart; list and ID retrieval are exercised.
- **AC-5: PASS.** Actual queued/running/completed/failed/cancelled paths, failure continuation, queued recovery, interrupted-running recovery, single-instance exclusion, and cancellation races pass. In-flight reads finish before the next delegated worker starts; terminal cancellation cannot be overwritten.
- **AC-6: PASS.** Deterministic registered-tool work runs through default, explicit, and configured profile selection. All six aliases are represented. Unknown/unconfigured/unsupported profiles fail honestly. Worker interface and configuration hold no fabricated hosted provider.
- **AC-7: PASS.** All five capabilities ran against actual local resources. System metrics are structured, real Git output is independently compared and preserves status columns, filesystem successes/errors and bounds are asserted.
- **AC-8: PASS.** Immediate and delegated denial tests assert restricted handlers never execute. Unknown tools and supplied approval fields fail. Traversal, absolute/device/stream paths, private paths, hard links and actual Windows junction escapes are denied; inspected text cannot alter policy.
- **AC-9: PASS.** The core-owned observation ledger, not worker return text, governs completion. Missing, failed and mismatched evidence fail; mutating returned evidence cannot replace the recorded observation. Successful result/evidence equality and verification are asserted and observed.
- **AC-10: PASS.** Actual browser interaction covers health, immediate tools, task creation/profile errors, recent history, progress, results/evidence and queued/running cancellation. The page reflects live backend health including disconnect/reconnect.
- **AC-11: PASS.** The development HTTP adapter uses provider-neutral commands/Core. All documented routes are exercised; direct Core task submission also validates shared command constraints. No voice SDK/type/personality dependency enters the core.
- **AC-12: PASS.** Runtime configuration rejects locations inside either the source checkout or configured inspection repository. Defaults are outside source control. Ignore checks and public-artifact inspection pass; examples contain only supported harmless configuration. Runtime has no external service requirement.
- **AC-13: PASS.** README and deeper guide match executed setup/start/test and interface behavior. Architecture/plan identify the implemented foundation while preserving historical provider research; manifesto, vision and license are retained.
- **AC-14: PASS.** Final complete suite is 34 passing tests with no skips. Real API integration and separate-process restart assertions supplement observed native Windows launcher/browser behavior. Tests assert behavior rather than relying solely on mocks or source inspection.
- **AC-15: PASS.** Independent Shade/Rules Lawyer review evaluated every criterion and original intent. Targeted findings were repaired by the Work Process and independently rechecked; final validation is recorded here and supplies the concise user handoff.

## Findings and repair recheck

- **F-1, task lifecycle, retry 1: resolved.** Cancellation could fall between publishing RUNNING and creating its cancellation signal. The signal is now published first; a seam test cancels at the RUNNING transition and asserts the handler never runs.
- **F-2, runtime configuration, retry 1: resolved.** Changing the inspection repository previously permitted runtime data inside the actual source checkout. Both roots are now checked; the regression rejects that configuration.
- Final boundary refinements also pass: direct Core command validation, malformed HTTP length handling, invalid default-profile validation, and exact Git status whitespace preservation.

## Intent Fidelity

**PASS.** The delivered product is the approved first executable local foundation with real capabilities, persistent asynchronous execution, external-to-worker policy and verification, and replaceable adapters. Deferring voice, AI planning, hosted workers and broader integrations follows the explicit request and approved scope; it does not claim the entire long-term vision is implemented.

## Unauthorized Scope Expansion

None material.

## Terminal Judgment

**COMPLETE — Adeptus Necroneerium Shade project PASS; all binding items verified.**

Required action: none for foundation acceptance. Normal use starts with `.\START_APHRAEL.ps1`, then the walkthrough in `FOUNDATION.md`. Known limitations remain the documented deterministic single-worker scope, cooperative cancellation of in-flight reads, trusted local account access, and deferred voice/model integrations. Changes have not been pushed or deployed.
