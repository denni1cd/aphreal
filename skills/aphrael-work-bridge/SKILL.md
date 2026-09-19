---
name: aphrael-work-bridge
description: "Delegate a repository task to ChatGPT Work through the monitored Aphrael GitHub PR protocol, or retrieve a previously verified Work result."
---

# Aphrael Work bridge

Use `scripts/aphrael_work_bridge.py delegate --instruction-file <path>` for a
user-authorized task that should run in ChatGPT Work. Do not run the delegated
task locally. Report its request ID and PR as pending until `status <id>` returns
`completed + verified`.

Use `scripts/aphrael_work_bridge.py status <id>` to validate the originating PR,
request file, returned ID, request hash, result hash, result author authority,
and durable GitHub comment. A PR update or completion claim alone is not success.

When asked what Work found, use `scripts/aphrael_work_bridge.py recall [id]` and
answer from its durable `completed + verified` record. Do not rerun the task.
