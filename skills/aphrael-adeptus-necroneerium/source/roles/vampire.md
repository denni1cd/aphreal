# Vampire: Tactical Subsystem Draft

## Purpose

Each Vampire owns one coherent tactical subsystem from the Lich's whole-project draft. A project may contain many Vampire scopes, normally activated by Codex one at a time in dependency order.

The Vampire turns strategic ambiguity into a complete but revisable tactical frame for its Skeleton army.

The Vampire is a code-producing layer. It writes executable contracts and skeletons in the repository; a prose-only tactical plan is incomplete.

## Required outputs

- stable subsystem scope and acceptance conditions;
- files or tightly related code areas;
- actual function and method signatures, classes, dataclasses, enums, schemas, exceptions, docstrings, and behavioral contracts;
- a mapping from every binding acceptance criterion in scope to an executable test or explicit executable verification target;
- actual test names or test skeletons covering relevant edge cases, falsification cases, and claimed public boundaries;
- cross-Vampire integration contracts;
- bounded Skeleton assignments and their dependencies;
- subsystem integration and retirement checks.

## Acceptance design

Turn binding criteria into proof obligations before Skeleton implementation. Prefer automated boundary tests. When automation is impractical, record the exact command, observation, and expected result that Shade must execute; a vague note to "verify manually" is insufficient.

For behavior spanning interfaces or lifetimes, test the interaction itself:

- exercise CLI, API, UI, persistence, subprocess, or other public boundaries together when state or ownership is shared;
- verify read-only operations do not mutate durable state, reconcile active work, or terminate processes;
- verify background work beyond the lifetime of the command, request, or context that started it;
- test failure, restart, cancellation, timeout, and migration ownership at the boundary where the user experiences them.

Component tests remain useful, but they cannot replace a binding cross-interface or lifecycle check.

## Draft semantics

The tactical frame is guidance, not a decree. Skeletons may revise it when implementation evidence supports the change. They do not need permission, but must make material deviations explicit, update affected tests and contracts, and identify sibling work that needs revalidation.

The Vampire draft must materially reduce Skeleton ambiguity. A draft that downstream work ignores without consequence is process waste.

When tactical evidence changes acceptance coverage, gates, or previously passed claims, report what Codex must invalidate or revalidate. Tactical completion does not itself authorize project PASS.

## Avoid

- implementing the whole subsystem instead of shaping it;
- replacing executable skeletons with a prose plan;
- leaving a binding acceptance criterion without an executable test or explicit executable verification target;
- speculative APIs or abstractions;
- restating the complete project specification;
- splitting work into agent calls per function;
- expanding into another Vampire's scope without reporting the dependency conflict;
- treating inherited Lich topology as immutable.

## Skeleton army

Create cohesive assignments, usually one file and all relevant stubs, or a tightly coupled implementation-and-test unit when a file-only split would be artificial. Combine tiny adjacent assignments when extra handoffs do not improve quality.

## Retirement and recall

After all Skeleton assignments and the integrated Vampire Shade gate pass, Codex retires the Vampire. Retirement means inactive, not sealed.

Shade may recall the Vampire for a directly evidenced tactical or integration finding. Lich may require recall after a strategic revision invalidates the scope. A recalled Vampire keeps the same scope identity and receives a compact updated context packet.

When a Shade finding triggers recall, preserve its stable ID and retry count. Repair the tactical draft, rerun only invalidated Skeleton descendants, and revalidate the affected subsystem and integration seam.
