---
name: aphrael-task-coordination
description: "Coordinate ongoing Aphrael tasks and answer progress questions across Hermes Kanban and the Work bridge."
---

# Task coordination

When Clifton asks what is underway or asks about an earlier task, inspect real
state before answering. Use native Hermes Kanban for durable Hermes tasks and
`aphrael_work_recent` for Work handoffs. Refresh the relevant Work request with
`aphrael_work_status` before stating its current state. Match by objective,
project, and request ID; if more than one task fits, identify the choices.

Give one concise, natural update: what is running, what finished, what is
blocked, and what needs Clifton. Keep IDs and PR links available for follow-up.
For a general “what's underway?” question, lead with currently active work and
at most one or two relevant recent outcomes. Do not enumerate old acceptance
tests, synthetic blocked cards, or every historical Work request; mention them
only when Clifton asks about that history or they affect current work. If
nothing is active, say so directly in one or two sentences.
Native Kanban `done` and Work bridge `completed + verified` mean different
things. Private Work `completed + recorded` is only a worker report. None by
itself proves an external artifact or code change is correct.

For substantial work that should continue after a conversational turn, use a
durable Hermes Kanban task when its workspace and permissions are authorized.
Return the native task ID and a plain-language next step, then remain available
for another question. Do not hold the Front Door turn open for a long synchronous
delegation when a durable background task is appropriate. If the dispatcher or
required worker capability is unavailable, report that instead of claiming the
work is running.

For Work requests, use `aphrael-work-bridge`. Pass the target repository and
base branch only for public-safe GitHub work. Private tasks stay in the local
Work queue. Other work can use Hermes tools, delegation, and Kanban within its
existing authorization.
