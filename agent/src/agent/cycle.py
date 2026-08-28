"""One trading cycle: observe -> gates -> decide -> AI overlay -> execute -> journal."""
from __future__ import annotations

from datetime import datetime

from . import ai, config, journal, risk, wheel
from .alpaca_client import Api, _num, parse_occ


def _market_summary(api: Api) -> dict:
    out = {}
    for sym in ("SPY", "QQQ"):
        px = api.last_trade(sym)
        closes = api.daily_closes(sym)
        sma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else None
        sma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None
        out[sym] = {
            "last": px,
            "sma20": round(sma20, 2) if sma20 else None,
            "sma50": round(sma50, 2) if sma50 else None,
            "vs_sma20_pct": round((px / sma20 - 1) * 100, 2) if px and sma20 else None,
            "vs_sma50_pct": round((px / sma50 - 1) * 100, 2) if px and sma50 else None,
        }
    # market-wide vol context for the AI regime read (practitioner rule:
    # "always know what vol is doing" — VIX awareness without a VIX feed)
    spy_vp = api.vol_dollar_percentile("SPY")
    if spy_vp is not None:
        out["SPY_vol_dollar_percentile"] = round(spy_vp, 3)
    return out


def _pos_brief(p) -> dict:
    return {"symbol": str(getattr(p, "symbol", "")),
            "qty": float(getattr(p, "qty", 0) or 0),
            "side": str(getattr(p, "side", "")),
            "avg_entry": float(getattr(p, "avg_entry_price", 0) or 0),
            "unrealized_pl": float(getattr(p, "unrealized_pl", 0) or 0)}


def _enforce_caps(entries: list[dict], collateral_used: float, caps: dict):
    """Central cap enforcement: the per-symbol budget in wheel.decide is blind to
    the other symbols' picks, so the final entry list is pruned here — best
    premium first — against the REAL totals."""
    approved, capped = [], []
    used = collateral_used
    symbols: set[str] = set()
    ranked = sorted(entries, key=lambda i: -(i.get("detail", {}).get("premium_pct") or 0))
    for i in ranked:
        try:
            _, _, _, strike = parse_occ(i["occ"])
        except Exception:
            capped.append({**i, "reason": "cap: unparseable occ"})
            continue
        need = strike * 100 * i["qty"]
        sym = i["underlying"]
        if sym not in symbols and len(symbols) >= config.MAX_UNDERLYINGS:
            capped.append({**i, "reason": f"cap: max {config.MAX_UNDERLYINGS} underlyings"})
            continue
        if used + need > caps["total"]:
            capped.append({**i, "reason": f"cap: total collateral budget {caps['total']:.0f}"})
            continue
        approved.append(i)
        used += need
        symbols.add(sym)
    return approved, capped


def run_cycle(dry_run: bool = True, force: bool = False, no_ai: bool = False) -> dict:
    api = Api()
    rec: dict = {"phase": "cycle", "dry_run": dry_run, "errors": [],
                 "orders": [], "intents": []}

    # 1) clock
    try:
        clock = api.clock()
        rec["market_open"] = bool(clock.is_open)
    except Exception as e:
        rec["errors"].append(f"clock: {e}")
        journal.append(rec)
        return rec
    if not clock.is_open and not force:
        rec["skipped"] = "market closed"
        journal.append(rec)
        return rec

    # 2) account + state + gates
    acct = api.account()
    equity = float(acct.equity)
    rec["equity"] = equity
    state = journal.load_state()
    risk.refresh_day_anchor(state, equity)
    journal.save_state(state)
    rec["day_anchor"] = state.get("day_start_equity")

    kr = risk.kill_reason()
    if kr:
        rec["halted"] = kr
        journal.append(rec)
        return rec

    dd_ok, dd_reason = risk.drawdown_ok(state, equity)
    if not dd_ok:
        rec["gate"] = dd_reason

    # 3) market summary + AI regime
    summary = _market_summary(api)
    rec["market"] = summary
    regime = ({"regime": "NEUTRAL", "reason": "AI disabled by flag", "ai": False}
              if no_ai else ai.read_regime(summary))
    rec["ai_regime"] = regime
    entries_allowed = bool(dd_ok and regime["regime"] != "RISK_OFF")
    rec["entries_allowed"] = entries_allowed

    # 4) positions -> wheel states
    positions = api.positions()
    rec["positions"] = [_pos_brief(p) for p in positions]
    states = wheel.collect_states(api, config.UNIVERSE)

    active = {u for u, st in states.items()
              if st.equity_qty > 0 or st.short_put is not None or st.short_call is not None}
    collateral_used = 0.0
    for u, st in states.items():
        if st.short_put is not None:
            _, _, _, strike = parse_occ(str(st.short_put.symbol))
            qty = abs(int(float(getattr(st.short_put, "qty", 0) or 0)))
            collateral_used += strike * 100 * qty
    caps = risk.collateral_caps(equity, regime["regime"])
    # Broker truth: our own caps may not exceed Alpaca's actual options buying
    # power (open CSP orders reserve it). If the field is missing, assume none.
    obp = _num(getattr(acct, "options_buying_power", None)) or 0.0
    caps["total"] = min(caps["total"], collateral_used + obp)
    rec["options_buying_power"] = obp
    rec["caps"] = {k: round(v, 2) for k, v in caps.items()}
    rec["collateral_used"] = round(collateral_used, 2)
    rec["active_underlyings"] = sorted(active)

    open_orders = api.open_orders()
    open_syms_sides = {(str(getattr(o, "symbol", "")), str(getattr(o, "side", "")))
                       for o in open_orders}
    rec["open_orders_n"] = len(open_orders)

    ctx = {"entries_allowed": entries_allowed, "caps": caps,
           "collateral_used": collateral_used, "universe": config.UNIVERSE,
           "active_underlyings": sorted(active),
           "slots_free": risk.slots_free(len(active))}

    # 5) deterministic decisions
    for u in config.UNIVERSE:
        st = states.get(u)
        if st is None:
            continue
        st.spot = api.last_trade(u)
        try:
            rec["intents"].extend(i.as_dict() for i in wheel.decide(api, st, ctx))
        except Exception as e:
            rec["errors"].append(f"decide {u}: {e}")
            rec["intents"].append({"kind": "SKIP", "underlying": u,
                                   "reason": f"error: {e}"})

    entries = [i for i in rec["intents"] if i["kind"] in ("SELL_CSP", "SELL_CC")]
    exits = [i for i in rec["intents"] if i["kind"] in ("BUYBACK_PUT", "BUYBACK_CC")]

    entries, capped = _enforce_caps(entries, collateral_used, caps)
    for i in capped:
        rec["intents"] = [x for x in rec["intents"] if x is not i]
        rec["intents"].append({"kind": "SKIP", "underlying": i.get("underlying", ""),
                               "occ": i.get("occ", ""), "reason": i.get("reason", "cap")})

    # 6) AI veto on entries only
    if no_ai:
        veto = {"veto": [], "reasons": {}, "ai": False}
    else:
        veto = ai.veto_entries(entries)
    rec["ai_veto"] = veto
    vetoed = set(veto.get("veto") or [])

    # 7) execute: exits first, then non-vetoed entries
    def _execute(intent: dict) -> None:
        sym_side = (intent["occ"], "sell" if intent["kind"].startswith("SELL") else "buy")
        if sym_side in open_syms_sides:
            rec["orders"].append({**intent, "action": "skip",
                                  "note": "open order already in flight"})
            return
        coid = f"{intent['coid']}-{datetime.now():%H%M}"
        if dry_run:
            rec["orders"].append({**intent, "coid": coid, "action": "would_submit"})
            return
        try:
            o = api.submit_option_limit(
                intent["occ"], intent["qty"], sym_side[1], intent["limit"], coid)
            rec["orders"].append({**intent, "coid": coid, "action": "submitted", **o})
        except Exception as e:
            rec["errors"].append(f"submit {intent['occ']}: {e}")
            rec["orders"].append({**intent, "coid": coid, "action": "error", "note": str(e)})

    for i in exits:                      # exits before entries, always
        _execute(i)
    for i in entries:
        if i["coid"] in vetoed:
            rec["orders"].append({**i, "action": "ai_veto",
                                  "note": (veto.get("reasons") or {}).get(i["coid"], "")})
            continue
        _execute(i)

    state["cycles"] = int(state.get("cycles", 0)) + 1
    journal.save_state(state)
    rec["cycle_no"] = state["cycles"]
    journal.append(rec)
    return rec
