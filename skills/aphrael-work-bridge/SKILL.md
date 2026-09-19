---
name: aphrael-work-bridge
description: "Delegate a repository task to ChatGPT Work through the monitored Aphrael GitHub PR protocol, or retrieve a previously verified Work result."
---

# Aphrael Work bridge

Use `aphrael_work_delegate` for a user-authorized task that should run in
ChatGPT Work. Pass the complete natural-language instruction. Do not run the
delegated task locally. Report its request ID and PR as pending until
`aphrael_work_status` returns `completed + verified`.

Use `aphrael_work_status` with the request ID to validate the originating PR,
request file, returned ID, request hash, result hash, result author authority,
and durable GitHub comment. A PR update or completion claim alone is not success.

When asked what Work found, use `aphrael_work_recall`, optionally with the known
request ID, and answer from its durable `completed + verified` record. Do not
rerun the task or query Work again.
