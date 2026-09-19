"""Minimal GitHub-triggered ChatGPT Work bridge for Aphrael."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid


REPO = "denni1cd/aphreal"
BASE = "main"
TITLE_PREFIX = "APHRAEL_WORK_REQUEST"
RESULT_MARKER = "APHRAEL_WORK_RESULT"
SAFE_ID = re.compile(r"^[0-9a-f]{32}$")


def state_root() -> Path:
    override = os.environ.get("APHRAEL_WORK_STATE")
    return Path(override) if override else Path.home() / ".aphrael" / "work_bridge"


def run_gh(*args: str) -> str:
    result = subprocess.run(["gh", *args], text=True, encoding="utf-8", capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "GitHub command failed")
    return result.stdout


def gh_json(*args: str):
    return json.loads(run_gh(*args))


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def request_path(request_id: str) -> Path:
    if not SAFE_ID.fullmatch(request_id):
        raise ValueError("invalid request ID")
    return state_root() / "requests" / f"{request_id}.json"


def request_body(request_id: str, instruction: str) -> str:
    instruction_sha = digest(instruction)
    return (
        f"{TITLE_PREFIX}\n"
        f"id: {request_id}\n"
        f"instruction_sha256: {instruction_sha}\n"
        "task:\n"
        f"{instruction}\n"
    )


def delegate_to_work(instruction: str) -> dict:
    instruction = instruction.strip()
    if not instruction:
        raise ValueError("instruction must not be empty")
    request_id = uuid.uuid4().hex
    branch = f"aphrael/work-{request_id}"
    title = f"{TITLE_PREFIX} {request_id}"
    body = request_body(request_id, instruction)
    base_sha = gh_json("api", f"repos/{REPO}/git/ref/heads/{BASE}")["object"]["sha"]
    run_gh("api", "-X", "POST", f"repos/{REPO}/git/refs", "-f", f"ref=refs/heads/{branch}",
           "-f", f"sha={base_sha}")
    remote_path = f".aphrael-work/requests/{request_id}.txt"
    encoded = base64.b64encode(body.encode("utf-8")).decode("ascii")
    try:
        created = gh_json("api", "-X", "PUT", f"repos/{REPO}/contents/{remote_path}",
                          "-f", f"message=Create Aphrael Work request {request_id}",
                          "-f", f"content={encoded}", "-f", f"branch={branch}")
        pr = gh_json("api", "-X", "POST", f"repos/{REPO}/pulls", "-f", f"title={title}",
                     "-f", f"head={branch}", "-f", f"base={BASE}", "-f", f"body={body}")
    except Exception:
        # A failed creation has no usable durable request; clean up its private branch.
        subprocess.run(["gh", "api", "-X", "DELETE", f"repos/{REPO}/git/refs/heads/{branch}"],
                       capture_output=True)
        raise
    record = {
        "request_id": request_id, "instruction": instruction,
        "instruction_sha256": digest(instruction), "request_body_sha256": digest(body),
        "repository": REPO, "base": BASE, "base_sha": base_sha, "branch": branch,
        "request_file": remote_path, "request_commit_sha": created["commit"]["sha"],
        "pr_number": pr["number"], "pr_url": pr["html_url"], "status": "pending",
    }
    atomic_json(request_path(request_id), record)
    return record


def parse_result(body: str) -> dict | None:
    prefix, separator, result = body.partition("\nresult:\n")
    if not separator or not prefix.startswith(RESULT_MARKER + "\n"):
        return None
    fields = {}
    for line in prefix.splitlines()[1:]:
        key, sep, value = line.partition(": ")
        if not sep or key in fields:
            return None
        fields[key] = value
    fields["result"] = result.rstrip("\n")
    return fields


def check(request_id: str) -> dict:
    path = request_path(request_id)
    if not path.exists():
        return {"request_id": request_id, "status": "failed", "detail": "unknown request ID"}
    record = json.loads(path.read_text(encoding="utf-8"))
    expected_body = request_body(request_id, record["instruction"])
    pr = gh_json("api", f"repos/{REPO}/pulls/{record['pr_number']}")
    mismatch = (
        pr.get("title") != f"{TITLE_PREFIX} {request_id}"
        or pr.get("body") != expected_body
        or pr.get("head", {}).get("ref") != record["branch"]
        or pr.get("base", {}).get("ref") != BASE
    )
    remote = gh_json("api", "-X", "GET", f"repos/{REPO}/contents/{record['request_file']}",
                     "-f", f"ref={record['branch']}")
    remote_body = base64.b64decode(remote["content"]).decode("utf-8")
    if mismatch or remote_body != expected_body or digest(expected_body) != record["request_body_sha256"]:
        record.update(status="result mismatch", detail="originating GitHub request evidence changed")
        atomic_json(path, record)
        return record
    comments = gh_json("api", f"repos/{REPO}/issues/{record['pr_number']}/comments")
    marked = [comment for comment in comments if RESULT_MARKER in comment.get("body", "")]
    candidates = [(comment, parse_result(comment.get("body", ""))) for comment in marked]
    candidates = [(comment, result) for comment, result in candidates if result is not None]
    if marked and not candidates:
        record.update(status="result mismatch", detail="malformed APHRAEL_WORK_RESULT comment")
        atomic_json(path, record)
        return record
    if not marked:
        record.update(status="pending", detail="no APHRAEL_WORK_RESULT comment")
        atomic_json(path, record)
        return record
    matching = [(comment, result) for comment, result in candidates if result.get("id") == request_id]
    if len(matching) != 1:
        record.update(status="result mismatch", detail="missing or ambiguous result for request ID")
        atomic_json(path, record)
        return record
    comment, result = matching[0]
    if result.get("request_sha256") != record["instruction_sha256"]:
        status, detail = "result mismatch", "returned request hash does not match"
    elif result.get("result_sha256") != digest(result["result"]):
        status, detail = "result mismatch", "returned result hash does not match"
    elif result.get("status") == "failed":
        status, detail = "failed", result["result"]
    elif result.get("status") != "completed":
        status, detail = "result mismatch", "returned status is invalid"
    elif comment.get("author_association") not in {"OWNER", "MEMBER", "COLLABORATOR"}:
        status, detail = "result mismatch", "result author lacks repository authority"
    else:
        status, detail = "completed + verified", "request, result, hashes, and GitHub evidence match"
    record.update(status=status, detail=detail, result=result["result"],
                  result_sha256=digest(result["result"]), result_comment_id=comment.get("id"),
                  result_comment_url=comment.get("html_url"), result_author=comment.get("user", {}).get("login"))
    atomic_json(path, record)
    return record


def recall(request_id: str | None = None) -> dict:
    paths = [request_path(request_id)] if request_id else sorted(
        (state_root() / "requests").glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    for path in paths:
        if path.exists():
            record = json.loads(path.read_text(encoding="utf-8"))
            if record.get("status") == "completed + verified":
                return record
    raise RuntimeError("no durable verified Work result found")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    delegate = sub.add_parser("delegate")
    delegate.add_argument("instruction", nargs="?")
    delegate.add_argument("--instruction-file", type=Path)
    status = sub.add_parser("status")
    status.add_argument("request_id")
    recall_parser = sub.add_parser("recall")
    recall_parser.add_argument("request_id", nargs="?")
    args = parser.parse_args()
    try:
        if args.command == "delegate":
            if bool(args.instruction) == bool(args.instruction_file):
                raise ValueError("provide exactly one instruction or --instruction-file")
            instruction = args.instruction_file.read_text(encoding="utf-8") if args.instruction_file else args.instruction
            output = delegate_to_work(instruction)
        elif args.command == "status":
            output = check(args.request_id)
        else:
            output = recall(args.request_id)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0 if output.get("status") != "result mismatch" and output.get("status") != "failed" else 1
    except Exception as exc:
        print(json.dumps({"status": "failed", "detail": str(exc)}), file=sys.stdout)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
