"""Behavioral acceptance of the real queue, evidence and persistence boundary."""
import time

from fastapi.testclient import TestClient

from aphrael.app import create_app
from aphrael.config import Settings


def wait_task(client, task_id, status=None):
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        task = client.get(f"/api/tasks/{task_id}").json()
        if task["status"] == status or (status is None and task["status"] in {"COMPLETED", "FAILED", "CANCELLED"}):
            return task
        time.sleep(0.02)
    raise AssertionError(task)


def test_api_real_work_and_persistence(tmp_path):
    settings = Settings(data_dir=tmp_path / "state")
    with TestClient(create_app(settings)) as client:
        assert client.get("/api/health").json()["healthy"]
        response = client.post("/api/tasks", json={"objective": "Inspect this workstation", "tool": "system.status"})
        assert response.status_code == 201
        task_id = response.json()["id"]
        task = wait_task(client, task_id)
        assert task["status"] == "COMPLETED", task
        assert task["verification"]["verified"]
        assert task["evidence"][0]["tool"] == "system.status"
        assert task["result"] == task["evidence"][0]["result"]
        assert [e["status"] for e in task["events"]] == ["QUEUED", "RUNNING", "COMPLETED"]
    with TestClient(create_app(settings)) as client:
        assert client.get(f"/api/tasks/{task_id}").json() == task
        assert client.get("/api/tasks").json()[0]["id"] == task_id
