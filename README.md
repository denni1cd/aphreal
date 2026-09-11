# Aphrael

Aphrael is a local-first, voice-first personal AI assistant designed to connect natural conversation with meaningful action on the user's own computer.

The core experience is simple: call Aphrael from a phone, speak naturally, ask questions or delegate work, and let Aphrael use the appropriate models, agents, tools, and local-computer capabilities to pursue the requested outcome.

Aphrael is not a single model and is not intended to be a chatbot with voice added on top. It is a conversational execution system. The realtime conversational layer remains available while longer work can be delegated to specialist workers such as reasoning agents, coding agents, local models, Strategerium, and evaluators.

## Project Principles

The project is governed by two foundation documents:

- [MANIFESTO.md](MANIFESTO.md) — rules and principles the project must adhere to.
- [VISION.md](VISION.md) — the intended user experience, capability direction, and practical boundaries.

Architecture and implementation decisions should be derived from these documents rather than redefining them.

## Current Constraints

- Aphrael is local-first and is expected to run primarily on the user's Windows workstation.
- Remote operation may require that workstation to remain powered on, connected, and running Aphrael.
- Paid always-on cloud compute is not a prerequisite for the project.
- Hosted services may still be used when they provide necessary capabilities such as telephone connectivity or hosted AI inference.
- Work-class capabilities are a goal, but Aphrael must not depend on undocumented private ChatGPT functionality.
- Visual desktop control is a fallback where more reliable structured interfaces are unavailable.

## Development Approach

Implementation will use Strategerium for strategic planning and acceptance-criteria gating, with Adeptus Necroneerium used as an independent evaluator/reviewer where appropriate. These development agents help build Aphrael; they are not automatically runtime dependencies of Aphrael itself.

## Status

The project is currently in architecture and implementation planning.
