# Aphrael policy and file evidence

This supported Hermes native plugin registers a pre-tool hook and two tools in
the `aphrael_guardrails` toolset. Configure a second **shell** `pre_tool_call`
hook invoking the installed `guard.py` with Hermes' Python and `fail_closed: true`.
Startup must reject missing/disabled plugins, hooks, hook consent, policy, board
selection or unexpected security configuration. A Python hook alone is insufficient
because Hermes skips exceptions raised by callbacks. The callback catches failures;
the shell hook also covers import/load failures. Keep `skills.inline_shell: false`.

Trusted setup supplies `HERMES_HOME/aphrael-policy.json`; an explicit
`APHRAEL_POLICY_FILE` overrides it for isolated tests. Its fields are:

```json
{
  "workspace": "C:/approved/workspace",
  "read_roots": ["C:/approved/workspace", "C:/projects/aphrael"],
  "write_roots": ["C:/approved/workspace/outputs"],
  "protected_paths": ["C:/approved/workspace/plugins", "C:/private/hermes"],
  "role": "worker",
  "evidence_root": "C:/private/aphrael-evidence",
  "board": "aphrael"
}
```

Roles are `parent`, `worker`, `reviewer`. Every process must explicitly select the
same `HERMES_KANBAN_BOARD`; worker and reviewer have separate Hermes homes.
Optional `read_roots` defaults to `[workspace]`. Relative file paths resolve from
`workspace`; absolute source paths can use an additional approved read root.
Only trusted setup changes this policy. Models cannot authorize new roots, change
roles, register requests, execute arbitrary shell, or write evidence. Unknown
tools deny by default. Stock Hermes file read/write/patch/search retain their
implementation; the guard validates and absolutizes their paths. Private names,
ADS, UNC/device paths, traversal, reparse points, symlinks and hardlinks are denied.
Search preflights every entry in its tree and refuses a mixed private/public tree;
search a narrower public directory when repository-root search encounters `.git`.

Terminal permits only the exact literals in `guard.py`, fixing its workdir to an
exact approved read root (default `workspace`). Git status disables fsmonitor and untracked cache. Arbitrary
terminal work requires a separate deliberate trusted policy change; the plugin
does not treat worker text or model approval as authorization.

A trusted human/setup action writes `evidence_root/requests/<request_id>.json`
before execution, binding the original approved outcome:

```json
{
  "request_id": "request1",
  "task_id": "actual-kanban-task-id",
  "board": "aphrael",
  "path": "C:/approved/workspace/outputs/result.txt",
  "sha256": "the-sha256-of-the-exact-user-requested-bytes"
}
```

`aphrael_verify_file(task_id, request_id)` is reviewer-only. It reads actual bytes,
compares their digest with the trusted requested digest and writes an independent
observation in private state, including the request digest, task, board and time.
`aphrael_verification_status(task_id, request_id)` rechecks current bytes and
binding, so stale results, modified requests and cross-task replay fail. Worker
assertions, Kanban completion and absence of errors cannot create verification.
Missing files/specs, mismatches and unavailable evidence return `verified: false`.
This supports concrete exact-file postconditions; it is not a general proof of
every conceivable action. Kanban lifecycle `done` remains distinct from verified.

The boundary assumes a trusted single-user workstation and trusted installed
runtime/skills/plugins/config. It is not an OS sandbox against another same-user
process racing path checks or changing private policy/evidence. The direct hash
observer verifies current bytes, not which actor wrote them. Human-approved
request provisioning is the authority; generating an expected hash from a
worker's output after execution would invalidate that guarantee.
