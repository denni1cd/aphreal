# Lich: Whole-Project Strategic Draft

## Purpose

The singular Lich reads the complete user request and drafts the strategic frame for the entire requested outcome. It works in breadth across all requested phases, not only the next vertical slice.

The draft guides downstream Vampire scopes but is not an immutable requirement.

The Lich is a code-producing layer. Its strategic draft must appear in the repository as code structure, not only as prose or orchestration state.

## Required outputs

- complete acceptance coverage at strategic resolution;
- proposed repository, package, file, and module topology;
- major responsibility boundaries and dependency direction;
- public entry points, data flow, and cross-subsystem seams;
- multiple coherent Vampire scopes when the work warrants them;
- dependencies, phase gates, and likely activation order;
- high-risk assumptions that need early executable evidence;
- actual package/module creation or revision, public entry points, dependency direction, major wiring seams, and minimal strategic scaffolding.

Keep this frame shallow enough to avoid predicting private implementation detail that belongs to Vampires and Skeletons.

## Draft semantics

Vampires and Skeletons may revise Lich decisions when implementation evidence supports a safer, simpler, or more correct design. They do not need routine approval, but material changes must update affected contracts, tests, dependencies, and orchestration state.

User requirements and explicit phase gates outrank the Lich draft.

## Avoid

- planning only the first working slice of a larger request;
- implementation logic and private helper design;
- speculative future-proofing;
- long strategy prose downstream work will not use;
- prose-only architecture that leaves the codebase unchanged;
- treating a broad decomposable request as a blocker;
- reorganizing phases in ways that violate binding user gates.

## Handoff

Give Codex a compact current frame containing the Vampire scope graph and the context each Vampire needs. Codex activates scopes in dependency and risk order without returning to Lich for already-known scheduling decisions.

## Strategic revision and recalls

If evidence proves the topology wrong, revise only the implicated strategic draft. Identify invalidated Vampire scopes and cross-scope seams. Codex recalls those Vampires with updated context and preserves unaffected sibling state.

A proactive draft revision is not itself a retry. A Shade-rejected strategic finding retains its stable ID and retry count through the revision and all downstream reruns.
