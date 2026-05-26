"""Paths and lightweight .env loading (no external dependency)."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KB_DIR = ROOT / "knowledge_base"
DB_PATH = ROOT / "kb.db"
SCENARIO = ROOT / "scenarios" / "call_center_aht.yaml"
RUBRIC = ROOT / "rubric" / "measure_rubric.yaml"


def load_env(path: Path | None = None) -> None:
    env = path or (ROOT / ".env")
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip())
