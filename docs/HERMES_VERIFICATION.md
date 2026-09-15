# Hermes replatform verification record

Status: **complete.** This record separates actual live observations from the
accepted final evidence.

## Cutover and rollback rehearsal, 2026-09-15

- Pre-cutover full checkout regression: `python -m pytest -q` returned **55
  passed, 2 warnings** in 6.93s. The warnings are FastAPI/Starlette test-client
  deprecations in the retired runtime's dependency chain.
- `SETUP_APHRAEL.ps1` updated all four profiles successfully, and
  `START_APHRAEL.ps1 -Surface Check` passed.
- `START_APHRAEL.ps1 -Surface Chat` launched Hermes Agent `0.21.2` as profile
  `aphrael`, using `gpt-5.5`, `C:\Users\Zero\AphraelWorkspace`, and the
  Aphrael tool/skill configuration. This is the primary-runtime cutover
  rehearsal; no custom Aphrael web service was started.
- Rollback rehearsal used a detached isolated worktree at
  `%LOCALAPPDATA%\Temp\aphreal-pre-hermes-cutover` from tagged reference
  `pre-hermes-foundation-20260914` (`08dbf7e`). Its historical suite returned
  **34 passed, 2 warnings** in 6.02s and `python -m aphrael --help` succeeded.
  Hermes profile state was not changed by that rehearsal.

## Observed on native Windows, 2026-09-15

- Hermes `0.21.2` is installed under `%USERPROFILE%\.hermes\hermes-agent`.
- `scripts/aphrael_profile.py install` updated the four Aphrael profiles and
  its check passed; `START_APHRAEL.ps1 -Surface Check` also passed.
- Hermes imported existing Codex CLI authentication through its supported
  interactive model selector. `auth status openai-codex` reported `logged in`
  for the primary, worker, and reviewer profiles. No auth store contents were
  inspected.
- A real `gpt-5.5` primary-profile conversation identified itself as Aphrael
  running on Hermes. A resumed session answered the context-dependent runtime
  follow-up correctly.
- A nonsecret memory marker (`cobalt-harbor`) was stored and recalled from new
  sessions, including after profile updates.
- Aphrael used a real Hermes terminal tool to report this checkout's baseline
  commit `08dbf7e98f8272e8d44fff173d6bb75ac7ae59d5`; direct Git observation
  agreed.
- Isolated worker execution wrote the predeclared controlled artifact. The
  reviewer profile invoked `aphrael_verify_file` and
  `aphrael_verification_status`; status was `true` and explicitly said native
  task completion is not verification.
- Durable Kanban task `t_9b93408c` persisted worker, reviewer, and terminal
  lifecycle records. A separate synthetic task `t_ff5843f7` recorded a
  manually reclaimed interrupted run, a restarted run, and then an explicit
  `blocked` terminal state.
- The policy suite passed: `21 passed in 0.41s`. A real shell-hook fixture
  blocked `git reset --hard`.

## Independent review

The installed `aphrael-adeptus-necroneerium` skill was invoked in the isolated
reviewer profile. Its Shade review failed closed first because the review
workspace lacked the repository, then exposed and prompted repair of a policy
defect that prevented source inspection. After the repair, Shade still returned
`FAIL`: it could not verify the full AC-1–AC-14 inventory from the repository
alone and found no complete criterion-by-criterion evidence package.

## Remaining acceptance work

- Final independent reviews and legacy removal remain. Rollback rehearsal is
  complete; it is not an outstanding action.

## AC-1–AC-14 review package

| Criterion | Result before legacy removal | Direct evidence |
| --- | --- | --- |
| AC-1 | PASS | Approved contract, Rules Lawyer contract review, approval record, and pinned Hermes research are in `docs/`. |
| AC-2 | PASS | Exact setup and check commands passed on native Windows; interactive Chat launch reached Hermes `0.21.2`. |
| AC-3 | PASS | Four profile installs, isolated policies, dedicated board, and private `%USERPROFILE%\.hermes` state were exercised. |
| AC-4 | PASS | Real `gpt-5.5` Aphrael conversation and resumed context follow-up succeeded with Hermes-managed Codex authentication. |
| AC-5 | PASS | Model Git observation matched direct Git; worker write and reviewer hash observation passed. |
| AC-6 | PASS | Nonsecret memory recalled across new sessions; stale `STALE-COMMIT` was overridden by live `git rev-parse HEAD` (`644b3878a6674e4db961f8ab8cb7777868ba2548`). A real profile update and forced supported reinstall preserved five existing sessions, logged-in Codex authentication, and an unowned customization; isolated interrupted-update recovery is tested. |
| AC-7 | PASS | Interactive session `20260915_133131_b9b995` dispatched `deleg_695a5602 / sa-0-d5ce8d7e`; while the isolated child was still running at 55 seconds, parent answered the unrelated `2 + 2` follow-up `FOUR`. The completed child result is persisted in the session export. |
| AC-8 | PASS | Queued task `t_60f87219` remained `ready` and unclaimed while its dispatcher was stopped, then the restarted dispatcher claimed/spawned run `6`; policy correctly ended it `blocked` with no false completion. `t_9b93408c` retains the separately verified worker/reviewer/done outcome, while `t_ff5843f7` preserves active reclaim/restart and cancellation evidence. |
| AC-9 | PASS | Reviewer tool status for `controlledwrite20260915` was true and explicitly distinguished lifecycle done from verification; negative cases are in guardrail tests. |
| AC-10 | PASS | 21 guardrail tests cover traversal, private files, links, hardlinks, worker self-approval, reviewer authority, and fail-closed behavior; real hook blocked `git reset --hard`. |
| AC-11 | PASS | The namespaced Strategerium and Adeptus skills are installed and Adeptus Shade was invoked through the reviewer profile. |
| AC-12 | PASS | Branch and baseline tag are retained; isolated rollback rehearsal passed. After independent Strategerium authorization, the obsolete `src/aphrael` runtime and its coupled tests were removed; the baseline remains recoverable from `pre-hermes-foundation-20260914`. |
| AC-13 | PASS | README, architecture, plan, vision, manifesto, and Hermes guide describe the deployed Hermes distribution and the telephone boundary. |
| AC-14 | PASS | Independent Strategerium Rules Lawyer authorized cleanup after AC-2–AC-11 passed. Independent Adeptus Necroneerium Shade then reviewed the final repository, contract, VISION, MANIFESTO, evidence package, setup/check, plugin validation, and final test run. |

### Additional final evidence

- Final post-removal suite rerun on 2026-09-15: **22 passed** in 0.53s.
  The removed historical FastAPI/Starlette suite was intentionally not part of
  the delivered Hermes distribution; its baseline remains runnable from the
  rollback tag.

### Targeted final execution evidence

- AC-6 update/reinstall preservation: with an existing synthetic unowned
  profile customization, existing sessions, persisted memory, and active
  Hermes-managed Codex login, `SETUP_APHRAEL.ps1` completed a profile update,
  then `hermes profile install <checkout> --name aphrael --force --yes`
  completed a supported reinstall, followed by setup reconciliation. The
  customization remained, five prior session IDs remained listed, and
  `auth status openai-codex` remained `logged in`. No credential material was
  read. `tests/hermes/test_profile_recovery.py` exercises owned-file recovery
  from an interrupted update backup.
- AC-7 live overlap: the TUI session `20260915_133131_b9b995` dispatched
  `deleg_695a5602 / sa-0-d5ce8d7e` in `background` mode. It reported
  `PARENT_READY` at seven seconds; the parent then accepted and answered
  `FOUR` to the unrelated question while the child was visibly still running
  at 55 seconds. The child subsequently completed its isolated six-file,
  100-point result, which is available through `sessions export`.
- AC-8 durable cancellation/recovery: `kanban show t_ff5843f7 --json` records
  worker run 3 as claimed/spawned/heartbeated then reclaimed, and run 4 as
  claimed/spawned/heartbeated then `blocked`. A subsequent `kanban dispatch
  --json` reported no spawns; the task remains `blocked`, with no completion
  timestamp or result.
- AC-8 queued restart: with no dispatcher process running, task `t_60f87219`
  was created and independently listed `ready`, with no `started_at`, runs, or
  claims. After starting `aphrael-dispatcher gateway run`, the same ID remained
  durable and was claimed at `1789498532`, spawned as run `6` (PID `28420`),
  and heartbeated. Its worker correctly reported the guardrail-bound inability
  to read the scratch workspace; Hermes recorded the run and task as
  `blocked`, with no completion timestamp, result, or success overwrite. This
  is the intended honest terminal outcome for the synthetic task. The existing
  `t_9b93408c` independently supplies the verified successful terminal case.
- TUI toolset warning repair: `aphrael_guardrails` declared `tools` but lacked
  Hermes' supported `provides_tools` and `provides_hooks` manifest fields.
  Adding both declarations and rerunning setup preserved the guardrails and
  passes plugin validation. Normal profile/TUI configuration does not list the
  plugin in `platform_toolsets` and launches without that warning. Hermes
  `0.21.2` still prints a harmless warning for an *explicit* `-t
  aphrael_guardrails`: upstream `cli.py` validates built-in toolsets before
  plugin discovery, even though the plugin then loads and `TOOLSET_OK` runs.

## Final independent closeout

- **Strategerium Rules Lawyer:** PASS for AC-1–AC-11 and authorization for
  cutover cleanup; it verified the queued-restart event chain and the supported
  plugin manifest repair. AC-12 completed with the authorized removal and
  retained rollback tag.
- **Adeptus Necroneerium Shade:** **PASS**. Shade independently reran the final
  suite (**22 passed in 0.45s**), setup plus `-Surface Check`, plugin validation,
  and `git diff --check`; it reviewed the final repository, the approved
  contract, VISION, MANIFESTO, and this evidence package.
