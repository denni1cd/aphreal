"""Create a trusted expected-outcome record for one Aphrael acceptance write.

This is an operator/setup command. It is deliberately not exposed as a Hermes
tool, so an agent cannot grant itself verification authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def identity(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value):
        raise argparse.ArgumentTypeError("use 1-128 letters, digits, _ or -")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--task-id", required=True, type=identity)
    parser.add_argument("--request-id", required=True, type=identity)
    parser.add_argument("--content-file", type=Path, required=True)
    parser.add_argument("--path", type=Path, required=True)
    args = parser.parse_args()

    workspace = args.workspace.resolve(strict=True)
    output = (workspace / "output").resolve(strict=True)
    target = args.path.resolve(strict=False)
    if target != output and output not in target.parents:
        raise SystemExit("target must be inside the configured output directory")
    content = args.content_file.read_bytes()
    record = {
        "task_id": args.task_id,
        "request_id": args.request_id,
        "board": "aphrael",
        "path": str(target),
        "sha256": hashlib.sha256(content).hexdigest(),
    }
    destination = args.evidence_root / "requests" / f"{args.request_id}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise SystemExit("request id already exists; immutable evidence request required")
    destination.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"Provisioned independent verification request {args.request_id}.")


if __name__ == "__main__":
    main()
