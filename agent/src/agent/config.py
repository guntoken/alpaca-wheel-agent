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

# --- judged-run sprint (LabLab Admin, 31 Agu): P&L window Sen 31 Agu 09:30 ET
# → total-equity snapshot at Thu 3 Sep close; "positions expiring on Friday,
# September 4 are excluded from this measurement". New CSPs (and defensive
# rolls) target exactly that expiry: premium lands as counted cash while the
# short's Thu-close mark is excluded, and any assignment settles post-snapshot.
# None = standard 7–35 DTE wheel. Disclosed in the journal/README. ---
SPRINT_EXPIRY = "2026-09-04"
# Kamis 3 Sep malam (malam terakhir window skor): TIDAK buka CSP baru —
# 1-DTE menjelang NFP (Jum 19:30 WIB, pasca-snapshot) = EV buruk. Premium
# 4 malam sudah tercatat sebagai cash; posisi expiry 4-Sep dikecualikan
# dari snapshot Kamis. Take-profit buyback & roll tetap diizinkan.
BLOCK_NEW_CSP = True
MIN_PREMIUM_PCT = 0.005        # premium >= 0.5% of collateral (strike*100)
TP_CLOSE_FRACTION = 0.50       # buy back when premium <= 50% of what we received
ROLL_DELTA = 0.60              # defensive: close short put when delta reaches this

# --- volatility-percentile gate (adapted from Rustamov et al. 2024, inverted
# for premium selling: skip NEW CSPs when vol is cheap vs its own history) ---
VOL_BAR_WINDOW = 21            # ~1 month bar, vs paper's 35-day OHP
VOL_HISTORY_DAYS = 250         # paper uses 250 trading days
VOL_PCT_FLOOR = 0.25           # sprint override (was 0.40): 4-session judged
                               # window Sen–Kam 31 Agu–3 Sep; idle capital = zero
                               # score, and 0.40 blocked 4/6 names on 30 Agu

# --- CC (covered call) ---
CC_TARGET_DELTA = 0.25
CC_DELTA_BAND = (0.12, 0.38)
BB_WINDOW = 20                 # covered-call strikes must clear the upper
BB_STD = 2.0                   # Bollinger Band (official Alpaca wheel guide)

# --- risk gates (the write-up section judges read) ---
MAX_UNDERLYINGS = 5            # max underlyings with exposure at once
MAX_COLLATERAL_PCT = 0.18      # per-underlying collateral cap (% of equity)
MAX_TOTAL_COLLATERAL_PCT = 0.72
MIN_OPEN_INTEREST = 200        # official Alpaca wheel tutorial threshold
MAX_QUOTE_SPREAD_PCT = 0.15    # (ask-bid)/mid
DAILY_DRAWDOWN_STOP = 0.03     # no NEW entries if equity < day anchor * (1 - 3%)
KILL_FILE = AGENT_DIR / "KILL"

# --- sector diversification (correlated assignments are the wheel's crash mode;
# idea adapted from agentic-trading-system's sector cap, own implementation) ---
SECTOR_MAP = {
    "semis": ["INTC", "MU"],
    "telecom": ["T", "NOK"],
    "auto": ["F", "GM"],
    "pharma": ["PFE"],
    "staples": ["KO"],
    "fintech": ["SOFI"],
    "china-ecom": ["BABA"],
    "media": ["WBD"],
    "materials": ["VALE"],
}
MAX_PER_SECTOR = 2             # max UNDERLYINGS with exposure in one sector

# --- deterministic regime overlay on top of the AI regime read
# (SPY intraday %; tiers adapted from agentic-trading-system, own implementation).
# The AI can flicker; this anchor can't. Tighter of the two always wins. ---
REGIME_SPY_BEAR_PCT = -2.0
REGIME_SPY_EXTREME_PCT = -4.0
REGIME_SPY_BULL_PCT = 2.0
BEAR_TARGET_DELTA = 0.20       # weak tape -> sell further OTM, not just less
BEAR_DELTA_BAND = (0.10, 0.30)
BEAR_BUDGET_MULT = 0.5
EXTREME_BUDGET_MULT = 0.0      # no new entries at all

# --- stale entry re-pricing (night-1 lesson: mid-limit T orders never filled;
# cancel-and-fresh-quote next cycle, with a chase cap so we stop chasing) ---
REPRICE_AFTER_MIN = 20
MAX_REPRICES_PER_SYMBOL_DAY = 3

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
