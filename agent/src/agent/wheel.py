"""The Wheel state machine: sell CSP -> (assignment) -> sell CC -> called away -> repeat."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from . import config
from .alpaca_client import Api, Candidate, _num, _quote_pair, parse_occ


@dataclass
class SymbolState:
    underlying: str
    equity_qty: int = 0
    qty_available: int = 0                # net of shares already committed to orders
    avg_cost: float = 0.0
    short_put: Optional[object] = None   # alpaca Position (short put)
    short_call: Optional[object] = None  # alpaca Position (short call)
    spot: Optional[float] = None


@dataclass
class Intent:
    kind: str            # SELL_CSP | BUYBACK_PUT | SELL_CC | BUYBACK_CC | SKIP
    underlying: str
    occ: str = ""
    qty: int = 0
    limit: float = 0.0
    coid: str = ""
    reason: str = ""
    detail: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {"kind": self.kind, "underlying": self.underlying, "occ": self.occ,
                "qty": self.qty, "limit": round(self.limit, 2), "coid": self.coid,
                "reason": self.reason, "detail": self.detail}


def collect_states(api: Api, universe: list[str]) -> dict[str, SymbolState]:
    states = {u: SymbolState(underlying=u) for u in universe}
    for p in api.positions():
        sym = str(p.symbol)
        asset_class = str(getattr(p, "asset_class", "") or "")
        qty = _num(getattr(p, "qty", 0)) or 0
        avg = _num(getattr(p, "avg_entry_price", 0)) or 0.0
        side = str(getattr(p, "side", "long"))
        if "option" in asset_class.lower():
            try:
                root, _exp, right, _strike = parse_occ(sym)
            except Exception:
                continue
            st = states.setdefault(root, SymbolState(underlying=root))
            if right == "P" and side == "short":
                st.short_put = p
            elif right == "C" and side == "short":
                st.short_call = p
        else:
            st = states.setdefault(sym, SymbolState(underlying=sym))
            st.equity_qty = int(qty)
            st.qty_available = int(_num(getattr(p, "qty_available", None)) or qty)
            st.avg_cost = avg
    return states


def _best(cands: list[Candidate], target: float, band: tuple[float, float],
          min_premium_pct: float = 0.0) -> Optional[Candidate]:
    ok = [c for c in cands if band[0] <= c.delta <= band[1]
          and (min_premium_pct == 0 or c.premium_pct >= min_premium_pct)]
    if not ok:
        return None
    return min(ok, key=lambda c: abs(c.delta - target))


def decide(api: Api, st: SymbolState, ctx: dict) -> list[Intent]:
    """ctx: entries_allowed, caps, open_coids (set of our open order coids)."""
    u = st.underlying
    skip = lambda r: [Intent("SKIP", u, reason=r)]

    # ---------- state 1: flat -> consider new CSP ----------
    if st.short_put is None and st.equity_qty == 0 and st.short_call is None:
        if not ctx["entries_allowed"]:
            return skip("no new entries (regime/risk gate)")
        if u not in ctx["universe"]:
            return skip("not in universe")
        if u in [i for i in ctx.get("active_underlyings", []) if i != u]:
            pass  # cap handled below via slots
        from . import risk
        eb = risk.earnings_block(u)
        if eb:
            return skip(eb)
        # Vol-percentile gate (Rustamov et al. 2024, inverted for short
        # premium): don't open NEW CSPs when vol-in-currency is cheap vs its
        # own history — that's the paper's straddle-BUY zone, our sell-avoid zone.
        vp = api.vol_dollar_percentile(u, config.VOL_BAR_WINDOW,
                                       config.VOL_HISTORY_DAYS)
        if vp is not None and vp < config.VOL_PCT_FLOOR:
            return skip(f"vol percentile {vp:.0%} < {config.VOL_PCT_FLOOR:.0%} "
                        "floor — premium cheap vs history (AON gate)")
        if not ctx["slots_free"]:
            return skip(f"max underlyings reached ({config.MAX_UNDERLYINGS})")
        strike_max = ctx["caps"]["per_underlying"] / 100.0
        cands = api.candidates(u, "P", config.DTE_MIN, config.DTE_MAX, strike_max=strike_max)
        best = _best(cands, config.CSP_TARGET_DELTA, config.CSP_DELTA_BAND,
                     config.MIN_PREMIUM_PCT)
        if best is None:
            return skip("no qualifying put (delta/DTE/OI/spread/premium filters)")
        collat_used = ctx.get("collateral_used", 0.0)
        budget = min(ctx["caps"]["per_underlying"],
                     ctx["caps"]["total"] - collat_used)
        qty = max(0, int(math.floor(budget / (best.strike * 100)))) if budget > 0 else 0
        if qty < 1:
            return skip(f"collateral budget exhausted for {u}")
        limit = max(best.mid, best.bid)  # marketable but not through the book
        return [Intent("SELL_CSP", u, occ=best.symbol, qty=qty, limit=limit,
                       coid=f"{config.ORDER_PREFIX}-CSP-{best.symbol}",
                       reason=(f"new CSP: delta {best.delta:.2f}, dte {best.dte}, "
                               f"prem {best.premium_pct:.2%} of collateral"
                               + (f", vol pct {vp:.0%}" if vp is not None else "")),
                       detail={**best.as_dict(), "vol_pct": vp})]

    # ---------- state 2: short put open -> manage ----------
    if st.short_put is not None:
        pos = st.short_put
        occ = str(pos.symbol)
        qty = abs(int(_num(getattr(pos, "qty", 0)) or 0))
        entry_prem = abs(_num(getattr(pos, "avg_entry_price", 0)) or 0.0)
        snaps = api.chain_snapshots(u)
        s = snaps.get(occ)
        if s is None or getattr(s, "latest_quote", None) is None:
            return skip(f"short put {occ}: no live quote, holding")
        bid, ask = _quote_pair(s.latest_quote)
        if not bid or not ask:
            return skip(f"short put {occ}: bad quote, holding")
        mid = (bid + ask) / 2
        delta = abs(_num(getattr(getattr(s, "greeks", None), "delta", None)) or 0.0)
        _, expiry, _, strike = parse_occ(occ)
        dte = (expiry - date.today()).days
        if dte <= 0:
            return skip(f"short put {occ} expires today — let it settle (assignment if ITM)")
        if entry_prem > 0 and ask <= entry_prem * config.TP_CLOSE_FRACTION:
            limit = min(mid, ask)
            return [Intent("BUYBACK_PUT", u, occ=occ, qty=qty, limit=limit,
                           coid=f"{config.ORDER_PREFIX}-TPP-{occ}",
                           reason=(f"take-profit: ask {ask:.2f} <= {config.TP_CLOSE_FRACTION:.0%}"
                                   f" of entry {entry_prem:.2f}"),
                           detail={"entry_prem": entry_prem, "ask": ask, "delta": delta, "dte": dte})]
        if delta >= config.ROLL_DELTA:
            limit = min(mid, ask)
            return [Intent("BUYBACK_PUT", u, occ=occ, qty=qty, limit=limit,
                           coid=f"{config.ORDER_PREFIX}-ROLL-{occ}",
                           reason=(f"defensive close: delta {delta:.2f} >= {config.ROLL_DELTA}"
                                   " (fresh CSP may follow next cycle)"),
                           detail={"entry_prem": entry_prem, "ask": ask, "delta": delta, "dte": dte})]
        return skip(f"hold short put {occ}: delta {delta:.2f}, dte {dte}, "
                    f"unrealized {float(getattr(pos, 'unrealized_pl', 0) or 0):+.2f}")

    # ---------- state 3: shares held (assigned) -> covered call ----------
    if st.equity_qty >= 100 and st.short_call is None:
        if not ctx["entries_allowed"]:
            return skip(f"holding {st.equity_qty} {u}: CC blocked by regime/risk gate")
        # Official Alpaca wheel guide: CC strike must clear BOTH cost basis and
        # the upper Bollinger Band (SMA20 + 2σ) — don't cap a stretched price.
        ub = api.upper_bollinger(u, config.BB_WINDOW, config.BB_STD)
        floor = max(st.avg_cost, ub) if ub else st.avg_cost
        cands = api.candidates(u, "C", config.DTE_MIN, config.DTE_MAX,
                               strike_min=max(floor, 0.01))
        best = _best(cands, config.CC_TARGET_DELTA, config.CC_DELTA_BAND)
        if best is None:
            return skip(f"no qualifying call above floor {floor:.2f} "
                        f"(cost {st.avg_cost:.2f}, upperBB "
                        f"{f'{ub:.2f}' if ub else 'n/a'})")
        avail = st.qty_available or st.equity_qty
        qty = avail // 100
        if qty < 1:
            return skip(f"{u}: shares already committed to other orders")
        limit = max(best.mid, best.bid)
        return [Intent("SELL_CC", u, occ=best.symbol, qty=qty, limit=limit,
                       coid=f"{config.ORDER_PREFIX}-CC-{best.symbol}",
                       reason=(f"covered call: delta {best.delta:.2f}, dte {best.dte}, "
                               f"strike {best.strike:.2f} >= floor {floor:.2f} "
                               f"(cost {st.avg_cost:.2f}, upperBB "
                               f"{f'{ub:.2f}' if ub else 'n/a'})"),
                       detail=best.as_dict())]
        # remainder < 100 shares stays uncovered by design (never sell naked calls)

    if st.equity_qty > 0 and st.equity_qty < 100:
        return skip(f"{st.equity_qty} {u} shares (<100) — no CC possible, holding")

    # ---------- state 4: shares + short call -> manage CC ----------
    if st.equity_qty >= 100 and st.short_call is not None:
        pos = st.short_call
        occ = str(pos.symbol)
        qty = abs(int(_num(getattr(pos, "qty", 0)) or 0))
        entry_prem = abs(_num(getattr(pos, "avg_entry_price", 0)) or 0.0)
        snaps = api.chain_snapshots(u)
        s = snaps.get(occ)
        if s is None or getattr(s, "latest_quote", None) is None:
            return skip(f"covered call {occ}: no live quote, holding")
        bid, ask = _quote_pair(s.latest_quote)
        if entry_prem > 0 and bid and bid <= entry_prem * config.TP_CLOSE_FRACTION:
            limit = min((bid + ask) / 2 if ask else bid, bid)
            return [Intent("BUYBACK_CC", u, occ=occ, qty=qty, limit=limit,
                           coid=f"{config.ORDER_PREFIX}-TPC-{occ}",
                           reason=(f"CC take-profit: bid {bid:.2f} <= "
                                   f"{config.TP_CLOSE_FRACTION:.0%} of entry {entry_prem:.2f}"),
                           detail={"entry_prem": entry_prem, "bid": bid})]
        return skip(f"hold covered call {occ} (strike {parse_occ(occ)[3]:.2f}, "
                    f"underlying {st.spot or 'n/a'})")

    return skip("state not handled")
