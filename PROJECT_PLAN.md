# Aphrael Project Plan

## Current milestone: Hermes replatform

The approved [Hermes replatform contract](docs/HERMES_REPLATFORM_CONTRACT.md) is the current scope. It replaces the previous custom Python foundation with a pinned Hermes distribution on native Windows.

The milestone delivers:

- versioned Aphrael identity, skills, configuration, and an explicit ownership manifest;
- four isolated Hermes profiles and a dedicated durable Kanban board;
- supported OpenAI Codex OAuth, without handling OAuth data in project code;
- a fail-closed guardrail plugin, bounded workspace policy, manual approvals, and independent outcome verification;
- documented setup, startup, update recovery, and operator checks; and
- live acceptance evidence for conversation, tools, memory, delegation, Kanban, specialist workflows, controlled writes, persistence, and update preservation.

The installation, provider-authorized live acceptance run, cutover/rollback rehearsal, and replacement checks are complete. The obsolete custom runtime has been removed after independent Strategerium authorization; the recoverable baseline tag remains the rollback source. The remaining work is independent Adeptus Necroneerium closeout review.

## Future work

The next development loop uses Desktop ChatGPT Work as the entry point. Aphrael
keeps its Hermes conversation and delegates repository work through the durable
Work bridge. The Front Door exposes recent handoffs and a fresh status check so
follow-up questions can resolve the exact request and PR. This does not turn a
bridge result into proof that a code change is correct or merged; PR diffs and
checks require separate review.

Future capability is selected from the [vision](VISION.md) and [manifesto](MANIFESTO.md) through a new reviewed, user-approved contract. Telephone services, tunnels, local speech runtimes, local models, containers, WSL, and an Aphrael-specific HTTP application are outside this milestone.
