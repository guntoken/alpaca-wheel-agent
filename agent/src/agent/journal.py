"""Append-only JSONL decision journal + small state file (day anchor, counters)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from . import config


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def append(record: dict) -> None:
    config.JOURNAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    rec = {"ts": utcnow_iso(), **record}
    with open(config.JOURNAL_FILE, "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


def load_state() -> dict:
    if config.STATE_FILE.exists():
        try:
            return json.loads(config.STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def save_state(state: dict) -> None:
    config.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = config.STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, default=str))
    tmp.replace(config.STATE_FILE)


def tail(n: int = 5) -> list[dict]:
    if not config.JOURNAL_FILE.exists():
        return []
    lines = config.JOURNAL_FILE.read_text().splitlines()
    return [json.loads(l) for l in lines[-n:] if l.strip()]
