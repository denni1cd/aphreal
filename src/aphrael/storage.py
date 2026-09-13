"""Transactional task records; each transition and event commit together."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def now():
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, status TEXT NOT NULL, created_at TEXT NOT NULL, body TEXT NOT NULL)")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=3)
        try:
            with db:
                yield db
        finally:
            db.close()

    def healthy(self):
        try:
            with self.connect() as db:
                db.execute("SELECT id, status, body FROM tasks LIMIT 1").fetchall()
            return True
        except sqlite3.Error:
            return False

    def create(self, request, profile):
        stamp = now()
        task = {"id": str(uuid4()), **request, "profile": profile, "status": "QUEUED", "created_at": stamp,
                "updated_at": stamp, "events": [{"at": stamp, "status": "QUEUED", "message": "Queued"}],
                "result": None, "error": None, "evidence": [], "verification": {"verified": False}}
        with self.connect() as db:
            db.execute("INSERT INTO tasks VALUES (?,?,?,?)", (task["id"], "QUEUED", stamp, json.dumps(task)))
        return task

    def get(self, task_id):
        with self.connect() as db:
            row = db.execute("SELECT body FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not row:
            raise KeyError(task_id)
        return json.loads(row[0])

    def recent(self, limit=50):
        with self.connect() as db:
            return [json.loads(row[0]) for row in db.execute("SELECT body FROM tasks ORDER BY created_at DESC, id DESC LIMIT ?", (limit,))]

    def queued(self):
        with self.connect() as db:
            row = db.execute("SELECT id FROM tasks WHERE status='QUEUED' ORDER BY created_at, id LIMIT 1").fetchone()
        return row[0] if row else None

    def transition(self, task_id, allowed, status, message, **updates):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT body FROM tasks WHERE id=?", (task_id,)).fetchone()
            if not row:
                raise KeyError(task_id)
            task = json.loads(row[0])
            if task["status"] not in allowed:
                return task
            stamp = now()
            task.update(updates, status=status, updated_at=stamp)
            task["events"].append({"at": stamp, "status": status, "message": message})
            db.execute("UPDATE tasks SET status=?,body=? WHERE id=?", (status, json.dumps(task), task_id))
            return task

    def recover(self):
        with self.connect() as db:
            ids = [r[0] for r in db.execute("SELECT id FROM tasks WHERE status='RUNNING'")]
        for task_id in ids:
            self.transition(task_id, {"RUNNING"}, "FAILED", "Process interrupted; work was not replayed",
                            error="Interrupted by process shutdown or crash")


class InstanceLock:
    """OS-held lock prevents two workers serving the same database."""
    def __init__(self, path):
        self.path = path
        self.handle = None

    def acquire(self):
        import os
        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle = self.path.open("a+b")
        try:
            handle.seek(0, 2)
            if handle.tell() == 0:
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            handle.close()
            raise RuntimeError("Aphrael is already using this data directory") from None
        self.handle = handle

    def release(self):
        if self.handle:
            self.handle.close()
            self.handle = None
