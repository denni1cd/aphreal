from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "aphrael_front_door.py"
spec = importlib.util.spec_from_file_location("aphrael_front_door", SCRIPT)
front_door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(front_door)


PROJECTS = [
    {
        "id": "p_12345678",
        "slug": "aphrael",
        "name": "Aphrael",
        "primary_path": r"C:\work\aphrael",
        "folders": [{"path": r"C:\work\aphrael", "is_primary": True}],
    },
    {
        "id": "p_87654321",
        "slug": "void-hunter",
        "name": "Void Hunter",
        "primary_path": r"C:\work\void-hunter",
        "folders": [{"path": r"C:\work\void-hunter", "is_primary": True}],
    },
]


def test_explicit_known_project_resolves():
    assert front_door.resolve_project("Review the Aphrael project", PROJECTS)["id"] == "p_12345678"
    assert front_door.resolve_project("Help with Void Hunter", PROJECTS)["id"] == "p_87654321"


def test_generic_request_stays_projectless():
    assert front_door.resolve_project("What is Hermes doing for us?", PROJECTS) is None
    assert front_door.resolve_project("Aphrael, what are you doing?", PROJECTS) is None
    assert front_door.resolve_project("Write an Aphrael acceptance artifact", PROJECTS) is None


def test_caller_workspace_resolves_registered_project():
    resolved = front_door.resolve_project(
        "Run the tests", PROJECTS, r"C:\work\aphrael\tests"
    )
    assert resolved["slug"] == "aphrael"


def test_ambiguous_explicit_match_stays_projectless():
    duplicate = {**PROJECTS[0], "id": "p_other", "slug": "other", "name": "Aphrael"}
    assert front_door.resolve_project("Aphrael", [PROJECTS[0], duplicate]) is None


def test_parse_real_hermes_quiet_footer():
    response, session_id, task_id = front_door.parse_hermes_output(
        "Aphrael response\n\nSession:        20260919_abc123\nDuration: 1s\n"
    )
    assert response == "Aphrael response"
    assert session_id == "20260919_abc123"
    assert task_id is None


def test_known_runtime_startup_warning_is_not_part_of_response():
    response, _, _ = front_door.parse_hermes_output(
        "Warning: Unknown toolsets: aphrael_guardrails\nActual answer"
    )
    assert response == "Actual answer"


def test_task_identifier_is_not_fabricated():
    _, _, task_id = front_door.parse_hermes_output("Created Hermes task t_deadbeef\n")
    assert task_id == "t_deadbeef"
