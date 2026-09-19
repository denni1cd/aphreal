"""Recovery behavior for an interrupted distribution update in an isolated profile."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import types


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "aphrael_profile.py"
spec = importlib.util.spec_from_file_location("aphrael_profile_recovery", SCRIPT)
profile_setup = importlib.util.module_from_spec(spec)
# The recovery function under test does not parse YAML.  Keep this repository's
# lightweight test environment independent from Hermes' setup-only PyYAML.
sys.modules.setdefault("yaml", types.ModuleType("yaml"))
spec.loader.exec_module(profile_setup)


def test_interrupted_owned_asset_update_restores_previous_state(tmp_path):
    profile = tmp_path / "profiles" / "aphrael"
    profile.mkdir(parents=True)
    (profile / "SOUL.md").write_text("new, interrupted", encoding="utf-8")
    backup = tmp_path / "backups" / "one"
    backup.mkdir(parents=True)
    (backup / "SOUL.md").write_text("prior working identity", encoding="utf-8")
    (backup / "restore.json").write_text(
        json.dumps({"profile": str(profile), "paths": ["SOUL.md"]}), encoding="utf-8"
    )
    (profile / "aphrael-update-in-progress").write_text(str(backup), encoding="utf-8")

    profile_setup.restore_interrupted(profile)

    assert (profile / "SOUL.md").read_text(encoding="utf-8") == "prior working identity"
    assert not (profile / "aphrael-update-in-progress").exists()
