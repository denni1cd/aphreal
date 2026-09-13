# Aphrael

Aphrael is a local-first personal AI assistant project for Windows. Its current foundation runs real read-only workstation, repository, and filesystem capabilities, with persistent asynchronous tasks and independently checked completion evidence. Voice and AI provider integration remain future work.

Install Python 3.12+ with `python` on PATH and Git for repository inspection. In PowerShell at this checkout:

```powershell
.\START_APHRAEL.ps1
```

The launcher prepares a local `.venv` and installs dependencies if needed. Initial setup requires package download access; the running foundation requires no paid account or external service. Open [http://127.0.0.1:8765](http://127.0.0.1:8765). Stop with Ctrl+C.

To explicitly install/update dependencies and run tests:

```powershell
.\SETUP_APHRAEL.ps1
.\.venv\Scripts\python.exe -m pytest -q
```

Select a capability and click **Run capability now**, or enter a descriptive objective and click **Create task** using the `general` profile. **Inspect** shows durable events, results, and evidence; **Cancel** stops queued or cooperative running work. The selected capability and JSON arguments determine the operation; the objective is not interpreted as a natural-language plan.

Runtime tasks and results live in `%LOCALAPPDATA%\Aphrael`, outside the repository. This development service is intended for a trusted local Windows account and binds to loopback.

- [Foundation usage, configuration, privacy, recovery, and adapter API](docs/FOUNDATION.md)
- [Foundation verification and independent assessment](docs/VERIFICATION.md)
- [Current architecture and preserved future research](ARCHITECTURE.md)
- [Current milestone and future roadmap](PROJECT_PLAN.md)
- [Approved execution contract](FOUNDATION_CONTRACT.md)
- [Manifesto](MANIFESTO.md) and [vision](VISION.md)

See [LICENSE](LICENSE) for licensing terms.
