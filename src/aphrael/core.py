"""Interaction-independent commands, task lifecycle and completion authority."""
import asyncio
from copy import deepcopy

from .capabilities import Registry
from .commands import TaskRequest
from .storage import InstanceLock, Store
from .workers import DeterministicWorker


class Core:
    def __init__(self, settings):
        self.settings = settings
        self.registry = Registry(settings.repo)
        self.store = Store(settings.data_dir / "tasks.sqlite3")
        self.lock = InstanceLock(settings.data_dir / "worker.lock")
        self.workers = {"deterministic": DeterministicWorker()}
        self.runner = None
        self.stopping = False
        self.active_id = None
        self.cancel_event = None
        self.executor_error = None

    async def start(self):
        self.lock.acquire()
        try:
            self.store.recover()
            self.stopping = False
            self.runner = asyncio.create_task(self._loop())
        except BaseException:
            self.lock.release()
            raise

    async def stop(self):
        self.stopping = True
        if self.cancel_event:
            self.cancel_event.set()
        try:
            if self.runner:
                await self.runner
        finally:
            self.lock.release()

    def profiles(self):
        result = []
        for name, config in self.settings.profiles.items():
            worker = config.get("worker") if config else None
            available = isinstance(worker, str) and worker in self.workers
            result.append({"name": name, "worker": worker, "available": available,
                           "reason": None if available else "Not configured or worker unavailable"})
        return result

    def resolve_profile(self, name):
        name = name or self.settings.default_profile
        config = self.settings.profiles.get(name)
        worker = config.get("worker") if config else None
        if not isinstance(worker, str) or worker not in self.workers:
            raise ValueError(f"Profile '{name}' is not configured or unavailable")
        return name, self.workers[worker]

    def health(self):
        try:
            names = {t["name"] for t in self.registry.describe()}
            registry_ok = {"system.status", "repository.status", "filesystem.list", "filesystem.read", "filesystem.search"} <= names
        except Exception:
            registry_ok = False
        checks = {"application": True, "persistence": self.store.healthy(),
                  "executor": bool(self.runner and not self.runner.done() and not self.stopping and not self.executor_error),
                  "registry": registry_ok}
        return {"healthy": all(checks.values()), "checks": checks, "active_task": self.active_id,
                "profiles": self.profiles(), "worker_mode": "deterministic safe capabilities; no AI provider"}

    async def immediate(self, tool, arguments):
        self.registry.validate(tool, arguments)
        return await asyncio.to_thread(self.registry.invoke, tool, arguments)

    def create_task(self, request):
        request = TaskRequest.model_validate(request).model_dump()
        profile, _ = self.resolve_profile(request.get("profile"))
        arguments = self.registry.validate(request["tool"], request.get("arguments", {}))
        request = {**request, "arguments": arguments}
        return self.store.create(request, profile)

    def cancel(self, task_id):
        task = self.store.transition(task_id, {"QUEUED", "RUNNING"}, "CANCELLED", "Cancellation requested")
        if task_id == self.active_id and self.cancel_event:
            self.cancel_event.set()
        return task

    async def _loop(self):
        try:
            while not self.stopping:
                task_id = self.store.queued()
                if not task_id:
                    await asyncio.sleep(0.05)
                    continue
                # Publish cancellation before making RUNNING visible to API threads.
                self.active_id = task_id
                self.cancel_event = asyncio.Event()
                task = self.store.transition(task_id, {"QUEUED"}, "RUNNING", "Worker started")
                if task["status"] != "RUNNING":
                    self.active_id = None
                    self.cancel_event = None
                    continue
                await self._perform(task)
                self.active_id = None
                self.cancel_event = None
        except Exception as exc:
            # Health reports executor failure; do not claim an operational queue.
            self.executor_error = type(exc).__name__

    async def _perform(self, task):
        evidence = []

        async def execute(name, arguments):
            if self.cancel_event.is_set():
                return None
            observed = await self.immediate(name, arguments)
            evidence.append(deepcopy(observed))
            return deepcopy(observed)

        try:
            _, worker = self.resolve_profile(task["profile"])
            await worker.run(deepcopy(task), execute, self.cancel_event)
            if self.stopping:
                self.store.transition(task["id"], {"RUNNING"}, "FAILED", "Interrupted during shutdown",
                                      error="Interrupted by shutdown", evidence=evidence)
                return
            if self.cancel_event.is_set():
                return
            # Only this core-owned evidence ledger can establish completion.
            valid = (len(evidence) == 1 and evidence[0]["ok"] is True
                     and evidence[0]["tool"] == task["tool"]
                     and evidence[0]["arguments"] == task["arguments"])
            if not valid:
                self.store.transition(task["id"], {"RUNNING"}, "FAILED", "Completion could not be verified",
                                      error="Missing, failed or mismatched capability evidence", evidence=evidence)
                return
            self.store.transition(task["id"], {"RUNNING"}, "COMPLETED", "Capability result verified",
                                  result=evidence[0]["result"], evidence=evidence,
                                  verification={"verified": True, "method": "core-observed matching successful capability", "evidence_id": evidence[0]["id"]})
        except Exception as exc:
            self.store.transition(task["id"], {"RUNNING"}, "FAILED", "Worker failed",
                                  error=f"Worker error: {type(exc).__name__}", evidence=evidence)
