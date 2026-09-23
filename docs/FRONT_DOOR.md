# Aphrael Front Door v1

## Purpose and boundary

The Front Door lets a normal Desktop ChatGPT Work conversation send ordinary
language to the real local Aphrael profile:

```text
Desktop ChatGPT Work
  -> local APHRAEL.ps1
  -> installed Hermes 0.21.2, profile aphrael
  -> Hermes sessions / memory / skills / delegation / Kanban / tools
  -> JSON envelope containing Aphrael's response
```

It is deliberately a thin process wrapper. It has no LLM loop, server, task
store, memory, or orchestration. Hermes remains authoritative. The installed
gateway was inspected and is a dispatcher for configured messaging platforms,
not a general programmatic local request endpoint. Hermes' supported
`chat --query-file ... -Q --source tool` interface is the v1 entry point.
`--query-file` preserves arbitrary request text without shell interpretation.

## Commands

From the repository checkout:

```powershell
.\APHRAEL.ps1 ask "What are you currently working on?"
.\APHRAEL.ps1 ask "What did we decide?" --resume 20260919_225802_db2e32
.\APHRAEL.ps1 ask "Run the tests" --workspace-path C:\path\to\registered\repo
.\APHRAEL.ps1 projects
.\APHRAEL.ps1 work-recent --compact
.\APHRAEL.ps1 work-status <request_id> --compact
```

`ask` returns JSON with `success`, `status`, `session_id`, `response`,
`project`, `task_id`, and `error`. The session ID is resolved from Hermes'
native session store; the wrapper does not mint it. Hermes 0.21.2 does not
return structured task metadata from quiet chat, so `task_id` remains null;
prose that merely resembles an ID is never promoted into authoritative data.
`work-recent` lists locally recorded bridge handoffs with exact request IDs and
last-observed statuses. `work-status` refreshes one request against GitHub and
returns its PR and verified result when available. These commands do not create
a Hermes conversation or replace its native task state.
The Work bridge starts PRs from `main` by default. For work on a published
development branch, explicitly ask Aphrael to use that branch as the PR base;
the bridge records and verifies the selected base. It does not infer the base
from the local checkout.

## Projects

Projects are native, per-profile Hermes Projects. Setup idempotently registers
this checkout as `aphrael`, bound to the Aphrael board. The front door resolves:

1. one explicitly named registered project;
2. one registered folder containing an explicit `--workspace-path`;
3. no project when the match is absent or ambiguous.

When a request contains exactly one explicit absolute path to an existing local
directory (or supplies it with `--workspace-path`) and that directory is not a
registered Project, the front door uses it as an ephemeral read-only workspace.
It augments the active invocation's read policy only, does not grant writes,
does not persist the path, and does not silently create a Hermes Project.

Continuation uses Hermes' session context. Task-level project inheritance is
owned by Hermes/Kanban, not reimplemented by the wrapper. Ad-hoc requests do
not create projects.

Register an established workspace without moving it:

```powershell
$record = Get-Content "$env:USERPROFILE\.aphrael\installation.json" -Raw | ConvertFrom-Json
$env:HERMES_HOME = $record.root
& $record.python -m hermes_cli.main -p aphrael project create "Void Hunter" C:\verified\existing\path --slug void-hunter
```

For a genuinely new persistent workspace, first set a personal configurable
root (for example `$env:APHRAEL_PROJECT_ROOT`), create a new non-existing child
directory beneath it, and register that exact directory with the same native
Hermes command. Never infer a personal development root, overwrite an existing
directory, or create a project for ordinary research. Front Door v1 does not
silently translate prose into filesystem/project creation; Aphrael must obtain
an explicit persistent-project request and use an authorized worker when a
write is required.

## Outputs, delegation, and verification

Source changes and durable artifacts for a resolved existing project belong in
that project's registered workspace. Projectless durable artifacts belong in a
task-specific directory below `%USERPROFILE%\AphraelWorkspace\output`.
Informational answers need no artifact. A reported path is a claim until the
file exists; controlled outcomes continue to use `aphrael-verified-action` and
the separate reviewer observation.

Conversational questions stay in the primary Aphrael session. Substantial
authorized work can use Hermes delegation. “Have Work investigate X” continues
to use `aphrael-work-bridge`; “What did Work find?” uses its status/recall tools
and the durable verified record. The front-end Work conversation is not the
delegated Work worker. Existing request metadata, idempotency, and verified
recall remain the loop boundary; the Front Door does not alter bridge triggers
or feed delegated worker prompts back through itself.

For a follow-up such as “What happened with that change?”, identify the exact
handoff through `work-recent` if the request ID is missing, then call
`work-status` or ask Aphrael to use `aphrael_work_status`. A recent row is a
local last-observed status, not a live GitHub check. `completed + verified`
establishes the integrity and authority of the returned report; inspect PR
diffs, checks, and merge state separately before claiming the code is correct,
tested, or merged.

## Desktop ChatGPT Work instruction

Paste this into a normal Desktop ChatGPT Work conversation:

> When I address Aphrael, use your local PowerShell/terminal capability to run `& 'C:\Users\Zero\python_projects\ai\aphreal\APHRAEL.ps1' ask '<my complete request>' --compact`. Parse the returned JSON and give me the `response` as Aphrael's answer, while preserving `session_id`, `project`, `task_id`, and any `error`. On my next Aphrael message, add `--resume <the prior session_id>` unless I ask for a new conversation. When Aphrael delegates to Work, preserve its bridge `request_id` and PR URL too. For a later progress question with a known request ID, call `APHRAEL.ps1 work-status <request_id> --compact`; if the ID is lost, use `APHRAEL.ps1 work-recent --compact` to identify the handoff, then refresh its status. Treat the Hermes session ID, Hermes task ID, and bridge request ID as different identifiers. Do not answer in Aphrael's place and do not invoke Hermes directly.

The request must be passed as one literal process argument; an automation
should use an argument array rather than string-building when available.

## Intentionally outside v1

There is no web/public endpoint, tunnel, cloud service, WSL/container
requirement, voice/phone integration, dashboard, generalized model router, or
streaming protocol. The boundary can later gain another local adapter without
replacing Hermes or changing this response envelope.
