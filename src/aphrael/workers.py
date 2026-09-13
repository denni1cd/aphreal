"""Workers receive capability access, never authority to verify themselves."""
import asyncio
from typing import Protocol


class Worker(Protocol):
    async def run(self, request: dict, execute, cancelled: asyncio.Event) -> None:
        """Perform the requested operation; evidence is captured by execute."""
        ...


class DeterministicWorker:
    async def run(self, request, execute, cancelled):
        # A bounded user-selected pause makes queue/progress/cancellation inspectable.
        remaining = request.get("delay_seconds", 0)
        while remaining > 0:
            if cancelled.is_set():
                return
            step = min(remaining, 0.1)
            await asyncio.sleep(step)
            remaining -= step
        if not cancelled.is_set():
            await execute(request["tool"], request["arguments"])
