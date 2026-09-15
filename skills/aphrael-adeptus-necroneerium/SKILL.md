---
name: aphrael-adeptus-necroneerium
description: "Optional Adeptus Necroneerium implementation and Shade review workflow. Invoke only when the user explicitly requests Adeptus Necroneerium, adeptus_necroneerium, or this skill. Never self-invoke because a task is complex."
---

# Adeptus Necroneerium on Hermes

Read [the complete source workflow](source/WORKFLOW.md) before proceeding. Preserve
all binding requirements, mode selection, executable draft responsibilities,
Shade gates, recall routing, isolated retry accounting and terminal outcomes.
Read the relevant complete role prompt under source/roles before each role:
[Lich](source/roles/lich.md), [Vampire](source/roles/vampire.md),
[Skeleton](source/roles/skeleton.md), [Shade](source/roles/shade.md).
The original [spec template](source/templates/spec.md) is also preserved.

Hermes adapter: Codex means the current Aphrael orchestrator. Named roles remain
responsibilities, not mandatory separate agent calls. When isolation benefits a
bounded assignment, use Hermes `delegate_task` and supply the complete relevant
role prompt and scoped artifacts. Independent final Shade review must have its
own context and direct observations, not merely repeat a worker's assertions.
Use available Hermes provider/model routing without fabricated model names.

Use Hermes Kanban for durable state on the explicitly selected Aphrael board,
with provisioned separate worker/reviewer homes. Keep private runtime evidence
outside Git. Native `done` is a lifecycle label, not a verified external outcome.
The source documents are retained verbatim; their relative links resolve inside
source/. Do not omit source requirements to make the adapter easier to execute.
