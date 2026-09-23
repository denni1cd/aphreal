# Aphrael

Aphrael is a Windows-native Hermes Agent distribution. Hermes provides the agent runtime; this repository supplies Aphrael's versioned identity, skills, guardrails, profile setup, and verification process.

The current distribution is pinned to Hermes `0.21.2` and uses the supported OpenAI Codex OAuth provider. It does not contain a web server, telephone integration, tunnel, local speech runtime, or a custom agent loop.

## Install and start

Use PowerShell in this checkout:

```powershell
.\SETUP_APHRAEL.ps1
```

The installer obtains the pinned Hermes runtime if required, creates four isolated profiles, installs the Aphrael guardrail plugin, and creates a dedicated Kanban board under `%USERPROFILE%\.hermes`. It does not read, print, import, or store OAuth credentials.

Hermes reuses supported Codex authentication from its private profile state.
Then start Aphrael:

```powershell
.\START_APHRAEL.ps1 -Surface Chat
```

`-Surface Tui` and `-Surface Desktop` use Hermes' supported interactive surfaces. `-Surface Check` validates the installed profiles without starting a conversation.

For a local programmatic turn from Desktop ChatGPT Work or PowerShell, use the
Front Door:

```powershell
.\APHRAEL.ps1 ask "What are you currently working on?"
```

It emits a JSON envelope containing success/status, the real Hermes session ID,
Aphrael's response, optional native Hermes Project context, a task ID field
(null where this Hermes interface has none), and error details. Continue the same Hermes
conversation with `--resume <session_id>`. See
[Front Door operations](docs/FRONT_DOOR.md) for the exact Desktop Work
instruction and project/output rules.

To follow work that Aphrael delegated to ChatGPT Work, use `work-recent` to find
the bridge request ID and `work-status <request_id>` to refresh its GitHub result.

Run repository verification with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Boundaries

Profiles keep their own configuration, policy, workspace, and runtime state. The distribution owns only the files listed in `distribution.yaml`; profile updates preserve user configuration, memories, sessions, credentials, and unowned local files. OAuth remains Hermes-managed and is intentionally never examined by Aphrael setup or tests.

The guardrail plugin uses both a fail-closed Hermes shell hook and native tool hooks. It limits reads to the configured workspace and source checkout, limits writes to the workspace output directory, blocks private runtime paths, and requires an independent reviewer check before a controlled write can be recorded as verified. It is a policy boundary for Hermes tools, not a claim of OS isolation from another process running as the same Windows user.

See [Front Door operations](docs/FRONT_DOOR.md), [the setup and operations guide](docs/HERMES_GUIDE.md), the [approved contract](docs/HERMES_REPLATFORM_CONTRACT.md), and [Hermes research](docs/HERMES_RESEARCH.md).
