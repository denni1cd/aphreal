from __future__ import annotations

import importlib
import json


plugin = importlib.import_module("plugins.aphrael_guardrails")


class Context:
    profile_name = "aphrael"

    def __init__(self):
        self.hooks = {}
        self.tools = {}

    def register_hook(self, name, handler):
        self.hooks[name] = handler

    def register_tool(self, *, name, toolset, schema, handler):
        self.tools[name] = {"toolset": toolset, "schema": schema, "handler": handler}


def registered(monkeypatch):
    ctx = Context()
    plugin.register(ctx)
    return ctx


def test_native_work_tools_register_with_strict_schemas(monkeypatch):
    ctx = registered(monkeypatch)
    expected = {"aphrael_work_delegate", "aphrael_work_status", "aphrael_work_recall", "aphrael_work_recent"}
    assert expected <= set(ctx.tools)
    assert all(ctx.tools[name]["toolset"] == "aphrael_guardrails" for name in expected)
    assert ctx.tools["aphrael_work_delegate"]["schema"]["parameters"]["required"] == ["instruction"]
    assert ctx.tools["aphrael_work_status"]["schema"]["parameters"]["required"] == ["request_id"]
    assert ctx.tools["aphrael_work_recall"]["schema"]["parameters"]["required"] == []
    assert all(ctx.tools[name]["schema"]["parameters"]["additionalProperties"] is False for name in expected)


def test_native_work_tool_invocation_calls_python_bridge(monkeypatch):
    calls = []
    monkeypatch.setattr(plugin.work_bridge, "delegate_to_work", lambda instruction, base: calls.append(("delegate", instruction, base)) or {
        "request_id": "a" * 32, "pr_url": "https://github.test/pull/1", "status": "pending", "base": base})
    monkeypatch.setattr(plugin.work_bridge, "check", lambda request_id: calls.append(("status", request_id)) or {
        "request_id": request_id, "pr_url": "https://github.test/pull/1", "status": "completed + verified",
        "detail": "verified", "result": "finding"})
    monkeypatch.setattr(plugin.work_bridge, "recall", lambda request_id=None: calls.append(("recall", request_id)) or {
        "request_id": "a" * 32, "pr_url": "https://github.test/pull/1", "status": "completed + verified",
        "result": "finding"})
    monkeypatch.setattr(plugin.work_bridge, "recent", lambda limit=10: calls.append(("recent", limit)) or [{
        "request_id": "a" * 32, "status": "pending"}])
    ctx = registered(monkeypatch)

    delegated = json.loads(ctx.tools["aphrael_work_delegate"]["handler"]({"instruction": "inspect"}))
    verified = json.loads(ctx.tools["aphrael_work_status"]["handler"]({"request_id": "a" * 32}))
    recalled = json.loads(ctx.tools["aphrael_work_recall"]["handler"]({}))
    recent = json.loads(ctx.tools["aphrael_work_recent"]["handler"]({}))

    assert delegated == {"request_id": "a" * 32, "pr_url": "https://github.test/pull/1", "status": "pending", "base": "main"}
    assert verified["status"] == recalled["status"] == "completed + verified"
    assert verified["result"] == recalled["result"] == "finding"
    assert recent["requests"][0]["request_id"] == "a" * 32
    assert calls == [("delegate", "inspect", "main"), ("status", "a" * 32), ("recall", None), ("recent", 10)]
