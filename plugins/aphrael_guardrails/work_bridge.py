"""Private and GitHub request handoffs to an on-demand Work runner."""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid


LEGACY_REPO = "denni1cd/aphreal"
BASE = "main"
TITLE_PREFIX = "APHRAEL_WORK_REQUEST"
RESULT_MARKER = "APHRAEL_WORK_RESULT"
SAFE_ID = re.compile(r"^[0-9a-f]{32}$")
SAFE_BASE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")
SAFE_REPO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}/[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")


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
    with tempfile.NamedTemporaryFile("w", dir=path.parent, prefix=path.stem + "-",
                                     suffix=".tmp", encoding="utf-8", delete=False) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def request_path(request_id: str) -> Path:
    if not SAFE_ID.fullmatch(request_id):
        raise ValueError("invalid request ID")
    return state_root() / "requests" / f"{request_id}.json"


def claim_path(request_id: str) -> Path:
    if not SAFE_ID.fullmatch(request_id):
        raise ValueError("invalid request ID")
    return state_root() / "claims" / f"{request_id}.json"


def request_body(request_id: str, instruction: str) -> str:
    instruction_sha = digest(instruction)
    return (
        f"{TITLE_PREFIX}\n"
        f"id: {request_id}\n"
        f"instruction_sha256: {instruction_sha}\n"
        "task:\n"
        f"{instruction}\n"
    )


def delegate_to_work(instruction: str, repository: str | None = None, base: str = BASE) -> dict:
    instruction = instruction.strip()
    if not instruction:
        raise ValueError("instruction must not be empty")
    if repository is None:
        request_id = uuid.uuid4().hex
        record = {
            "request_id": request_id, "kind": "private", "instruction": instruction,
            "instruction_sha256": digest(instruction),
            "created_at": datetime.now(timezone.utc).isoformat(), "status": "pending",
        }
        atomic_json(request_path(request_id), record)
        return record
    if not SAFE_REPO.fullmatch(repository) or any(part in {".", ".."} or part.endswith(".lock") for part in repository.split("/")):
        raise ValueError("explicit GitHub owner/repository required")
    if not SAFE_BASE.fullmatch(base) or any(part in {"", ".", ".."} or part.endswith(".lock") for part in base.split("/")):
        raise ValueError("invalid base branch")
    request_id = uuid.uuid4().hex
    branch = f"aphrael/work-{request_id}"
    title = f"{TITLE_PREFIX} {request_id}"
    body = request_body(request_id, instruction)
    base_sha = gh_json("api", f"repos/{repository}/git/ref/heads/{base}")["object"]["sha"]
    run_gh("api", "-X", "POST", f"repos/{repository}/git/refs", "-f", f"ref=refs/heads/{branch}",
           "-f", f"sha={base_sha}")
    remote_path = f".aphrael-work/requests/{request_id}.txt"
    encoded = base64.b64encode(body.encode("utf-8")).decode("ascii")
    try:
        created = gh_json("api", "-X", "PUT", f"repos/{repository}/contents/{remote_path}",
                          "-f", f"message=Create Aphrael Work request {request_id}",
                          "-f", f"content={encoded}", "-f", f"branch={branch}")
        pr = gh_json("api", "-X", "POST", f"repos/{repository}/pulls", "-f", f"title={title}",
                     "-f", f"head={branch}", "-f", f"base={base}", "-f", f"body={body}")
    except Exception:
        # A failed creation has no usable durable request; clean up its private branch.
        subprocess.run(["gh", "api", "-X", "DELETE", f"repos/{repository}/git/refs/heads/{branch}"],
                       capture_output=True)
        raise
    record = {
        "request_id": request_id, "kind": "github", "instruction": instruction,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "instruction_sha256": digest(instruction), "request_body_sha256": digest(body),
        "repository": repository, "base": base, "base_sha": base_sha, "branch": branch,
        "request_file": remote_path, "request_commit_sha": created["commit"]["sha"],
        "pr_number": pr["number"], "pr_url": pr["html_url"], "status": "pending",
    }
    atomic_json(request_path(request_id), record)
    return record


def pending(limit: int = 10) -> list[dict]:
    """List new, unclaimed requests for manual recovery."""
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    directory = state_root() / "requests"
    records = []
    for path in sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime):
        if not SAFE_ID.fullmatch(path.stem) or claim_path(path.stem).exists():
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        if (record.get("request_id") != path.stem or not record.get("created_at")
                or record.get("status") != "pending"):
            continue
        records.append({key: record.get(key) for key in (
            "request_id", "kind", "instruction", "repository", "base", "pr_url", "created_at"
        )})
        if len(records) >= limit:
            break
    return records


def claim(request_id: str, worker: str = "chatgpt-work") -> dict:
    """Atomically reserve one live pending request for a Work runner."""
    if not worker or len(worker) > 80 or any(ch in worker for ch in "\r\n"):
        raise ValueError("invalid worker name")
    record = json.loads(request_path(request_id).read_text(encoding="utf-8"))
    if record.get("request_id") != request_id or not record.get("created_at"):
        raise ValueError("request is not eligible for automatic pickup")
    checked = check(request_id)
    if checked.get("status") != "pending":
        raise ValueError("request is no longer pending")
    path = claim_path(request_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"request_id": request_id, "worker": worker,
               "claimed_at": datetime.now(timezone.utc).isoformat()}
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ValueError("request has already been claimed") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)
    return {**{key: checked.get(key) for key in (
        "request_id", "kind", "instruction", "repository", "base", "pr_url", "status"
    )}, **payload}


def post_result(request_id: str, result: str, status: str = "completed") -> dict:
    """Record the worker report without claiming that its outcome was proven."""
    if status not in {"completed", "failed"}:
        raise ValueError("invalid result status")
    result = result.rstrip("\n")
    if not result.strip():
        raise ValueError("result must not be empty")
    if not claim_path(request_id).is_file():
        raise ValueError("request must be claimed before posting a result")
    record = check(request_id)
    if record.get("status") != "pending":
        raise ValueError("request is no longer pending")
    if record.get("kind") == "private":
        record.update(
            status="completed + recorded" if status == "completed" else "failed",
            result=result, result_sha256=digest(result),
            reported_at=datetime.now(timezone.utc).isoformat(),
        )
        atomic_json(request_path(request_id), record)
        return {"request_id": request_id, "status": record["status"]}
    body = (
        f"{RESULT_MARKER}\n"
        f"id: {request_id}\n"
        f"status: {status}\n"
        f"request_sha256: {record['instruction_sha256']}\n"
        f"result_sha256: {digest(result)}\n"
        f"result:\n{result}"
    )
    comment = gh_json("api", "-X", "POST",
                      f"repos/{record['repository']}/issues/{record['pr_number']}/comments",
                      "-f", f"body={body}")
    return {"request_id": request_id, "status": "reported", "worker_status": status,
            "pr_url": record["pr_url"], "result_comment_url": comment.get("html_url")}


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
    if record.get("kind") == "private":
        if digest(record.get("instruction", "")) != record.get("instruction_sha256"):
            return {**record, "status": "result mismatch", "detail": "local request text changed"}
        if record.get("result_sha256") and digest(record.get("result", "")) != record["result_sha256"]:
            return {**record, "status": "result mismatch", "detail": "local result bytes changed"}
        return record
    repository = record.get("repository", LEGACY_REPO)
    if not SAFE_REPO.fullmatch(repository):
        raise ValueError("stored repository is invalid")
    expected_body = request_body(request_id, record["instruction"])
    pr = gh_json("api", f"repos/{repository}/pulls/{record['pr_number']}")
    mismatch = (
        pr.get("title") != f"{TITLE_PREFIX} {request_id}"
        or pr.get("body") != expected_body
        or pr.get("head", {}).get("ref") != record["branch"]
        or pr.get("head", {}).get("repo", {}).get("full_name") != repository
        or pr.get("base", {}).get("ref") != record.get("base", BASE)
        or pr.get("base", {}).get("repo", {}).get("full_name") != repository
        or pr.get("html_url") != record["pr_url"]
    )
    remote = gh_json("api", "-X", "GET", f"repos/{repository}/contents/{record['request_file']}",
                     "-f", f"ref={record['branch']}")
    remote_body = base64.b64decode(remote["content"]).decode("utf-8")
    if mismatch or remote_body != expected_body or digest(expected_body) != record["request_body_sha256"]:
        record.update(status="result mismatch", detail="originating GitHub request evidence changed")
        atomic_json(path, record)
        return record
    comments = gh_json("api", f"repos/{repository}/issues/{record['pr_number']}/comments")
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
            if record.get("kind") == "private":
                record = check(record["request_id"])
            if record.get("status") in {"completed + verified", "completed + recorded"}:
                return record
    raise RuntimeError("no durable completed Work result found")


def recent(limit: int = 10) -> list[dict]:
    """List local handoffs so a follow-up can identify its exact request ID."""
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    directory = state_root() / "requests"
    records = []
    for path in sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        if not SAFE_ID.fullmatch(path.stem):
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("request_id") != path.stem:
            continue
        records.append({key: record.get(key) for key in (
            "request_id", "kind", "instruction", "repository", "status", "pr_url", "detail"
        )})
        records[-1]["pickup_state"] = "claimed" if claim_path(path.stem).exists() else (
            "eligible" if record.get("created_at") and record.get("status") == "pending" else None)
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    delegate = sub.add_parser("delegate")
    delegate.add_argument("instruction", nargs="?")
    delegate.add_argument("--instruction-file", type=Path)
    delegate.add_argument("--repository", help="GitHub owner/repository for a PR handoff; omit for a private local handoff")
    delegate.add_argument("--base", default=BASE, help="Existing GitHub base branch (default: main)")
    status = sub.add_parser("status")
    status.add_argument("request_id")
    recall_parser = sub.add_parser("recall")
    recall_parser.add_argument("request_id", nargs="?")
    recent_parser = sub.add_parser("recent")
    recent_parser.add_argument("--limit", type=int, default=10)
    pending_parser = sub.add_parser("pending")
    pending_parser.add_argument("--limit", type=int, default=10)
    claim_parser = sub.add_parser("claim")
    claim_parser.add_argument("request_id")
    claim_parser.add_argument("--worker", default="chatgpt-work")
    complete_parser = sub.add_parser("complete")
    complete_parser.add_argument("request_id")
    complete_parser.add_argument("--result-file", type=Path, required=True)
    complete_parser.add_argument("--status", choices=["completed", "failed"], default="completed")
    args = parser.parse_args()
    try:
        if args.command == "delegate":
            if bool(args.instruction) == bool(args.instruction_file):
                raise ValueError("provide exactly one instruction or --instruction-file")
            instruction = args.instruction_file.read_text(encoding="utf-8") if args.instruction_file else args.instruction
            output = delegate_to_work(instruction, args.repository, args.base)
        elif args.command == "status":
            output = check(args.request_id)
        elif args.command == "recent":
            output = {"status": "ok", "requests": recent(args.limit)}
        elif args.command == "pending":
            output = {"status": "ok", "requests": pending(args.limit)}
        elif args.command == "claim":
            output = claim(args.request_id, args.worker)
        elif args.command == "complete":
            output = post_result(args.request_id, args.result_file.read_text(encoding="utf-8"), args.status)
        else:
            output = recall(args.request_id)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0 if output.get("status") != "result mismatch" and output.get("status") != "failed" else 1
    except Exception as exc:
        print(json.dumps({"status": "failed", "detail": str(exc)}), file=sys.stdout)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
