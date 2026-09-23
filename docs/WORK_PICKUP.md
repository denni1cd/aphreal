# Work pickup

Aphrael can hand work to a scheduled local worker without making the task about
the Aphrael repository. The handoff has two forms:

- **Private local:** No repository is supplied. The request and worker report
  stay under `%USERPROFILE%\.aphrael\work_bridge`. The status
  `completed + recorded` confirms only that the worker's stored report is
  intact; inspect external results separately.
- **GitHub repository:** Aphrael supplies an explicit `owner/repository` and
  optional base branch. The request is placed in a PR in that repository. Its
  text is visible to people with access to that repository. The existing
  `completed + verified` status checks request/result hashes, PR identity and
  comment authority; it does not review code or prove a real-world outcome.

The scheduler uses these commands from the Aphrael checkout:

```powershell
.\APHRAEL.ps1 work-pending --compact
.\APHRAEL.ps1 work-claim <request_id> --compact
.\APHRAEL.ps1 work-complete <request_id> --result-file C:\path\to\result.txt --status completed --compact
.\APHRAEL.ps1 work-status <request_id> --compact
```

`work-pending` lists only new unclaimed records. A claim is an atomic local
reservation, so simultaneous runs cannot take the same request. After claiming,
the worker follows the complete instruction, uses its normal approval boundary,
and reports a truthful result. Use `--status failed` when work could not be
completed. The worker checks `work-status` after posting. If a process stops
after claiming, the request stays claimed for manual inspection; Aphrael does
not silently run it a second time.

Pickup requires an app-managed scheduled worker. `SETUP_APHRAEL.ps1` installs
the bridge but does not create a scheduler or start a separate agent platform.
On this workstation, the scheduled **Aphrael Work pickup** task checks the local
queue every ten minutes through a local Codex task; ChatGPT Work remains the
conversation entry point. The computer and Codex app must be available for a
local run. The scheduled task stays quiet when the queue is empty and processes
at most one new request per run. Its first unattended run must be observed
before relying on automatic pickup for consequential work.

`APHRAEL.ps1 activity --compact` combines active Hermes Kanban tasks and recent
Work handoffs. Aphrael should summarize that state in plain language and keep
the exact IDs available when needed. The Front Door starts Hermes' existing
Kanban dispatcher on conversation turns, so authorized durable Hermes tasks can
continue while the user asks another question.
