# Aphrael Project Plan

## Completed foundation: Hermes replatform

The approved [Hermes replatform contract](docs/HERMES_REPLATFORM_CONTRACT.md) is the current scope. It replaces the previous custom Python foundation with a pinned Hermes distribution on native Windows.

The milestone delivers:

- versioned Aphrael identity, skills, configuration, and an explicit ownership manifest;
- four isolated Hermes profiles and a dedicated durable Kanban board;
- supported OpenAI Codex OAuth, without handling OAuth data in project code;
- a fail-closed guardrail plugin, bounded workspace policy, manual approvals, and independent outcome verification;
- documented setup, startup, update recovery, and operator checks; and
- live acceptance evidence for conversation, tools, memory, delegation, Kanban, specialist workflows, controlled writes, persistence, and update preservation.

The installation, provider-authorized live acceptance run, cutover/rollback rehearsal, replacement checks, and independent closeout review are complete. The obsolete custom runtime has been removed after independent Strategerium authorization; the recoverable baseline tag remains the rollback source.

## Current milestone: Work-first coordination across projects

Desktop ChatGPT Work remains the conversational entry point. Aphrael keeps its
Hermes conversation and task state. Work handoffs now support private local
requests for ordinary tasks and explicit GitHub repositories for public-safe
repository changes. A combined activity view reads active Hermes tasks and Work
handoffs, while the Front Door starts Hermes' existing dispatcher so durable
tasks can continue after a turn. New Work requests can be atomically claimed by
a scheduled local runner. The runner's report remains a claim: private results
are recorded, and GitHub results have their request and comment provenance
checked separately from any review of the code or real-world outcome.

## Future work

Future capability is selected from the [vision](VISION.md) and [manifesto](MANIFESTO.md) through a new reviewed, user-approved contract. Telephone services, tunnels, local speech runtimes, local models, containers, WSL, and an Aphrael-specific HTTP application are outside this milestone.
