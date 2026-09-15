# Hermes replatform verification record

Status: **in progress; not a completion claim.** This record separates actual
live observations from acceptance criteria still requiring work.

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

- Capture the live evidence in a criterion-by-criterion package and exercise
  stale-memory-versus-live-state, update interruption recovery, and a fully
  inspectable delegated child result.
- Complete the required independent Strategerium closeout review.
- Map replacement guarantees, rehearse rollback in an isolated checkout, then
  remove the obsolete custom runtime and its coupled tests only after the
  remaining replacement checks pass.
- Re-run Adeptus Shade and Strategerium reviews after those changes. Until then
  the migration is incomplete and the old runtime remains intentionally.
