"""Verify one ChatGPT Work bridge result from the originating GitHub PR."""

import argparse
import base64
import json
import subprocess
import sys


REPO = "denni1cd/aphreal"
PREFIX = "APHRAEL_WORK_REQUEST"
RESULT = "APHRAEL_WORK_RESULT"


def gh(*args):
    run = subprocess.run(["gh", *args], capture_output=True, text=True)
    if run.returncode:
        raise RuntimeError(run.stderr.strip() or run.stdout.strip())
    return json.loads(run.stdout)


def verify(request_id):
    token = f"APHRAEL_WORK_BRIDGE_SUCCESS_{request_id}".encode()
    prs = gh("pr", "list", "--repo", REPO, "--state", "all", "--limit", "100",
             "--json", "number,title,body,headRefName")
    matches = [pr for pr in prs if pr["title"].startswith(PREFIX)
               and f"id: {request_id}" in pr["body"]
               and PREFIX in pr["body"]]
    if not matches:
        return "pending", "request PR not found"
    if len(matches) != 1:
        return "result mismatch", "request ID appears on multiple PRs"

    pr = matches[0]
    number = pr["number"]
    comments = gh("api", f"repos/{REPO}/issues/{number}/comments")
    results = [c["body"] for c in comments if RESULT in c["body"]]
    if any(f"id: {request_id}" in body and "status: failed" in body for body in results):
        return "failed", f"Work reported failure on PR #{number}"
    if results and not any(f"id: {request_id}" in body and "status: completed" in body
                           for body in results):
        return "result mismatch", f"completion comment ID/status differs on PR #{number}"

    run = subprocess.run(
        ["gh", "api", "-X", "GET", f"repos/{REPO}/contents/work_bridge_test.txt",
         "-f", f"ref={pr['headRefName']}"], capture_output=True, text=True)
    if run.returncode:
        if "404" in run.stderr:
            return "pending", f"artifact absent on PR #{number} head branch"
        raise RuntimeError(run.stderr.strip())
    artifact = json.loads(run.stdout)
    actual = base64.b64decode(artifact["content"])
    if actual != token:
        return "result mismatch", f"artifact bytes differ on PR #{number} head branch"
    if not any(f"id: {request_id}" in body and "status: completed" in body
               for body in results):
        return "pending", f"artifact matches but completion result absent on PR #{number}"
    return "completed + verified", f"PR #{number}, artifact bytes and completion ID match"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("request_id")
    args = parser.parse_args()
    try:
        status, detail = verify(args.request_id)
    except (RuntimeError, ValueError, KeyError) as exc:
        status, detail = "failed", str(exc)
    print(f"{status}: {detail}")
    return 0 if status == "completed + verified" else 1


if __name__ == "__main__":
    sys.exit(main())
