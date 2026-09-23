# Work pickup

Aphrael can hand work to the active ChatGPT Work conversation without making the task about
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

The active Work conversation uses the exact request ID returned by Aphrael:

```powershell
.\APHRAEL.ps1 work-claim <request_id> --compact
.\APHRAEL.ps1 work-complete <request_id> --result-file C:\path\to\result.txt --status completed --compact
.\APHRAEL.ps1 work-status <request_id> --compact
```

`work-pending` is a manual recovery command, not a recurring pickup check. It
lists only new unclaimed records. A claim is an atomic local
reservation, so simultaneous runs cannot take the same request. After claiming,
the worker follows the complete instruction, uses its normal approval boundary,
and reports a truthful result. Use `--status failed` when work could not be
completed. The worker checks `work-status` after posting. If a process stops
after claiming, the request stays claimed for manual inspection; Aphrael does
not silently run it a second time.

Pickup is on demand in the same ChatGPT Work turn that asked Aphrael to delegate.
The Work conversation claims only the returned request ID, performs the task,
and records its result. This spends no model turns checking an empty queue.
`SETUP_APHRAEL.ps1` installs the bridge but does not create a scheduler. If the
conversation ends before pickup, the request remains pending. Resume it by
request ID; `work-pending` can recover the ID when it is lost. Do not restart
the old recurring **Aphrael Work pickup** automation.

`APHRAEL.ps1 activity --compact` combines active Hermes Kanban tasks and recent
Work handoffs. Aphrael should summarize that state in plain language and keep
the exact IDs available when needed. The Front Door starts Hermes' existing
Kanban dispatcher on conversation turns, so authorized durable Hermes tasks can
continue while the user asks another question.
