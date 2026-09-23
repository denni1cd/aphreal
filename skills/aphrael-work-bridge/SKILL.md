---
name: aphrael-work-bridge
description: "Delegate a repository task to ChatGPT Work through the monitored Aphrael GitHub PR protocol, or retrieve a previously verified Work result."
---

# Aphrael Work bridge

Use `aphrael_work_delegate` for a user-authorized task that should run in
ChatGPT Work. Pass the complete natural-language instruction. Do not run the
delegated task locally. Report its request ID and PR as pending until
`aphrael_work_status` returns `completed + verified`.
The default PR base is `main`. When the user names an existing development
branch as the target, pass that branch in `base`; do not infer it from a local
checkout or change it after the request is created.

Use `aphrael_work_status` with the request ID to validate the originating PR,
request file, returned ID, request hash, result hash, result author authority,
and durable GitHub comment. A PR update or completion claim alone is not success.
If a follow-up omits the request ID, use `aphrael_work_recent` to identify the
exact handoff from its instruction and PR, then call `aphrael_work_status` with
that ID. Recent entries contain last-observed status only. If multiple handoffs
could match, report the choices rather than guessing.

When asked what Work found, use `aphrael_work_recall`, optionally with the known
request ID, and answer from its durable `completed + verified` record. Do not
rerun the task or query Work again.
This verification binds the returned report to the request and GitHub comment;
it does not prove that the PR's code is correct, tested, or merged. Inspect the
diff and checks separately before making those claims.
