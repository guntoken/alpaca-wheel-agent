"""Risk gates: every path to an order runs through here."""
from __future__ import annotations

from datetime import date

from . import config


def kill_reason() -> str | None:
    """Touch KILL file (in agent dir) -> agent stops submitting anything."""
    if config.KILL_FILE.exists():
        return "kill-switch file present (agent/KILL)"
    return None


def refresh_day_anchor(state: dict, equity: float) -> dict:
    """Reset the daily drawdown anchor and reprice counters each day."""
    today = date.today().isoformat()
    if state.get("day") != today:
        state["day"] = today
        state["day_start_equity"] = equity
        state["repriced"] = {}
    return state


def sector_of(symbol: str) -> str:
    for sector, tickers in config.SECTOR_MAP.items():
        if symbol in tickers:
            return sector
    return "other"


def deterministic_regime(spy_day_change_pct: float | None) -> dict:
    """SPY-intraday-change regime tiers. The AI regime can flicker; this anchor
    cannot. The tighter of the two always governs entries and budget."""
    if spy_day_change_pct is None:
        return {"regime": "NEUTRAL", "budget_mult": 1.0, "delta_override": None}
    if spy_day_change_pct <= config.REGIME_SPY_EXTREME_PCT:
        return {"regime": "EXTREME_BEAR", "budget_mult": config.EXTREME_BUDGET_MULT,
                "delta_override": None}
    if spy_day_change_pct <= config.REGIME_SPY_BEAR_PCT:
        return {"regime": "BEAR", "budget_mult": config.BEAR_BUDGET_MULT,
                "delta_override": config.BEAR_TARGET_DELTA}
    return {"regime": "NEUTRAL_OR_BULL", "budget_mult": 1.0, "delta_override": None}


def drawdown_ok(state: dict, equity: float) -> tuple[bool, str | None]:
    anchor = float(state.get("day_start_equity") or equity)
    if equity < anchor * (1 - config.DAILY_DRAWDOWN_STOP):
        return False, (f"daily drawdown stop: equity {equity:.0f} < "
                       f"{config.DAILY_DRAWDOWN_STOP:.0%} of anchor {anchor:.0f}")
    return True, None


def earnings_block(symbol: str) -> str | None:
    """No new entries from the day before earnings through earnings day."""
    blk = config.EARNINGS_BLACKOUT.get(symbol)
    if not blk:
        return None
    try:
        d = date.fromisoformat(blk)
    except ValueError:
        return None
    today = date.today()
    if (d - today).days <= 1 and (d - today).days >= 0:
        return f"earnings blackout {symbol} @ {blk}"
    return None


def collateral_caps(equity: float, regime: str) -> dict:
    """Total collateral budget depends on the AI regime read; per-symbol cap doesn't."""
    total_pct = config.MAX_TOTAL_COLLATERAL_PCT
    if regime == "NEUTRAL":
        total_pct *= 0.5
    elif regime == "RISK_OFF":
        total_pct = 0.0
    return {
        "per_underlying": equity * config.MAX_COLLATERAL_PCT,
        "total": equity * total_pct,
        "total_pct_effective": total_pct,
    }


def slots_free(active_underlyings: int) -> bool:
    return active_underlyings < config.MAX_UNDERLYINGS
