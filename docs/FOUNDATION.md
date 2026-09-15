# Historical foundation

The former custom FastAPI/browser runtime is historical only. Its complete,
runnable implementation remains recoverable from Git tag
`pre-hermes-foundation-20260914` for the documented rollback procedure.

Current Aphrael operation uses the Hermes distribution:

```powershell
.\SETUP_APHRAEL.ps1
.\START_APHRAEL.ps1 -Surface Chat
.\.venv\Scripts\python.exe -m pytest -q
```

See [the Hermes guide](HERMES_GUIDE.md) for runtime state, updates, recovery,
and operator checks.
