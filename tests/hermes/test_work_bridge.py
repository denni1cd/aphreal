from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
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
        "request_body_sha256": bridge.digest(body), "repository": bridge.LEGACY_REPO,
        "base": "main", "branch": f"aphrael/work-{request_id}",
        "request_file": f".aphrael-work/requests/{request_id}.txt",
        "pr_number": 9, "pr_url": "https://github.test/pull/9", "status": "pending",
    }
    bridge.atomic_json(bridge.request_path(request_id), record)
    return request_id, body, record


def github_responses(body, record, comments):
    return [
        {"title": f"{bridge.TITLE_PREFIX} {record['request_id']}", "body": body,
         "head": {"ref": record["branch"], "repo": {"full_name": record["repository"]}},
         "base": {"ref": "main", "repo": {"full_name": record["repository"]}},
         "html_url": record["pr_url"]},
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
    record = bridge.delegate_to_work("Do the task", "denni1cd/aphreal")
    assert record["status"] == "pending"
    assert record["pr_number"] == 12
    assert record["branch"] == "aphrael/work-" + "b" * 32
    assert bridge.request_path(record["request_id"]).is_file()
    assert record["created_at"]
    assert any("repos/denni1cd/aphreal/pulls" in call for call in calls)


def test_delegate_can_target_explicit_existing_development_branch(tmp_path, monkeypatch):
    monkeypatch.setenv("APHRAEL_WORK_STATE", str(tmp_path))
    calls = []
    replies = iter([
        {"object": {"sha": "base-sha"}},
        {"commit": {"sha": "request-sha"}},
        {"number": 13, "html_url": "https://github.test/pull/13"},
    ])
    monkeypatch.setattr(bridge, "gh_json", lambda *args: calls.append(args) or next(replies))
    monkeypatch.setattr(bridge, "run_gh", lambda *args: calls.append(args) or "")
    record = bridge.delegate_to_work("Update docs", "denni1cd/aphreal", "codex/aphrael-front-door-v1")
    assert record["base"] == "codex/aphrael-front-door-v1"
    assert any("repos/denni1cd/aphreal/git/ref/heads/codex/aphrael-front-door-v1" in call for call in calls)
    assert any("-f" in call and "base=codex/aphrael-front-door-v1" in call for call in calls)
    with pytest.raises(ValueError):
        bridge.delegate_to_work("Update docs", "denni1cd/aphreal", "../main")
    with pytest.raises(ValueError):
        bridge.delegate_to_work("Update docs", "not-a-repository")


def test_delegate_routes_to_another_repository(tmp_path, monkeypatch):
    monkeypatch.setenv("APHRAEL_WORK_STATE", str(tmp_path))
    calls = []
    replies = iter([
        {"object": {"sha": "base-sha"}},
        {"commit": {"sha": "request-sha"}},
        {"number": 4, "html_url": "https://github.test/other/pull/4"},
    ])
    monkeypatch.setattr(bridge, "gh_json", lambda *args: calls.append(args) or next(replies))
    monkeypatch.setattr(bridge, "run_gh", lambda *args: calls.append(args) or "")
    record = bridge.delegate_to_work("Fix a bug", "owner/other")
    assert record["repository"] == "owner/other"
    assert all("repos/denni1cd/aphreal" not in str(call) for call in calls)
    assert any("repos/owner/other/pulls" in call for call in calls)


def test_recent_identifies_handoffs_without_claiming_live_status(tmp_path, monkeypatch):
    request_id, _, _ = stored_request(tmp_path, monkeypatch)
    recent = bridge.recent()
    assert recent == [{
        "request_id": request_id, "instruction": "Assess architecture",
        "kind": None, "repository": "denni1cd/aphreal", "status": "pending", "pr_url": "https://github.test/pull/9", "detail": None,
        "pickup_state": None,
    }]
    assert bridge.recent(1) == recent
    with pytest.raises(ValueError):
        bridge.recent(0)


def test_scheduled_pickup_ignores_legacy_and_claims_once(tmp_path, monkeypatch):
    request_id, _, record = stored_request(tmp_path, monkeypatch)
    assert bridge.pending() == []
    record["created_at"] = "2026-09-23T00:00:00+00:00"
    bridge.atomic_json(bridge.request_path(request_id), record)
    assert [item["request_id"] for item in bridge.pending()] == [request_id]
    monkeypatch.setattr(bridge, "check", lambda _: record)
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: attempt_claim(bridge, request_id), range(2)))
    assert outcomes.count("claimed") == 1
    assert outcomes.count("request has already been claimed") == 1
    assert bridge.pending() == []
    assert bridge.recent()[0]["pickup_state"] == "claimed"


def test_private_handoff_stays_local_and_reports_without_verification(tmp_path, monkeypatch):
    monkeypatch.setenv("APHRAEL_WORK_STATE", str(tmp_path))
    monkeypatch.setattr(bridge, "gh_json", lambda *args: pytest.fail("private work reached GitHub"))
    record = bridge.delegate_to_work("Prepare a personal briefing")
    assert record["kind"] == "private"
    assert record["status"] == "pending"
    assert bridge.pending()[0]["request_id"] == record["request_id"]
    bridge.claim(record["request_id"])
    result = bridge.post_result(record["request_id"], "Briefing ready")
    assert result["status"] == "completed + recorded"
    assert bridge.check(record["request_id"])["status"] == "completed + recorded"
    assert bridge.recall(record["request_id"])["result"] == "Briefing ready"
    assert bridge.pending() == []


def test_two_private_handoffs_can_be_claimed_independently(tmp_path, monkeypatch):
    monkeypatch.setenv("APHRAEL_WORK_STATE", str(tmp_path))
    first = bridge.delegate_to_work("Research project A")
    second = bridge.delegate_to_work("Prepare project B brief")
    identifiers = {first["request_id"], second["request_id"]}
    assert {item["request_id"] for item in bridge.pending()} == identifiers
    with ThreadPoolExecutor(max_workers=2) as pool:
        claimed = list(pool.map(bridge.claim, identifiers))
    assert {item["request_id"] for item in claimed} == identifiers
    assert bridge.pending() == []


def attempt_claim(module, request_id):
    try:
        module.claim(request_id)
        return "claimed"
    except ValueError as exc:
        return str(exc)


def test_claimed_result_comment_has_verifiable_hashes(tmp_path, monkeypatch):
    request_id, _, record = stored_request(tmp_path, monkeypatch)
    bridge.atomic_json(bridge.claim_path(request_id), {"request_id": request_id})
    calls = []
    monkeypatch.setattr(bridge, "check", lambda _: record)
    monkeypatch.setattr(bridge, "gh_json", lambda *args: calls.append(args) or {
        "html_url": "https://github.test/comment/2"})
    posted = bridge.post_result(request_id, "Finished the other project.\n")
    assert posted["status"] == "reported"
    assert "repos/denni1cd/aphreal/issues/9/comments" in calls[0]
    comment_body = next(value[5:] for value in calls[0] if value.startswith("body="))
    parsed = bridge.parse_result(comment_body)
    assert parsed["id"] == request_id
    assert parsed["request_sha256"] == record["instruction_sha256"]
    assert parsed["result_sha256"] == bridge.digest(parsed["result"])
