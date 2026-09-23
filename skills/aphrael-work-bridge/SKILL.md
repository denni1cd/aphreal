---
name: aphrael-work-bridge
description: "Delegate authorized work through Aphrael's private local queue or an explicit GitHub repository PR, and retrieve its recorded result."
---

# Aphrael Work bridge

Use `aphrael_work_delegate` for a user-authorized task that should run in Work.
Pass the complete natural-language instruction. For ordinary or private work,
omit `repository`: the request stays in Aphrael's private local Work queue.
For a public-safe GitHub repository task, pass the explicit `owner/repository`
target; the request text will appear in a PR in that repository. Never default
to the Aphrael repository when Clifton asks about another project. Do not run
the delegated task yourself. Report its exact request ID and pending state.
The default PR base is `main`. When the user names an existing development
branch as the target, pass that branch in `base`; do not infer it from a local
checkout or change it after the request is created.

Use `aphrael_work_status` with the request ID to validate the originating PR,
request file, returned ID, request hash, result hash, result author authority,
and durable GitHub comment for GitHub requests. A PR update or completion claim
alone is not success. For private requests, `completed + recorded` means the
scheduled worker reported a result and its local bytes still match their digest;
it is not independent proof that the requested action succeeded.
If a follow-up omits the request ID, use `aphrael_work_recent` to identify the
exact handoff from its instruction and PR, then call `aphrael_work_status` with
that ID. Recent entries contain last-observed status only. If multiple handoffs
could match, report the choices rather than guessing.

When asked what Work found, use `aphrael_work_recall`, optionally with the known
request ID, and answer from its durable record while stating the right evidence
level. Do not rerun the task or query Work again.
This verification binds the returned report to the request and GitHub comment;
it does not prove that the PR's code is correct, tested, or merged. Inspect the
diff and checks separately before making those claims.
