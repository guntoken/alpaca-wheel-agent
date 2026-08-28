"""Configuration: temperament knobs + risk gates. Paper-only, hardcoded."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

AGENT_DIR = Path(__file__).resolve().parents[2]  # .../alpaca-hackathon-2026/agent
load_dotenv(AGENT_DIR / ".env")

KEY_ID = os.environ.get("APCA_API_KEY_ID", "")
SECRET_KEY = os.environ.get("APCA_API_SECRET_KEY", "")

PAPER = True  # immutable by design: this project never talks to the live endpoint

# --- universe: liquid names with weekly options, sized so one contract fits ---
UNIVERSE = ["INTC", "T", "F", "GM", "PFE", "KO", "NOK", "SOFI", "BABA", "MU", "WBD", "VALE"]

# --- CSP (cash-secured put) ---
CSP_TARGET_DELTA = 0.30
CSP_DELTA_BAND = (0.18, 0.42)
DTE_MIN, DTE_MAX = 7, 35
MIN_PREMIUM_PCT = 0.005        # premium >= 0.5% of collateral (strike*100)
TP_CLOSE_FRACTION = 0.50       # buy back when premium <= 50% of what we received
ROLL_DELTA = 0.60              # defensive: close short put when delta reaches this

# --- CC (covered call) ---
CC_TARGET_DELTA = 0.25
CC_DELTA_BAND = (0.12, 0.38)

# --- risk gates (the write-up section judges read) ---
MAX_UNDERLYINGS = 5            # max underlyings with exposure at once
MAX_COLLATERAL_PCT = 0.18      # per-underlying collateral cap (% of equity)
MAX_TOTAL_COLLATERAL_PCT = 0.72
MIN_OPEN_INTEREST = 100
MAX_QUOTE_SPREAD_PCT = 0.15    # (ask-bid)/mid
DAILY_DRAWDOWN_STOP = 0.03     # no NEW entries if equity < day anchor * (1 - 3%)
KILL_FILE = AGENT_DIR / "KILL"

# --- files ---
STATE_FILE = AGENT_DIR / "state.json"
JOURNAL_FILE = AGENT_DIR / "journal.jsonl"
LOGS_DIR = AGENT_DIR / "runs"

# --- orders ---
ORDER_PREFIX = "WHL"           # all client_order_ids start with this

# --- AI layer ---
AI_ENABLED = True
AI_TIMEOUT_S = 90

# Earnings blackout: {"SYM": "2026-09-02"} — no new entries from T-1 to T+0.
# Maintained by the operator agent each morning (Trading API has no earnings feed).
EARNINGS_BLACKOUT: dict[str, str] = {}
