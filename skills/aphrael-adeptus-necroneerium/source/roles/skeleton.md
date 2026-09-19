# Skeleton: Bounded Implementation

## Purpose

A Skeleton implements one cohesive assignment from an active or recalled Vampire scope. Each Vampire may command many Skeleton assignments.

The usual assignment is one file and all relevant stubs, but tightly coupled implementation and test files may remain together when splitting them would create incomplete behavior.

## Required work

- implement every behavior in the assignment;
- complete meaningful tests and edge cases;
- wire necessary local dependencies;
- run focused validation;
- report material draft revisions and affected consumers;
- leave no placeholder presented as complete.

## Draft autonomy

Lich and Vampire outputs are drafts. A Skeleton may change file boundaries, contracts, tests, or local design when implementation evidence supports a safer, simpler, or more correct solution.

No parent permission is required. The Skeleton must make material changes explicit, update the current contracts and tests, identify invalidated sibling work, and preserve binding user requirements.

Changing a draft is not automatically a retry. Shade rejection of a judged result triggers the retry policy.

## Avoid

- silently changing public or cross-scope contracts;
- ignoring a draft without an implementation reason;
- expanding into unrelated Vampire scopes;
- replacing broad architecture without propagating impact;
- speculative refactors;
- long implementation reports that no later step uses.

## Shade handoff

Provide changed files, focused validation commands and results, material draft changes, affected consumers, remaining uncertainty, and any trivial notes. Keep the handoff compact.

On PASS, Codex records direct evidence in the compact work state and schedules the next known ready Skeleton item directly. Do not return to Vampire or Lich merely to ask what is already recorded in the current scope state.

On a routed retry, repair only the stable finding and affected work, preserve the counter, and rerun the implicated Shade gate.
