from __future__ import annotations

import base64
import importlib.util
import json
from pathlib import Path
import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "plugins" / "aphrael_guardrails" / "work_bridge.py"
spec = importlib.util.spec_from_file_location("aphrael_work_bridge_test", SCRIPT)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


def stored_request(tmp_path, monkeypatch, instruction="Assess architecture"):
    monkeypatch.setenv("APHRAEL_WORK_STATE", str(tmp_path))
    request_id = "a" * 32
    body = bridge.request_body(request_id, instruction)
    record = {
        "request_id": request_id, "instruction": instruction,
        "instruction_sha256": bridge.digest(instruction),
        "request_body_sha256": bridge.digest(body), "repository": bridge.REPO,
        "base": "main", "branch": f"aphrael/work-{request_id}",
        "request_file": f".aphrael-work/requests/{request_id}.txt",
        "pr_number": 9, "pr_url": "https://github.test/pull/9", "status": "pending",
    }
    bridge.atomic_json(bridge.request_path(request_id), record)
    return request_id, body, record


def github_responses(body, record, comments):
    return [
        {"title": f"{bridge.TITLE_PREFIX} {record['request_id']}", "body": body,
         "head": {"ref": record["branch"]}, "base": {"ref": "main"}},
        {"content": base64.b64encode(body.encode()).decode()},
        comments,
    ]


def test_pending_then_verified_result_is_durable_and_recallable(tmp_path, monkeypatch):
    request_id, body, record = stored_request(tmp_path, monkeypatch)
    result_text = "A concise assessment"
    comment_body = (
        f"{bridge.RESULT_MARKER}\nid: {request_id}\nstatus: completed\n"
        f"request_sha256: {record['instruction_sha256']}\n"
        f"result_sha256: {bridge.digest(result_text)}\nresult:\n{result_text}"
    )
    responses = github_responses(body, record, [])
    monkeypatch.setattr(bridge, "gh_json", lambda *args: responses.pop(0))
    assert bridge.check(request_id)["status"] == "pending"

    responses = github_responses(body, record, [{
        "id": 77, "html_url": "https://github.test/comment/77",
        "body": comment_body, "author_association": "OWNER", "user": {"login": "owner"},
    }])
    monkeypatch.setattr(bridge, "gh_json", lambda *args: responses.pop(0))
    verified = bridge.check(request_id)
    assert verified["status"] == "completed + verified"
    assert verified["result"] == result_text
    assert bridge.recall(request_id)["result_comment_id"] == 77


def test_wrong_result_hash_is_mismatch(tmp_path, monkeypatch):
    request_id, body, record = stored_request(tmp_path, monkeypatch)
    comment = {
        "id": 1, "html_url": "https://github.test/comment/1", "author_association": "OWNER",
        "user": {"login": "owner"},
        "body": (f"{bridge.RESULT_MARKER}\nid: {request_id}\nstatus: completed\n"
                 f"request_sha256: {record['instruction_sha256']}\nresult_sha256: {'0' * 64}\n"
                 "result:\nchanged"),
    }
    responses = github_responses(body, record, [comment])
    monkeypatch.setattr(bridge, "gh_json", lambda *args: responses.pop(0))
    assert bridge.check(request_id)["status"] == "result mismatch"


def test_malformed_marker_is_mismatch(tmp_path, monkeypatch):
    request_id, body, record = stored_request(tmp_path, monkeypatch)
    responses = github_responses(body, record, [{"body": bridge.RESULT_MARKER + "\nbroken"}])
    monkeypatch.setattr(bridge, "gh_json", lambda *args: responses.pop(0))
    assert bridge.check(request_id)["status"] == "result mismatch"


def test_delegate_creates_branch_request_pr_and_state(tmp_path, monkeypatch):
    monkeypatch.setenv("APHRAEL_WORK_STATE", str(tmp_path))
    monkeypatch.setattr(bridge.uuid, "uuid4", lambda: type("U", (), {"hex": "b" * 32})())
    calls = []
    replies = iter([
        {"object": {"sha": "base-sha"}},
        {"commit": {"sha": "request-sha"}},
        {"number": 12, "html_url": "https://github.test/pull/12"},
    ])
    monkeypatch.setattr(bridge, "gh_json", lambda *args: calls.append(args) or next(replies))
    monkeypatch.setattr(bridge, "run_gh", lambda *args: calls.append(args) or "")
    record = bridge.delegate_to_work("Do the task")
    assert record["status"] == "pending"
    assert record["pr_number"] == 12
    assert record["branch"] == "aphrael/work-" + "b" * 32
    assert bridge.request_path(record["request_id"]).is_file()
    assert any("repos/denni1cd/aphreal/pulls" in call for call in calls)


def test_recent_identifies_handoffs_without_claiming_live_status(tmp_path, monkeypatch):
    request_id, _, _ = stored_request(tmp_path, monkeypatch)
    recent = bridge.recent()
    assert recent == [{
        "request_id": request_id, "instruction": "Assess architecture",
        "status": "pending", "pr_url": "https://github.test/pull/9", "detail": None,
    }]
    assert bridge.recent(1) == recent
    with pytest.raises(ValueError):
        bridge.recent(0)
