# Adeptus Necroneerium Working Spec

Use this template only when it materially improves implementation, completion accounting, or review. Skip it for Direct mode and small Tactical work.

This is compact orchestration state, not a ceremonial design document. Lich and Vampire sections are revisable drafts. User requirements and explicit acceptance gates remain binding.

## Complete request

<!-- State the complete requested outcome, including every supplied phase. -->

## Binding requirements and acceptance inventory

<!-- Record observable user requirements, compatibility constraints, and phase gates. -->

| ID | Required outcome | Executable test or exact verification target | State |
| --- | --- | --- | --- |
|  |  |  | Unverified |

Binding item states are `verified`, `failed`, or `unverified`. Pending implementation remains `unverified`; any `failed` or `unverified` binding item prohibits PASS.

## Selected mode

Mode: <!-- Direct, Tactical, or Adeptus -->

Reason: <!-- Explain why the selected hierarchy is proportional to the task. -->

## Lich: whole-project strategic draft

### Proposed topology

<!-- Cover the complete request in breadth: packages, modules, major responsibilities, public seams, and dependency direction. Avoid private implementation detail. -->

### Cross-scope contracts and risks

<!-- Record only interfaces, compatibility obligations, and high-risk assumptions that affect more than one Vampire scope. -->

### Vampire scope graph

| Scope ID | Tactical subsystem | Dependencies | Acceptance coverage | State |
| --- | --- | --- | --- | --- |
| V-1 |  |  |  | Pending |

States: Pending, Active, Retired-PASS, Recalled, Invalidated, Blocked, Terminal-FAIL.

## Active or recalled Vampire: tactical draft

Scope ID:

Relevant Lich draft revision:

### Files, contracts, and tests

<!-- Define the subsystem's files or code areas, signatures, schemas, exceptions, behaviors, edge cases, and integration checks. Map every binding criterion in scope to an executable test or an exact command, observation, and expected result. Include cross-interface, read-only mutation, and background-lifetime checks when relevant. This is guidance and may be revised from implementation evidence. -->

### Skeleton assignments

| Item ID | Cohesive implementation unit | Dependencies | Focused validation | State |
| --- | --- | --- | --- | --- |
|  |  |  |  | Pending |

### Retirement conditions

<!-- State the subsystem behavior and integration evidence required for the Vampire Shade gate to pass. -->

## Draft revision and invalidation log

<!-- Record only material changes that affect contracts, dependencies, siblings, passed work, or acceptance coverage. Lower responsibilities do not need permission to make supported changes. -->

| Revision | Evidence/reason | Draft changed | Affected work | Required revalidation |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Shade review gates

### Skeleton evidence

<!-- Compact direct evidence for each completed Skeleton item. -->

### Vampire integration evidence

<!-- Direct evidence required before retiring the active Vampire. -->

### Phase and project evidence

<!-- Full acceptance coverage, real boundary checks, exact test totals, README commands, documentation audit, and final cleanup. -->

| Acceptance ID | State | Direct evidence | Independent boundary check |
| --- | --- | --- | --- |
|  | Unverified |  |  |

## Finding and recall state

Initial judged work is attempt 0. First rejection triggers retry 1; rejection of retry 1 triggers retry 2; rejection after retry 2 terminates the project. Never pool or reset counters.

| Scope path | Finding ID | Judged item and root defect | Responsible level | Triggered retry | Affected descendants/seams | Status |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

For a Vampire recall, preserve the scope ID, relevant drafts, finding identity, retry state, invalidated passes, unaffected siblings, and retirement conditions.

## Completion state

Verified acceptance IDs:

Failed acceptance IDs:

Unverified acceptance IDs:

Next dependency-ready scope/item:

Invalidated work awaiting revalidation:

Current outcome: <!-- IN PROGRESS, PASS, BLOCKED, or TERMINAL FAIL -->

Project PASS is forbidden while a binding acceptance item is `failed` or `unverified`, or a required Vampire scope, phase gate, or project gate remains incomplete.

Before final output, confirm every binding requirement and gate has direct evidence. BLOCKED requires a genuine external blocker that prevents all remaining feasible progress. Terminal FAIL requires one stable finding rejected with evidence at attempt 0, retry 1, and retry 2.
