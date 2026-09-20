# Aphrael Architecture

## Runtime boundary

Aphrael is a distribution running on the Hermes Agent runtime, natively on
Windows. Hermes owns provider authentication, sessions, memory, conversations,
agent execution, Kanban task lifecycle, delegation, and its supported chat,
TUI, and desktop surfaces. Aphrael does not embed or wrap another agent loop.

```text
ChatGPT Work -> APHRAEL.ps1 -> Hermes chat --query-file -Q
                         or Hermes chat / TUI / desktop
          |
          v
   Aphrael Hermes profile
    | identity and skills
    | Aphrael guardrail plugin + fail-closed shell hook
    | dedicated Aphrael Kanban board
          |
          v
Hermes providers, memory, sessions, delegation, and tools
```

`APHRAEL.ps1 ask` is a process boundary, not a service or agent. It invokes the
installed pinned Hermes CLI with `-p aphrael`, tags the session as a tool
integration, and returns a JSON envelope. Hermes' gateway was inspected for
this milestone; it dispatches configured messaging platforms and does not
provide a general local request API. The supported quiet single-query chat
interface is therefore the thinner and more appropriate native entry point.

Project context comes from Hermes' per-profile `projects.db`. Setup registers
this checkout as the `aphrael` Project and the front door only reads it through
Hermes' own `projects_db` module. The wrapper has no project or task database.
An explicit known name wins; an explicitly supplied caller workspace can match
a registered folder; otherwise a request stays projectless. Because Aphrael is
also the assistant's name, that project requires project/repository/workspace
wording rather than a bare “Aphrael” vocative.

An explicitly supplied existing local directory can also be used for one
invocation as an ephemeral read-only workspace. The front door derives a
temporary policy from the installed profile policy, adds only that read root,
and deletes the temporary policy after Hermes exits; it neither grants writes
nor creates a Project.

`distribution.yaml` pins Hermes to `0.21.2`, identifies the distribution-owned
files, and avoids carrying runtime state in the repository. The profile source
is the checked-out distribution and its state lives under the Hermes home.

## Profiles

Setup installs four isolated profiles: `aphrael` for the primary conversation,
`aphrael-worker` for delegated work, `aphrael-reviewer` for independent outcome
checks, and `aphrael-dispatcher` for the Kanban gateway. They share only the
explicit Aphrael board. Each has an individual configuration, policy, plugin
installation, and `.env` bootstrap file.

The provider is OpenAI Codex OAuth with no configured fallback provider. Hermes
owns the OAuth data. Manual approval is required; cron, unattended, and
single-query approval modes are denied.

## Guardrails and evidence

`aphrael_guardrails` is a supported Hermes plugin. Its native pre-tool hook and
its configured fail-closed shell hook apply the same policy. The policy has
separate read and write roots, denies private runtime paths and filesystem
indirection, permits only a small read-only terminal command set, and rejects
all other tools by default.

A reviewer can verify an exact, predeclared file outcome by recording a hash
and independent observation. A task state transition to done is not treated as
external proof. These controls constrain Hermes-managed tools; a process
running independently as the same Windows user remains outside their OS
security boundary.

## Updates and recovery

Before a profile update, setup backs up only distribution-owned profile assets.
If an update is interrupted, setup restores those assets before retrying. User
configuration, OAuth, memories, sessions, and other unowned data are preserved.
The `START_APHRAEL.ps1 -Surface Check` command detects missing guardrails,
unsafe approval configuration, missing profile isolation, and a missing board.

Telephone services, tunnels, local speech stacks, containers, WSL, public HTTP,
and custom Python API runtimes are not part of this distribution. Front Door v1
is local and synchronous; it does not add streaming or a background API.
