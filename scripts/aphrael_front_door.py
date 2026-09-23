"""Thin local front door for the installed Aphrael Hermes profile.

This module does not implement an agent loop, memory, tasks, or persistence.
It resolves optional native Hermes Project context and invokes Hermes' supported
single-query chat interface with the real ``aphrael`` profile.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
from typing import Any
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


SESSION_RE = re.compile(r"(?m)^Session:\s+([^\s]+)\s*$")
QUOTED_WINDOWS_PATH_RE = re.compile(r'''["']([A-Za-z]:\\[^"'\r\n]+)["']''')
BARE_WINDOWS_PATH_RE = re.compile(r"(?<![\w])([A-Za-z]:\\[^\s\"'<>|?*]+)")


def installation() -> dict[str, Any]:
    record = Path.home() / ".aphrael" / "installation.json"
    if not record.is_file():
        raise RuntimeError("Aphrael is not installed; run SETUP_APHRAEL.ps1")
    value = json.loads(record.read_text(encoding="utf-8"))
    for key in ("root", "workspace", "python"):
        if not value.get(key):
            raise RuntimeError(f"Aphrael installation record is missing {key}")
    return value


def native_projects(profile_home: Path) -> list[dict[str, Any]]:
    """Read projects through Hermes' public projects_db module, never our own DB."""
    from hermes_cli import projects_db

    with projects_db.connect_closing(profile_home / "projects.db") as conn:
        return [project.to_dict() for project in projects_db.list_projects(conn)]


def _path_key(value: str | Path) -> str:
    return os.path.normcase(os.path.abspath(os.fspath(value))).rstrip("\\/")


def explicit_workspace(request: str, workspace_path: str | None = None) -> Path | None:
    """Return one explicit, existing, non-link directory supplied by the caller."""
    raw_candidates = [workspace_path] if workspace_path else [
        *QUOTED_WINDOWS_PATH_RE.findall(request),
        *BARE_WINDOWS_PATH_RE.findall(request),
    ]
    candidates: list[Path] = []
    for raw in filter(None, raw_candidates):
        candidate = Path(str(raw).rstrip(".,;!"))
        try:
            if not candidate.is_absolute() or not candidate.is_dir():
                continue
            current = Path(candidate.anchor)
            linked = False
            for part in candidate.parts[1:]:
                current /= part
                info = current.lstat()
                if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                    linked = True
                    break
            if not linked:
                candidates.append(Path(os.path.abspath(candidate)))
        except OSError:
            continue
    unique = {_path_key(path): path for path in candidates}
    return next(iter(unique.values())) if len(unique) == 1 else None


def resolve_project(
    request: str, projects: list[dict[str, Any]], workspace_path: str | None = None
) -> dict[str, Any] | None:
    """Resolve an explicit name/slug, then an explicitly supplied caller workspace."""
    folded = request.casefold()
    explicit: list[dict[str, Any]] = []
    for project in projects:
        candidates = {str(project.get("slug") or ""), str(project.get("name") or "")}
        matched = any(
            candidate and re.search(
                rf"(?<![\w-]){re.escape(candidate.casefold())}(?![\w-])", folded
            ) for candidate in candidates
        )
        # "Aphrael" is both this project's name and the assistant's name. A
        # bare vocative or artifact text must not turn an ad-hoc request into
        # project work; require project/repository wording for this one slug.
        if matched and any(candidate.casefold() == "aphrael" for candidate in candidates):
            matched = bool(re.search(
                r"\baphrael(?:\s+(?:project|repo(?:sitory)?|workspace))\b|"
                r"\b(?:project|repo(?:sitory)?|workspace)\s+(?:named\s+)?aphrael\b",
                folded,
            ))
        if matched:
            explicit.append(project)
    if len(explicit) == 1:
        return explicit[0]
    if workspace_path:
        target = _path_key(workspace_path)
        matches = []
        for project in projects:
            folders = [folder.get("path") for folder in project.get("folders", [])]
            if project.get("primary_path"):
                folders.append(project["primary_path"])
            for folder in filter(None, folders):
                root = _path_key(folder)
                if target == root or target.startswith(root + os.sep):
                    matches.append(project)
                    break
        if len(matches) == 1:
            return matches[0]
    return None


def project_summary(project: dict[str, Any] | None) -> dict[str, Any] | None:
    if project is None:
        return None
    return {
        "id": project.get("id"),
        "slug": project.get("slug"),
        "name": project.get("name"),
        "path": project.get("primary_path"),
    }


def _prompt(
    request: str, project: dict[str, Any] | None, workspace: Path | None = None
) -> str:
    boundary = (
        "You are being invoked through Aphrael Front Door v1. Treat the following "
        "as an ordinary user turn. Hermes remains authoritative for memory, sessions, "
        "skills, delegation, Kanban, tools, and verification. Do not create a project "
        "unless the user clearly asks to start a persistent project. Do not redelegate "
        "a request for an existing Work result; use aphrael-work-bridge recall/status."
    )
    if project:
        boundary += (
            f" The caller resolved native Hermes Project {project['name']!r} "
            f"({project['id']}, slug {project['slug']}) at {project.get('primary_path')}. "
            "Use that as project context and place project artifacts in its workspace."
        )
    elif workspace:
        boundary += (
            f" The caller explicitly supplied existing local workspace {str(workspace)!r}. "
            "It is an ephemeral read-only workspace context, not a registered project. "
            "Inspect it with allowed read-only tools; do not write there or claim it was "
            "registered as a Hermes Project. For Git inspection, terminal commands must be "
            "issued one per tool call, with no chaining or git -C prefix. Safe exact commands "
            "include: git status --short --branch; git branch --show-current; git rev-parse HEAD; "
            "git log -1 --oneline --decorate; git --no-pager log -5 --oneline; git remote -v."
        )
    else:
        boundary += (
            " No registered project was resolved. Keep this request projectless unless "
            "the user explicitly requests persistent project creation. Projectless durable "
            "artifacts belong in the controlled Aphrael output workspace."
        )
    return f"{boundary}\n\nUser request:\n{request}"


def invoke_hermes(
    request: str,
    install: dict[str, Any],
    project: dict[str, Any] | None,
    workspace: Path | None = None,
    resume: str | None = None,
) -> tuple[subprocess.CompletedProcess[str], str | None]:
    profile_home = Path(install["root"]) / "profiles" / "aphrael"
    env = os.environ.copy()
    env.update(
        HERMES_HOME=str(install["root"]),
        HERMES_KANBAN_HOME=str(Path(install["root"]) / "aphrael-board"),
        HERMES_KANBAN_BOARD="aphrael",
        PYTHONIOENCODING="utf-8",
    )
    env.pop("APHRAEL_POLICY_FILE", None)
    workdir = project.get("primary_path") if project else str(workspace or install["workspace"])
    args = [
        str(install["python"]), "-m", "hermes_cli.main", "-p", "aphrael",
        "chat", "--query-file", "", "-Q", "--source", "tool",
    ]
    if resume:
        args.extend(("--resume", resume))
        session_title = None
    else:
        # Hermes quiet mode intentionally omits its interactive exit footer.
        # A unique native session title lets us ask Hermes for the real ID
        # after the turn without scraping or inventing an identifier.
        session_title = f"aphrael-front-door-{uuid.uuid4().hex}"
        args.extend(("--continue", session_title, "--create-if-missing"))
    policy_path: str | None = None
    if workspace:
        base_policy_path = profile_home / "aphrael-policy.json"
        ephemeral_policy = json.loads(base_policy_path.read_text(encoding="utf-8-sig"))
        ephemeral_policy["read_roots"] = list(dict.fromkeys([
            *ephemeral_policy.get("read_roots", [ephemeral_policy["workspace"]]),
            str(workspace),
        ]))
        # Hermes tools commonly omit workdir for operations in the current
        # conversational workspace. Point relative reads and read-only terminal
        # defaults at the explicit directory; write_roots remain unchanged.
        ephemeral_policy["workspace"] = str(workspace)
        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
            json.dump(ephemeral_policy, handle)
            policy_path = handle.name
        env["APHRAEL_POLICY_FILE"] = policy_path
    with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False) as handle:
        handle.write(_prompt(request, project, workspace))
        query_path = handle.name
    args[args.index("--query-file") + 1] = query_path
    try:
        result = subprocess.run(
            args, cwd=workdir, env=env, text=True, encoding="utf-8",
            errors="replace", capture_output=True, timeout=None,
        )
        return result, session_title
    finally:
        Path(query_path).unlink(missing_ok=True)
        if policy_path:
            Path(policy_path).unlink(missing_ok=True)


def parse_hermes_output(stdout: str) -> tuple[str, str | None, str | None]:
    session_match = SESSION_RE.search(stdout)
    session_id = session_match.group(1) if session_match else None
    response = stdout[: session_match.start()].rstrip() if session_match else stdout.strip()
    response = re.sub(r"^Warning: Unknown toolsets: aphrael_guardrails\s*", "", response)
    # Hermes 0.21.2 has no structured task-id field on this interface. Natural
    # language is not authoritative evidence, so never promote text that merely
    # resembles an ID into envelope metadata.
    return response, session_id, None


def ask(args: argparse.Namespace) -> int:
    install = installation()
    projects = native_projects(Path(install["root"]) / "profiles" / "aphrael")
    workspace = explicit_workspace(args.request, args.workspace_path)
    project = resolve_project(args.request, projects, str(workspace) if workspace else None)
    ad_hoc_workspace = workspace if project is None else None
    try:
        result, session_title = invoke_hermes(
            args.request, install, project, ad_hoc_workspace, args.resume
        )
    except Exception as exc:
        envelope = {
            "success": False, "status": "error", "session_id": args.resume,
            "response": None, "project": project_summary(project), "task_id": None,
            "error": {"type": type(exc).__name__, "message": str(exc)},
        }
        print(json.dumps(envelope, ensure_ascii=False, indent=None if args.compact else 2))
        return 1
    response, session_id, task_id = parse_hermes_output(result.stdout)
    if not session_id and session_title:
        from hermes_state import SessionDB
        db = SessionDB(Path(install["root"]) / "profiles" / "aphrael" / "state.db", read_only=True)
        try:
            session_id = db.resolve_session_by_title(session_title)
        finally:
            db.close()
    ok = result.returncode == 0
    envelope = {
        "success": ok,
        "status": "completed" if ok else "error",
        "session_id": session_id or args.resume,
        "response": response or None,
        "project": project_summary(project),
        "task_id": task_id,
        "error": None if ok else {
            "type": "HermesInvocationError",
            "message": (result.stderr or result.stdout or f"Hermes exited {result.returncode}").strip(),
            "exit_code": result.returncode,
        },
    }
    print(json.dumps(envelope, ensure_ascii=False, indent=None if args.compact else 2))
    return 0 if ok else 1


def list_projects(_: argparse.Namespace) -> int:
    install = installation()
    projects = native_projects(Path(install["root"]) / "profiles" / "aphrael")
    print(json.dumps({"success": True, "projects": projects}, ensure_ascii=False, indent=2))
    return 0


def work_status(args: argparse.Namespace) -> int:
    """Expose the same durable bridge check to the Work front end."""
    from plugins.aphrael_guardrails import work_bridge

    try:
        record = work_bridge.check(args.request_id)
    except Exception as exc:
        record = {"request_id": args.request_id, "status": "failed", "detail": str(exc)}
    print(json.dumps(record, ensure_ascii=False, indent=None if args.compact else 2))
    return 1 if record.get("status") in {"failed", "result mismatch"} else 0


def work_recent(args: argparse.Namespace) -> int:
    from plugins.aphrael_guardrails import work_bridge

    try:
        output = {"requests": work_bridge.recent(args.limit)}
    except Exception as exc:
        output = {"status": "failed", "detail": str(exc)}
    print(json.dumps(output, ensure_ascii=False,
                     indent=None if args.compact else 2))
    return 1 if output.get("status") == "failed" else 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="aphrael", description="Local front door to the real Aphrael Hermes profile")
    commands = root.add_subparsers(dest="command", required=True)
    ask_parser = commands.add_parser("ask", help="Send a natural-language turn to Aphrael")
    ask_parser.add_argument("request")
    ask_parser.add_argument("--resume", help="Resume a Hermes session returned by an earlier call")
    ask_parser.add_argument("--workspace-path", help="Caller workspace used only to resolve a registered Hermes Project")
    ask_parser.add_argument("--compact", action="store_true", help="Emit compact JSON")
    ask_parser.set_defaults(handler=ask)
    projects_parser = commands.add_parser("projects", help="List native Hermes Projects registered for Aphrael")
    projects_parser.set_defaults(handler=list_projects)
    status_parser = commands.add_parser("work-status", help="Refresh one Work handoff from GitHub")
    status_parser.add_argument("request_id")
    status_parser.add_argument("--compact", action="store_true")
    status_parser.set_defaults(handler=work_status)
    recent_parser = commands.add_parser("work-recent", help="List locally recorded Work handoffs")
    recent_parser.add_argument("--limit", type=int, default=10)
    recent_parser.add_argument("--compact", action="store_true")
    recent_parser.set_defaults(handler=work_recent)
    return root


def main() -> int:
    args = parser().parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
