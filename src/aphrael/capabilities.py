"""Bounded local inspection. Policy is applied here, outside worker control."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
import platform
import socket
import stat
import subprocess
from typing import Callable, Literal
from uuid import uuid4

import psutil
from pydantic import BaseModel, ConfigDict, Field


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Empty(Schema):
    pass


class ListInput(Schema):
    path: str = "."
    limit: int = Field(default=100, ge=1, le=200)


class ReadInput(Schema):
    path: str
    max_bytes: int = Field(default=16384, ge=1, le=65536)


class SearchInput(ListInput):
    query: str = Field(min_length=1, max_length=200)
    limit: int = Field(default=30, ge=1, le=100)


class SystemOutput(Schema):
    hostname: str
    os: str
    cpu: dict
    memory: dict
    process: dict


class RepositoryOutput(Schema):
    branch: str
    commit: str
    dirty: bool
    changed_files: list[str]
    truncated: bool


class ListingOutput(Schema):
    path: str
    entries: list[dict]
    truncated: bool


class ReadOutput(Schema):
    path: str
    content: str
    bytes_read: int
    truncated: bool


class SearchOutput(Schema):
    path: str
    query: str
    matches: list[dict]
    files_scanned: int
    truncated: bool


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    handler: Callable[[dict], dict]
    risk: Literal["read_only", "state_changing", "approval_required"] = "read_only"


class Registry:
    def __init__(self, repo: Path):
        self.repo = Path(repo).resolve(strict=True)
        self._tools: dict[str, Tool] = {}
        for tool in (
            Tool("system.status", "Inspect this workstation and Aphrael process", Empty, SystemOutput, self._system),
            Tool("repository.status", "Inspect current repository Git state", Empty, RepositoryOutput, self._repository),
            Tool("filesystem.list", "List allowed repository entries", ListInput, ListingOutput, self._list),
            Tool("filesystem.read", "Read bounded UTF-8 repository text", ReadInput, ReadOutput, self._read),
            Tool("filesystem.search", "Search literal text in bounded repository files", SearchInput, SearchOutput, self._search),
        ):
            self.register(tool)

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError("Tool is already registered")
        if tool.risk not in {"read_only", "state_changing", "approval_required"}:
            raise ValueError("Unknown tool risk")
        self._tools[tool.name] = tool

    def describe(self) -> list[dict]:
        return [{"name": t.name, "description": t.description, "risk": t.risk,
                 "input_schema": t.input_model.model_json_schema(),
                 "output_schema": t.output_model.model_json_schema()}
                for t in self._tools.values()]

    def validate(self, name: str, arguments: dict) -> dict:
        if name not in self._tools:
            raise ValueError("Unknown tool")
        tool = self._tools[name]
        if tool.risk != "read_only":
            raise PermissionError("Policy permits read-only tools only; trusted approval is unavailable")
        return tool.input_model.model_validate(arguments).model_dump()

    def invoke(self, name: str, arguments: dict) -> dict:
        envelope = {"id": str(uuid4()), "tool": name, "arguments": arguments,
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                    "ok": False, "result": None, "error": None}
        try:
            args = self.validate(name, arguments)
            envelope["arguments"] = args
            tool = self._tools[name]
            envelope["result"] = tool.output_model.model_validate(tool.handler(args)).model_dump()
            envelope["ok"] = True
        except Exception as exc:
            # Never include OS exception strings: they may disclose private absolute paths.
            envelope["error"] = {"type": type(exc).__name__, "message": self._error(exc)}
        return envelope

    @staticmethod
    def _error(exc: Exception) -> str:
        if isinstance(exc, PermissionError):
            return "Policy denied this operation or path"
        if isinstance(exc, FileNotFoundError):
            return "Requested file or required program was not found"
        if isinstance(exc, UnicodeError):
            return "Requested file is not UTF-8 text"
        if isinstance(exc, ValueError):
            return "Unknown tool, invalid arguments, or invalid tool output"
        return "Capability execution failed; check the requested operation and local prerequisites"

    @staticmethod
    def _sensitive(part: str) -> bool:
        lower = part.lower()
        return ((lower.startswith(".") and lower != ".env.example") or
                lower in {"runtime", "secrets", "private", "memory", "logs", "node_modules", "__pycache__", "venv"} or
                lower.endswith((".db", ".sqlite", ".sqlite3", ".pem", ".key", ".pfx", ".log")))

    def _path(self, value: str) -> Path:
        # Reject Windows alternate data streams and device/UNC paths on every platform.
        if "\x00" in value or ":" in value or value.startswith(("\\", "/")):
            raise PermissionError("Path denied")
        relative = Path(value)
        if relative.is_absolute() or ".." in relative.parts or any(self._sensitive(p) for p in relative.parts):
            raise PermissionError("Path denied")
        path = self.repo / relative
        current = self.repo
        for part in relative.parts:
            current = current / part
            info = current.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise PermissionError("Links and reparse points denied")
            if stat.S_ISREG(info.st_mode) and info.st_nlink > 1:
                raise PermissionError("Hard links denied")
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(self.repo):
            raise PermissionError("Path denied")
        return resolved

    def _relative(self, path: Path) -> str:
        return path.relative_to(self.repo).as_posix()

    def _bytes(self, path: Path, limit: int) -> tuple[bytes, bool]:
        path = self._path(self._relative(path))
        before = path.stat()
        with path.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino) or opened.st_nlink > 1:
                raise PermissionError("File changed during inspection")
            self._path(self._relative(path))
            data = stream.read(limit + 1)
        return data[:limit], len(data) > limit

    def _list(self, args: dict) -> dict:
        path = self._path(args["path"])
        entries, scanned = [], 0
        with os.scandir(path) as children:
            for child in children:
                scanned += 1
                if scanned > 1000 or len(entries) >= args["limit"]:
                    return {"path": self._relative(path), "entries": entries, "truncated": True}
                try:
                    allowed = self._path(self._relative(Path(child.path)))
                except (PermissionError, FileNotFoundError):
                    continue
                entries.append({"name": allowed.name, "kind": "directory" if allowed.is_dir() else "file"})
        return {"path": self._relative(path), "entries": entries, "truncated": False}

    def _read(self, args: dict) -> dict:
        path = self._path(args["path"])
        data, truncated = self._bytes(path, args["max_bytes"])
        # A byte limit may cut the final UTF-8 character; omit that partial character only.
        import codecs
        content = codecs.getincrementaldecoder("utf-8")().decode(data, final=not truncated)
        if "\x00" in content:
            raise ValueError("Binary text denied")
        return {"path": self._relative(path), "content": content, "bytes_read": len(data), "truncated": truncated}

    def _search(self, args: dict) -> dict:
        root = self._path(args["path"])
        matches, scanned, visited, total_bytes = [], 0, 0, 0
        truncated = False
        pending = [root]
        while pending:
            path = pending.pop()
            visited += 1
            if visited > 1000 or total_bytes >= 2_000_000 or len(matches) >= args["limit"]:
                truncated = True
                break
            try:
                path = self._path(self._relative(path))
            except (PermissionError, FileNotFoundError):
                continue
            if path.is_dir():
                with os.scandir(path) as children:
                    for index, child in enumerate(children):
                        if index >= 1000 or len(pending) >= 1000:
                            truncated = True
                            break
                        pending.append(Path(child.path))
                continue
            data, cut = self._bytes(path, min(65536, 2_000_000 - total_bytes))
            scanned += 1
            total_bytes += len(data)
            truncated = truncated or cut
            try:
                content = data.decode("utf-8")
            except UnicodeError:
                continue
            if "\x00" in content:
                continue
            for number, line in enumerate(content.splitlines(), 1):
                if args["query"].casefold() in line.casefold():
                    matches.append({"path": self._relative(path), "line": number, "text": line[:300]})
                    if len(matches) >= args["limit"]:
                        truncated = True
                        break
        return {"path": self._relative(root), "query": args["query"], "matches": matches,
                "files_scanned": scanned, "truncated": truncated}

    def _system(self, args: dict) -> dict:
        memory = psutil.virtual_memory()
        process = psutil.Process()
        return {"hostname": socket.gethostname(), "os": platform.platform(),
                "cpu": {"description": platform.processor() or "unavailable", "logical_count": psutil.cpu_count(),
                        "usage_percent": psutil.cpu_percent(interval=0.1)},
                "memory": {"total_bytes": memory.total, "available_bytes": memory.available, "usage_percent": memory.percent},
                "process": {"pid": process.pid, "name": process.name(), "memory_bytes": process.memory_info().rss}}

    def _repository(self, args: dict) -> dict:
        def git(*parts: str) -> str:
            result = subprocess.run(["git", "--no-optional-locks", "-C", str(self.repo), *parts],
                                    capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10,
                                    shell=False, check=True)
            # Leading spaces in porcelain status encode the index/worktree state.
            return result.stdout.rstrip("\r\n")
        commit = git("rev-parse", "HEAD")
        branch = git("rev-parse", "--abbrev-ref", "HEAD")
        changes = git("status", "--porcelain=v1", "--untracked-files=normal").splitlines()
        return {"branch": branch, "commit": commit, "dirty": bool(changes),
                "changed_files": changes[:200], "truncated": len(changes) > 200}
