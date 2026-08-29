"""Export read-only dashboard data (dashboard/data.json).

The hosted dashboard must carry ZERO credentials: everything it shows is
snapshotted here from the journal + the paper API and committed to the repo.
"""
from __future__ import annotations

import json

from . import config
from .alpaca_client import Api, _enumval, _num, parse_occ
from .journal import load_state

DASH_DIR = config.AGENT_DIR / "dashboard"
DATA_FILE = DASH_DIR / "data.json"


def write_dashboard_data(api: Api | None = None) -> dict:
    api = api or Api()
    data: dict = {}

    acct = api.account()
    state = load_state()
    data["updated"] = api.clock().timestamp.isoformat()
    data["account"] = {
        "equity": _num(acct.equity),
        "cash": _num(acct.cash),
        "options_buying_power": _num(getattr(acct, "options_buying_power", None)),
        "day_start_equity": state.get("day_start_equity"),
        "paper_only": True,
    }

    # positions with wheel context parsed from the OCC symbol
    positions = []
    spot_cache: dict[str, float | None] = {}
    for p in api.positions():
        sym = str(getattr(p, "symbol", ""))
        try:
            root, exp, right, strike = parse_occ(sym)
            kind = f"short {'put' if right == 'P' else 'call'}"
        except Exception:
            root, exp, right, strike = sym, None, None, None
            kind = "equity"
        if root not in spot_cache:
            spot_cache[root] = api.last_trade(root) or _num(
                getattr(p, "current_price", None))
        positions.append({
            "symbol": sym, "underlying": root, "kind": kind,
            "strike": strike, "expiry": exp.isoformat() if exp else None,
            "qty": _num(getattr(p, "qty", 0)),
            "avg_entry": _num(getattr(p, "avg_entry_price", 0)),
            "mark": _num(getattr(p, "current_price", None)),
            "unrealized_pl": _num(getattr(p, "unrealized_pl", 0)),
            "collateral": (strike * 100 * abs(_num(getattr(p, "qty", 0)) or 0)
                           if strike else None),
            "spot": spot_cache.get(root),
        })
    data["positions"] = positions

    data["open_orders"] = [{
        "symbol": str(getattr(o, "symbol", "")),
        "side": _enumval(getattr(o, "side", "")),
        "qty": _num(getattr(o, "qty", 0)),
        "limit": _num(getattr(o, "limit_price", None)),
        "status": _enumval(getattr(o, "status", "")),
        "coid": str(getattr(o, "client_order_id", "")),
    } for o in api.open_orders()]

    # net filled premium (our fills only: sells add, buybacks subtract)
    from alpaca.trading.requests import GetOrdersRequest
    from alpaca.trading.enums import QueryOrderStatus
    closed = api.trade.get_orders(GetOrdersRequest(
        status=QueryOrderStatus.CLOSED, limit=100)) or []
    premium_total = 0.0
    fills = []
    for o in closed:
        if not str(getattr(o, "client_order_id", "")).startswith(config.ORDER_PREFIX):
            continue
        filled_qty = _num(getattr(o, "filled_qty", 0)) or 0.0
        price = _num(getattr(o, "filled_avg_price", None))
        side = _enumval(getattr(o, "side", ""))
        if price and filled_qty:
            # option contracts: quoted price is per-share, ×100 multiplier
            notional = price * 100 * filled_qty
            premium_total += notional if side == "sell" else -notional
            fills.append({
                "ts": str(getattr(o, "filled_at", None) or getattr(o, "submitted_at", "")),
                "symbol": str(getattr(o, "symbol", "")), "side": side,
                "qty": filled_qty, "price": price, "notional": round(notional, 2),
            })
    data["fills"] = fills[-30:]
    data["premium_net_collected"] = round(premium_total, 2)

    # journal-derived series
    cycles = []
    if config.JOURNAL_FILE.exists():
        cycles = [json.loads(l) for l in config.JOURNAL_FILE.read_text().splitlines() if l.strip()]
    data["equity_curve"] = [
        {"ts": c.get("ts"), "equity": c.get("equity")}
        for c in cycles if c.get("equity") is not None
    ][-400:]
    # macro panel the AI regime reader saw on the last cycle
    data["market_context"] = next(
        (c.get("market") for c in reversed(cycles) if c.get("market")), None)
    data["regime_history"] = [
        {"ts": c.get("ts"), "regime": (c.get("ai_regime") or {}).get("regime"),
         "reason": (c.get("ai_regime") or {}).get("reason"),
         "det": (c.get("det_regime") or {}).get("regime"),
         "spy_pct": (c.get("det_regime") or {}).get("spy_day_change_pct")}
        for c in cycles if c.get("ai_regime")
    ][-80:]
    feed = []
    for c in cycles:
        for i in c.get("intents", []):
            feed.append({"ts": c.get("ts"), "cycle": c.get("cycle_no"),
                         "kind": i.get("kind"), "underlying": i.get("underlying"),
                         "occ": i.get("occ", ""), "reason": i.get("reason", "")})
    data["decisions_feed"] = feed[-100:]
    vetoes = []
    for c in cycles:
        for o in c.get("orders", []):
            if o.get("action") == "ai_veto":
                vetoes.append({"ts": c.get("ts"), "occ": o.get("occ"),
                               "note": o.get("note", "")})
    data["ai_vetoes"] = vetoes[-20:]
    data["stats"] = {
        "cycles_total": len(cycles),
        "live_cycles": sum(1 for c in cycles if not c.get("dry_run")),
        "fills": len(fills),
        "unrealized_pl": round(sum(p["unrealized_pl"] or 0 for p in positions), 2),
        "kill_switch": config.KILL_FILE.exists(),
    }
    data["risk_limits"] = {
        "max_underlyings": config.MAX_UNDERLYINGS,
        "max_collateral_pct": config.MAX_COLLATERAL_PCT,
        "max_total_collateral_pct": config.MAX_TOTAL_COLLATERAL_PCT,
        "max_per_sector": config.MAX_PER_SECTOR,
        "daily_drawdown_stop": config.DAILY_DRAWDOWN_STOP,
        "csp_target_delta": config.CSP_TARGET_DELTA,
        "tp_close_fraction": config.TP_CLOSE_FRACTION,
    }

    DASH_DIR.mkdir(parents=True, exist_ok=True)
    tmp = DATA_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, default=str, indent=1))
    tmp.replace(DATA_FILE)
    return data


if __name__ == "__main__":
    d = write_dashboard_data()
    print(f"data.json written: {d['stats']}")
