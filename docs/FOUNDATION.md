# Foundation guide

## Run and inspect

From the checkout in PowerShell, run `.\START_APHRAEL.ps1`. Python 3.12+ must be available as `python`; Git must be on PATH for repository inspection. The launcher runs setup if the environment or required imports are missing. Explicit setup/update is `.\SETUP_APHRAEL.ps1`. Setup installs the editable package and test dependencies in `.venv`; it needs package download access. No hosted runtime service or API key is required.

Open http://127.0.0.1:8765. If the port is occupied, use `.\START_APHRAEL.ps1 -Port 8766` and the corresponding URL. A second instance using the same runtime directory is rejected. If PowerShell blocks local scripts under your policy, use a session-only invocation permitted by your workstation policy: `powershell -ExecutionPolicy Bypass -File .\START_APHRAEL.ps1`. Stop the foreground server with Ctrl+C; shutdown can wait for an in-flight inspection to finish.

1. Confirm health shows application, persistence, executor, and registry ready. A degraded or disconnected service must be treated as unavailable; consult the displayed error and server terminal rather than assuming previous results describe current health.
2. Select `system.status`, leave Arguments as `{}`, and click **Run capability now**. Inspect the structured immediate result, including its `ok` flag.
3. Select `repository.status`, enter an objective such as “Inspect this checkout,” choose `general`, and click **Create task**. The page refreshes automatically. **Inspect** exposes timestamps, lifecycle events, result, evidence, and verification.
4. To observe cancellation, set **Pause before execution** to 20 seconds, create a task, and click **Cancel**. To cancel queued work, create a second task while the first is paused and cancel the second.
5. Try `filesystem.read` with `{"path":"README.md"}`, `filesystem.list` with `{"path":"."}`, and `filesystem.search` with `{"query":"Aphrael"}`.
6. Stop and restart the service, then inspect the same task in recent history. Its ID, events, result, and evidence are durable.

The objective is descriptive metadata. A task performs the selected capability with its explicit arguments; it does not infer steps or reason over arbitrary natural-language instructions. The optional 0–30 second pause is a development control for observing queue and cancellation behavior.

## Lifecycle and evidence

Tasks move from QUEUED to RUNNING and then COMPLETED, FAILED, or CANCELLED. One delegated worker runs at a time. Failure preserves an error and permits later work. Cancelling queued work prevents execution; cancelling running work signals the cooperative worker and prevents a later completion overwrite. An already-running read may finish, and the queue waits for it before starting the next worker. Cancellation is not a forceful termination of a filesystem or Git operation.

On restart, previously RUNNING tasks become FAILED with an interruption error and are not replayed. QUEUED tasks resume. Previously terminal results remain intact. Graceful shutdown also records active interruption honestly.

The core captures actual capability results independently of the worker's return value. Completion requires exactly one successful observed capability matching the requested tool and arguments. Evidence includes an ID, observation time, normalized arguments, result/error, and success flag; verification refers to that evidence. Verification establishes that the selected supported operation ran, not that a free-form objective was fulfilled beyond that operation.

## Capabilities and privacy

- `system.status`: hostname, OS, CPU description/count/usage sample, memory, and the Aphrael process's PID/name/memory. It does not enumerate other applications or collect process command lines. Optional unavailable CPU information is exposed as null or “unavailable.”
- `repository.status`: actual Git branch, commit, dirty flag, and up to 200 porcelain status lines, with truncation indicated. Requires Git and a valid repository with a commit.
- `filesystem.list`: allowed repository entries, at most 200 returned entries.
- `filesystem.read`: bounded UTF-8 text, up to 65,536 bytes; truncation is explicit.
- `filesystem.search`: case-insensitive literal text search, bounded traversal and bytes, up to 100 matches with snippets. It is not an exhaustive index; check `truncated`.

Paths are relative to the configured repository. Absolute/device/UNC paths, traversal, alternate data streams, symbolic links, junctions/reparse points, hard links, hidden paths (except `.env.example`), and common private/runtime paths and secret/database/log extensions are denied. Listing/search omit denied entries. This name-based exclusion is not a secret-content detector: do not place private data in otherwise allowed source files. Errors distinguish failed inspection from empty successful results.

Task objectives and inspected results are retained in `%LOCALAPPDATA%\Aphrael\tasks.sqlite3`, alongside SQLite support files and `worker.lock`. This data may contain local machine information and file excerpts. It is private local runtime data, not public acceptance evidence. There is no automatic retention/purge or encryption layer in this milestone. Keep Windows account access appropriately restricted and stop Aphrael before backing up its runtime directory. `.gitignore` provides additional safeguards, but do not move runtime data or credentials into source control.

The launcher binds only to loopback. Browser requests require the same origin and JSON mutation bodies; the service also checks host/cross-site headers. There is no account authentication. Other programs running as the local user can access it. Do not expose it through a tunnel or reverse proxy. The foundation needs no external transmission during operation; dependency installation is separate.

## Configuration

Environment variables are read at process startup. `.env.example` documents them but `.env` files are **not automatically loaded**. Set values in the PowerShell session before launching:

```powershell
$env:APHRAEL_PORT = '8765'
# Optional absolute paths:
$env:APHRAEL_DATA_DIR = Join-Path $env:LOCALAPPDATA 'Aphrael'
$env:APHRAEL_CONFIG = Join-Path $env:LOCALAPPDATA 'Aphrael\profiles.json'
```

Only set `APHRAEL_CONFIG` after creating that JSON file. `APHRAEL_REPO` optionally changes the inspected checkout/allowed filesystem root; its default is the source checkout. Runtime storage must remain outside the configured repository. Configuration files support only `default_profile` and `profiles` at the top level, for example:

```json
{
  "default_profile": "general",
  "profiles": {
    "general": {"worker": "deterministic"},
    "fast": {"worker": "deterministic"},
    "voice": null,
    "deep": null,
    "coding": null,
    "local": null
  }
}
```

Without custom configuration, only `general` is available. The standard aliases are `voice`, `fast`, `general`, `deep`, `coding`, and `local`. Missing, null, unknown, or unsupported workers produce an explicit unavailable error. Profile objects may hold provider/model metadata for future adapters; adding a model name does not install or enable a provider. `deterministic` is the only implemented worker. The API uses `default_profile` when `profile` is omitted; the browser exposes explicit profile selection.

## Adapter boundary

The browser is a small HTTP adapter over `Core`. It has no voice-provider dependency. A future conversation adapter can call the same HTTP routes or the provider-neutral Core methods and task store, while leaving registry policy and core-owned evidence verification in charge. It must translate intent into supported structured operations and handle unavailable profiles honestly.

| Operation | HTTP boundary |
| --- | --- |
| Application/persistence/executor/registry health | `GET /api/health` (503 when degraded) |
| Tool schemas and risk metadata | `GET /api/tools` |
| Available/unavailable profiles | `GET /api/profiles` |
| Immediate capability | `POST /api/tools/invoke` |
| Delegate with optional profile | `POST /api/tasks` |
| Recent tasks, including results | `GET /api/tasks?limit=50` |
| Task/events/result/evidence by ID | `GET /api/tasks/{id}` |
| Cancel queued/running task | `POST /api/tasks/{id}/cancel` with `{}` |

POST requests require `Content-Type: application/json`. For example, a task body is:

```json
{"objective":"Inspect the checkout","tool":"repository.status","arguments":{},"profile":"general","delay_seconds":2}
```

Immediate invocation uses only `tool` and `arguments`. API validation rejects extra request fields; worker/file content cannot supply approval authority. Only read-only capabilities can run. No approval issuance endpoint or state-changing capability exists. FastAPI's local `/docs` page lists the request schemas.

## Verification and deferred work

Run the complete suite from the checkout:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The suite covers configuration, storage, lifecycle, registry/policy, evidence, and API behavior. The manual walkthrough above supplements automated checks with actual Windows startup, browser controls, and restart retrieval. Exact executed totals and independent assessment belong in the closeout evidence; these instructions do not assert that a particular run passed.

Voice, telephone access, AI planning, hosted/Codex/LM Studio workers, write/shell tools, external integrations, personal memory, recurring scheduling, and automatic login startup remain deferred. [Architecture](../ARCHITECTURE.md) and [project plan](../PROJECT_PLAN.md) preserve earlier research as future options.
