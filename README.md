# Aphrael

Aphrael is a Windows-native Hermes Agent distribution. Hermes provides the agent runtime; this repository supplies Aphrael's versioned identity, skills, guardrails, profile setup, and verification process.

The current distribution is pinned to Hermes `0.21.2` and uses the supported OpenAI Codex OAuth provider. It does not contain a web server, telephone integration, tunnel, local speech runtime, or a custom agent loop.

## Install and start

Use PowerShell in this checkout:

```powershell
.\SETUP_APHRAEL.ps1
```

The installer obtains the pinned Hermes runtime if required, creates four isolated profiles, installs the Aphrael guardrail plugin, and creates a dedicated Kanban board under `%USERPROFILE%\.hermes`. It does not read, print, import, or store OAuth credentials.

Complete the one-time provider authorization using Hermes' device flow:

```powershell
$env:HERMES_HOME = "$env:USERPROFILE\.hermes"
& "$env:USERPROFILE\.hermes\hermes-agent\venv\Scripts\python.exe" -m hermes_cli.main -p aphrael auth add openai-codex --type oauth
```

Follow the URL and code shown by Hermes. Then start Aphrael:

```powershell
.\START_APHRAEL.ps1 -Surface Chat
```

`-Surface Tui` and `-Surface Desktop` use Hermes' supported interactive surfaces. `-Surface Check` validates the installed profiles without starting a conversation.

## Boundaries

Profiles keep their own configuration, policy, workspace, and runtime state. The distribution owns only the files listed in `distribution.yaml`; profile updates preserve user configuration, memories, sessions, credentials, and unowned local files. OAuth remains Hermes-managed and is intentionally never examined by Aphrael setup or tests.

The guardrail plugin uses both a fail-closed Hermes shell hook and native tool hooks. It limits reads to the configured workspace and source checkout, limits writes to the workspace output directory, blocks private runtime paths, and requires an independent reviewer check before a controlled write can be recorded as verified. It is a policy boundary for Hermes tools, not a claim of OS isolation from another process running as the same Windows user.

See [the setup and operations guide](docs/HERMES_GUIDE.md), the [approved contract](docs/HERMES_REPLATFORM_CONTRACT.md), and [Hermes research](docs/HERMES_RESEARCH.md).
