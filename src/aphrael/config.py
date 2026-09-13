"""Small explicit configuration; no provider SDK or secret is required."""
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

ALIASES = ("voice", "fast", "general", "deep", "coding", "local")


def default_profiles():
    return {**{name: None for name in ALIASES}, "general": {"worker": "deterministic"}}


@dataclass
class Settings:
    repo: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2])
    data_dir: Path = field(default_factory=lambda: Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local" / "share"))) / "Aphrael")
    port: int = 8765
    default_profile: str = "general"
    profiles: dict = field(default_factory=default_profiles)

    def __post_init__(self):
        self.repo = self.repo.resolve()
        self.data_dir = self.data_dir.resolve()
        if self.data_dir.is_relative_to(self.repo):
            raise ValueError("Runtime data must be outside the repository")
        source_repo = Path(__file__).resolve().parents[2]
        if self.data_dir.is_relative_to(source_repo):
            raise ValueError("Runtime data must be outside the source repository")
        if not 1 <= self.port <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        if not isinstance(self.profiles, dict):
            raise ValueError("profiles must be an object")
        if not isinstance(self.default_profile, str) or not self.default_profile.strip():
            raise ValueError("default_profile must be a nonempty profile name")
        self.profiles = {**{name: None for name in ALIASES}, **self.profiles}
        for name, profile in self.profiles.items():
            if not isinstance(name, str) or (profile is not None and not isinstance(profile, dict)):
                raise ValueError("Each profile must be an object or null")

    @classmethod
    def from_env(cls):
        config = {}
        if path := os.environ.get("APHRAEL_CONFIG"):
            config = json.loads(Path(path).read_text(encoding="utf-8"))
            if not isinstance(config, dict) or set(config) - {"profiles", "default_profile"}:
                raise ValueError("Configuration supports profiles and default_profile only")
        for env, key in (("APHRAEL_DATA_DIR", "data_dir"), ("APHRAEL_REPO", "repo")):
            if value := os.environ.get(env):
                config[key] = Path(value)
        config["port"] = int(os.environ.get("APHRAEL_PORT", "8765"))
        return cls(**config)
