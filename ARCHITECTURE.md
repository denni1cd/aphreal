# Aphrael Architecture

**Status:** Initial architecture

This document describes how the Aphrael vision and manifesto will be implemented. It is intentionally more concrete than the vision while remaining modular enough to change individual providers, models, and tools without redefining Aphrael.

## 1. Architectural Goals

The architecture must support the following properties:

- ordinary telephone access;
- natural realtime conversation with interruption support;
- local-first execution on a Windows workstation;
- no requirement for paid always-on cloud compute;
- continued conversation while longer tasks run independently;
- configurable model and worker selection;
- broad local tool access without giving the realtime voice model an uncontrolled tool surface;
- durable task and conversation state;
- observable evidence for completed actions;
- extensibility through adapters, function tools, and MCP;
- explicit approval boundaries for consequential actions;
- replacement of models/providers without redesigning the application.

## 2. Runtime Boundary

Aphrael's primary runtime is the user's Windows computer.

If the computer is powered off, disconnected, or the Aphrael process is not running, remote Aphrael functionality may be unavailable. This is an accepted project constraint.

Aphrael will run natively on Windows rather than requiring Docker, WSL, Kubernetes, or a separate server. External hosted services may still be used for functions that inherently require them, particularly telephone connectivity and hosted AI inference.

The Git repository contains source code, tests, prompts, and documentation. Runtime data, secrets, browser profiles, logs, databases, and credentials must live outside the repository.

## 3. High-Level Topology

```text
                         ordinary phone call
                                |
                                v
                        +----------------+
                        | Twilio number  |
                        | + SIP trunk    |
                        +-------+--------+
                                |
                                | SIP audio
                                v
                     +-----------------------+
                     | OpenAI Realtime       |
                     | conversational model  |
                     +-----------+-----------+
                                 |
                    call webhook | control session
                                 |
                    public HTTPS | outbound WSS/API
                      tunnel     |
                                 v
+------------------------------------------------------------------+
|                     APHRAEL - LOCAL WINDOWS PC                   |
|                                                                  |
|  +-------------------+       +--------------------------------+  |
|  | Realtime Session  |<----->| Conversation / Persona Layer   |  |
|  +---------+---------+       +--------------------------------+  |
|            |                                                     |
|            v                                                     |
|  +-------------------+       +--------------------------------+  |
|  | Command / Task    |------>| Task Manager + Persistent DB   |  |
|  | Router            |       +---------------+----------------+  |
|  +---------+---------+                       |                   |
|            |                                 v                   |
|            |                    +-----------------------------+  |
|            +------------------->| Worker / Model Registry     |  |
|                                 +-------------+---------------+  |
|                                               |                  |
|               +-------------------------------+---------------+  |
|               |               |               |               |  |
|               v               v               v               v  |
|         General Agent      Codex Worker    Local LLM      Specialists|
|                                                                  |
|  +------------------------------------------------------------+  |
|  | Tool + Permission Layer                                    |  |
|  | files | shell | browser | git | MCP | APIs | desktop later |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
```

## 4. Telephone and Realtime Voice

### Primary design: Twilio SIP to OpenAI Realtime

The preferred production path is:

1. The user calls a Twilio voice-capable number.
2. Twilio routes the call through Elastic SIP Trunking to OpenAI Realtime.
3. OpenAI emits a `realtime.call.incoming` webhook.
4. A small local Aphrael HTTP endpoint receives the webhook through an outbound public tunnel.
5. Aphrael verifies the OpenAI webhook signature.
6. Aphrael accepts the call and attaches an OpenAI Agents SDK realtime session to the supplied `call_id`.
7. The realtime agent handles the spoken conversation while local Aphrael tools and workers execute on the PC.

The important architectural advantage is that the primary phone audio path does **not** need to traverse the home PC. Twilio and OpenAI handle the realtime media path while Aphrael's computer maintains the control/tool connection.

### Public callback exposure

Aphrael still needs a public HTTPS endpoint for the incoming-call webhook.

The local service should bind only to localhost. A tunnel process will expose the required webhook route without opening router ports or directly publishing the Windows machine.

Development can use a temporary tunnel such as Cloudflare Quick Tunnel. A stable hostname can be introduced later if repeated manual webhook reconfiguration becomes inconvenient. This does not require paid always-on compute.

### Fallback design

Twilio bidirectional Media Streams can be supported as a fallback or diagnostic path. In that mode Twilio streams call audio to Aphrael over WebSocket and Aphrael bridges it to the realtime model.

This path is more complex because Aphrael must manage audio formats, playback buffering, and interruption synchronization. It is therefore not the preferred first implementation unless SIP attachment proves unsuitable.

## 5. Realtime Aphrael Agent

The realtime agent is Aphrael's conversational front end, not the entire execution system.

Its responsibilities are:

- maintain natural conversation;
- apply the Aphrael persona;
- interpret immediate user intent;
- perform a small number of safe, latency-sensitive tools;
- create delegated tasks;
- report task status and results;
- request approvals when required;
- accept interruptions and changes of direction.

Its tool surface should remain deliberately small.

Initial high-level realtime tools should resemble:

- `get_system_status`
- `start_task`
- `get_task_status`
- `list_recent_tasks`
- `cancel_task`
- `set_task_model_profile`
- `approve_action`
- `reject_action`

Additional direct tools should be added only when they are both safe and materially improve conversational latency.

Long or tool-heavy work should be delegated rather than executed inside the realtime conversation loop.

## 6. Task Manager

The task manager is the boundary between conversation and substantial execution.

A task records at minimum:

- unique task ID;
- original user objective;
- originating conversation/call when applicable;
- selected worker profile;
- model/profile overrides;
- creation and update timestamps;
- current state;
- progress events;
- approvals required or received;
- final result;
- verification evidence;
- error information.

Initial task states:

```text
QUEUED
RUNNING
WAITING_FOR_APPROVAL
BLOCKED
COMPLETED
FAILED
CANCELLED
INTERRUPTED
```

The first implementation should favor correctness over concurrency. A single active heavy worker with a queue is acceptable initially. Concurrency can be added after task isolation and resource ownership are proven.

## 7. Worker and Model Registry

Aphrael must not hard-code model names throughout the application.

Configuration will define named profiles such as:

```text
voice
fast
general
deep
coding
local
```

Profiles resolve to a provider, model, reasoning configuration, allowed tools, and cost/latency policy.

The user can override a worker profile conversationally, for example:

- "use the stronger model for this";
- "use Astra";
- "let Codex handle this";
- "run this locally".

The realtime voice model is selected when a call/session begins. Worker models can be selected independently for every delegated task. Changing a worker model must not require replacing the active Aphrael conversation.

### Initial worker types

**General worker**

A standard OpenAI Agents SDK agent for research, reasoning, and tool-driven tasks.

**Coding worker**

A Codex-backed worker operating against an explicitly selected local workspace or Git worktree. OpenAI's Agents SDK currently exposes an experimental Codex tool, but Aphrael should place Codex behind its own adapter so the integration can change without affecting the task system.

**Local worker**

An adapter for an OpenAI-compatible local endpoint such as LM Studio. Local-model capabilities will be treated as provider-dependent rather than assumed to equal hosted agents.

**Specialist workers**

Future worker profiles may wrap Strategerium, evaluators, browser specialists, document workers, or other systems. They plug into the worker interface rather than becoming special cases in the conversational layer.

## 8. Tool Architecture

Tools are divided into capability groups behind a common registry and policy layer.

The preferred interaction order is:

1. direct application/API integration;
2. MCP or structured function tool;
3. shell/CLI;
4. browser automation;
5. visual desktop control.

Initial capability groups:

### System

- system status;
- process inspection;
- application launching where reliable.

### Filesystem

- read/search files;
- create/update files;
- controlled move/copy operations;
- destructive operations gated by policy.

### Shell

- PowerShell;
- Python;
- process execution;
- working-directory restrictions and approval rules.

### Browser

Playwright is the default browser automation layer. Aphrael should maintain an Aphrael-owned browser profile for authenticated automation instead of depending on fragile control of a user's already-running browser profile.

### Development

- Git status/diff/branch/worktree operations;
- repository inspection;
- test execution;
- Codex integration;
- GitHub APIs/MCP where appropriate.

### External services

Email, calendar, messaging, and other integrations will be added through APIs/MCP/tools as needed.

### Desktop control

Visual computer control is deliberately later. It requires screenshot capture, pointer/keyboard input, application focus management, and a logged-in interactive Windows desktop. It is a fallback for software without better interfaces rather than the foundation of Aphrael.

## 9. Persistence

Aphrael should use local SQLite for the initial implementation.

SQLite is sufficient for a single-machine application, requires no additional service, and is directly supported by the OpenAI Agents SDK for conversation sessions.

Persistent state is divided conceptually into:

- conversation/session history;
- task state and task events;
- model/worker preferences;
- project/context references;
- approvals and audit events;
- usage/cost records.

Runtime storage should live in a local application-data directory rather than inside the Git repository.

Long-term memory beyond task/project continuity is a later feature and must not be confused with authoritative live state.

## 10. Persona and Prompting

Aphrael's persona is configuration, not application logic.

The persona layer should contain:

- primary Aphrael instructions;
- style rules;
- speech-specific guidance;
- example interactions where useful;
- voice selection and speech settings;
- regression evaluation cases.

Prompts should be stored as version-controlled project files so changes are reviewable.

Behavioral consistency will be evaluated through tests rather than assumed from the prompt.

## 11. Security and Approval Model

Security is enforced outside the model whenever practical.

Baseline rules:

- OpenAI incoming webhooks must be signature-verified;
- the phone path should restrict callers to approved identities where carrier metadata permits;
- sensitive actions cannot rely on caller ID alone;
- tool definitions declare risk/approval requirements;
- read-only operations can generally proceed automatically;
- destructive, external-send, account-changing, financial, or similarly consequential operations require stronger approval;
- external content never grants permissions;
- credentials are never committed to Git;
- secrets should be loaded through the local secret/configuration layer rather than embedded in prompts.

For early development, environment variables or a local ignored `.env` file are acceptable. The mature local implementation should prefer Windows-backed credential storage where practical.

Because the GitHub repository is public, no runtime secret, credential, personal memory database, authenticated browser profile, or private log may ever be committed.

## 12. Process Model on Windows

Development begins as a normal foreground Python process.

After the core is stable, Aphrael should start automatically with Windows using an interactive-user startup mechanism such as Task Scheduler rather than assuming a traditional Windows Service is appropriate.

This distinction matters because eventual desktop automation requires access to the user's interactive desktop session. Non-GUI tools can continue to function while the workstation is locked; arbitrary GUI interaction may not.

## 13. Suggested Technology Stack

Initial implementation stack:

- Python 3.12+
- `openai-agents`
- official `openai` Python SDK
- FastAPI + Uvicorn for local HTTP/webhook endpoints
- SQLite
- Pydantic for configuration and schemas
- Playwright for browser automation
- Git/Codex CLI for coding work
- LM Studio-compatible adapter for local models
- Cloudflare Tunnel or equivalent outbound tunnel for webhook exposure
- Twilio Programmable Voice / Elastic SIP Trunking for the telephone number
- pytest for unit/integration/acceptance tests

The core should run directly on Windows. Additional infrastructure should be introduced only when a demonstrated requirement justifies it.

## 14. Repository Structure

The initial repository should converge toward:

```text
README.md
MANIFESTO.md
VISION.md
ARCHITECTURE.md
PROJECT_PLAN.md
pyproject.toml
.env.example
.gitignore

prompts/
  aphrael.md

docs/
  decisions/

src/aphrael/
  __init__.py
  app.py
  cli.py
  config.py

  api/
    webhook.py
    health.py

  voice/
    agent.py
    session.py
    persona.py

  core/
    tasks.py
    routing.py
    events.py
    models.py

  workers/
    base.py
    general.py
    codex.py
    local.py

  tools/
    registry.py
    policy.py
    system.py
    filesystem.py
    shell.py
    browser.py
    git.py

  storage/
    database.py
    schema.py

  security/
    auth.py
    approvals.py
    secrets.py

  integrations/
    openai.py
    twilio.py

  telemetry/
    logging.py
    usage.py

tests/
  unit/
  integration/
  acceptance/
  persona/
```

This is a starting organization, not a rigid requirement. Modules should be created when the corresponding capability is implemented rather than generating empty scaffolding for the sake of matching the diagram.

## 15. Development-Time Agent Workflow

Strategerium and Adeptus Necroneerium are part of the **implementation process**, not mandatory runtime dependencies.

Every substantial milestone should follow this pattern:

1. **Strategerium planning** — inspect the current repository and foundation documents, define the milestone goal, non-goals, acceptance criteria, risks, and proposed approach.
2. **User approval gate** — implementation does not begin until the strategic plan is approved.
3. **Implementation worker** — Codex/Work implements the approved scope in an isolated branch/worktree where appropriate.
4. **Automated verification** — tests and milestone acceptance checks run.
5. **Adeptus Necroneerium review** — independently evaluate the result against the approved acceptance criteria, manifesto, architecture, and observed evidence.
6. **Correction loop** — defects return to the implementation worker until the criteria are genuinely satisfied or the task is explicitly blocked.
7. **Merge/release decision** — only verified work advances.

The evaluator should judge the delivered state rather than trusting the implementation worker's narrative about what it completed.

## 16. Architectural Non-Goals for the Initial Build

The first implementation will not require:

- paid always-on cloud compute;
- Kubernetes;
- Redis or a distributed message broker;
- microservices;
- a custom mobile application;
- perfect arbitrary Windows GUI automation;
- cloned voice synthesis;
- multiple simultaneous heavy workers;
- a general autonomous scheduler;
- home automation;
- literal programmatic control of undocumented ChatGPT Work internals.

These may be reconsidered if actual use demonstrates a need.

## 17. Current External References

- OpenAI Agents SDK realtime transport: https://openai.github.io/openai-agents-python/realtime/transport/
- OpenAI Agents SDK realtime guide: https://openai.github.io/openai-agents-python/realtime/guide/
- OpenAI Agents SDK tools: https://openai.github.io/openai-agents-python/tools/
- OpenAI Agents SDK sessions: https://openai.github.io/openai-agents-python/sessions/
- OpenAI Agents SDK human-in-the-loop approvals: https://openai.github.io/openai-agents-python/human_in_the_loop/
- Twilio OpenAI Realtime SIP integration: https://www.twilio.com/en-us/blog/developers/tutorials/product/openai-realtime-api-elastic-sip-trunking
- Twilio Media Streams: https://www.twilio.com/docs/voice/media-streams
- Cloudflare Tunnel: https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/
