"""Wheel Agent — live dashboard (read-only, zero credentials).

Serves dashboard/data.json, snapshotted from the trading agent's journal and
the Alpaca PAPER account. Hosted copy on Streamlit Community Cloud reads the
file from this repo; nothing here can place an order or see an API key.

Run locally:  streamlit run agent/dashboard/app.py
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Wheel Agent — Alpaca Hackathon",
                   page_icon="🦉", layout="wide")

HERE = Path(__file__).parent
DATA = json.loads((HERE / "data.json").read_text())

st.title("🦉 Wheel Agent — autonomous options wheel, AI-vetoed")
st.caption(
    f"Alpaca AI Trading Agents Hackathon 2026 · PAPER TRADING ONLY · "
    f"data updated {str(DATA.get('updated', ''))[:19]} UTC")

acct = DATA.get("account", {})
stats = DATA.get("stats", {})
rl = DATA.get("risk_limits", {})

tabs = st.tabs(["🕹 Command Center", "🧪 Risk Lab", "🧠 AI Brain", "⚙️ Execution Desk"])

# ---------------------------------------------------------------- Command ---
with tabs[0]:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Equity", f"${acct.get('equity', 0):,.0f}")
    c2.metric("Net premium collected", f"${DATA.get('premium_net_collected', 0):,.0f}")
    c3.metric("Unrealized P&L", f"${stats.get('unrealized_pl', 0):,.0f}")
    c4.metric("Open positions", len(DATA.get("positions", [])))
    c5.metric("Cycles (live)", f"{stats.get('live_cycles', 0)}")

    curve = pd.DataFrame(DATA.get("equity_curve", []))
    if not curve.empty:
        curve = curve.set_index("ts")["equity"]
        st.subheader("Equity curve (every cycle, from the decision journal)")
        st.line_chart(curve, height=260)

    st.subheader("Market regime — two independent readers, tighter one governs")
    hist = DATA.get("regime_history", [])
    if hist:
        last = hist[-1]
        b1, b2 = st.columns(2)
        b1.metric("AI regime (Claude)", last.get("regime") or "-",
                  f"SPY {last.get('spy_pct')}% d/d" if last.get("spy_pct") is not None else None)
        b2.metric("Deterministic anchor", last.get("det") or "-")
        st.info(f"🧠 Claude said: “{last.get('reason')}”", icon="🧠")

    st.subheader("The wheel, per underlying")
    by_under: dict[str, list] = {}
    for p in DATA.get("positions", []):
        by_under.setdefault(p["underlying"], []).append(p)
    if by_under:
        chips = st.columns(len(by_under))
        for chip, (u, plist) in zip(chips, by_under.items()):
            kinds = {p["kind"] for p in plist}
            if "equity" in kinds:
                stage = "④ shares held → selling covered calls" if any(
                    "call" in k for k in kinds) else "③ assigned → CC next cycle"
            elif any("put" in k for k in kinds):
                stage = "② short put — collecting premium"
            else:
                stage = "① cash — scanning for CSPs"
            chip.markdown(f"**{u}**\n\n`{stage}`\n\n{len(plist)} leg(s)")
    else:
        st.write("No open positions — stage ① (cash, scanning).")

# ------------------------------------------------------------------ Risk ---
with tabs[1]:
    st.subheader("Positions")
    pos = pd.DataFrame(DATA.get("positions", []))
    if not pos.empty:
        show = pos[["underlying", "kind", "strike", "expiry", "qty",
                    "avg_entry", "mark", "unrealized_pl", "collateral", "spot"]]
        show.columns = ["underlying", "kind", "strike", "expiry", "qty",
                        "entry", "mark", "uP&L", "collateral $", "spot"]
        st.dataframe(show, width='stretch')
        st.bar_chart(pos.groupby("underlying")["collateral"].sum()
                     if "collateral" in pos else None, height=220)
        cap = (acct.get("equity", 0) or 0) * rl.get("max_collateral_pct", 0)
        st.caption(f"Per-underlying collateral cap: ${cap:,.0f} "
                   f"({rl.get('max_collateral_pct', 0):.0%} of equity). "
                   f"Max {rl.get('max_underlyings')} underlyings, "
                   f"{rl.get('max_per_sector')} per sector.")

    st.subheader("Stress test — what a selloff tonight would do")
    shocks = [-0.01, -0.02, -0.05]
    cols = st.columns(len(shocks))
    rows = []
    for col, sh in zip(cols, shocks):
        book_pl = 0.0
        at_risk = 0.0
        itm = []
        for p in DATA.get("positions", []):
            if "put" not in (p.get("kind") or ""):
                continue
            spot = p.get("spot") or 0
            strike = p.get("strike") or 0
            qty = abs(p.get("qty") or 0)
            prem = (p.get("avg_entry") or 0) * 100 * qty
            new_spot = spot * (1 + sh)
            owed = max(0.0, strike - new_spot) * 100 * qty
            book_pl += prem - owed
            if strike > new_spot:
                at_risk += p.get("collateral") or 0
                itm.append(p["underlying"])
        col.metric(f"SPY {sh:+.0%}", f"${book_pl:+,.0f}",
                   f"{len(itm)} put(s) ITM", delta_color="inverse")
        rows.append({"shock": f"{sh:+.0%}", "est. book P&L": f"${book_pl:+,.0f}",
                     "collateral at risk": f"${at_risk:,.0f}",
                     "ITM underlyings": ", ".join(sorted(set(itm))) or "—"})
    st.table(pd.DataFrame(rows))
    st.caption("Uniform-shock approximation: every underlying moves with SPY, "
               "beta 1, no vol expansion. Reality is messier — this is a floor, "
               "not a forecast.")

    st.subheader("Safety rails (hard-coded, not dashboard decorations)")
    rails = pd.DataFrame([
        ["Paper-only", "PAPER=True hard-coded; live endpoint not even resolvable"],
        ["Collateral caps", f"{rl.get('max_collateral_pct', 0):.0%}/underlying, "
         f"{rl.get('max_total_collateral_pct', 0):.0%} total, clamped to broker "
         "options buying power"],
        ["Diversification", f"max {rl.get('max_underlyings')} underlyings, "
         f"{rl.get('max_per_sector')} per sector"],
        ["Entry quality", f"CSP delta {rl.get('csp_target_delta')} ± band, OI ≥ 200, "
         "spread ≤ 15%, vol-percentile ≥ 40th pct of own history"],
        ["Exits", f"take-profit at {rl.get('tp_close_fraction', 0):.0%} of credit; "
         "roll only for net credit; never buy back a challenged put at a big debit"],
        ["Daily drawdown stop", f"no new entries past −{rl.get('daily_drawdown_stop', 0):.0%}"],
        ["Kill switch", "agent/KILL file halts all submissions"],
    ], columns=["rail", "detail"])
    st.dataframe(rails, width='stretch', hide_index=True)

# ---------------------------------------------------------------- AI Brain ---
with tabs[2]:
    st.subheader("The AI that can only say NO")
    st.markdown(
        "Claude never places or sizes a trade. Each cycle it reads the market "
        "summary, classifies the regime, and may veto proposed entries. "
        "It can tighten risk; it can never force a trade. Below are its actual "
        "words, verbatim from the decision journal.")
    if hist:
        df = pd.DataFrame(hist[-15:])[["ts", "regime", "det", "spy_pct", "reason"]]
        df.columns = ["ts (UTC)", "AI regime", "anchor", "SPY %", "Claude's reasoning"]
        st.dataframe(df, width='stretch', hide_index=True)
    vetoes = DATA.get("ai_vetoes", [])
    st.metric("Entries vetoed so far", len(vetoes))
    if vetoes:
        st.dataframe(pd.DataFrame(vetoes), width='stretch', hide_index=True)

    st.subheader("Decision feed (deterministic engine)")
    feed = pd.DataFrame(DATA.get("decisions_feed", [])[-40:])
    if not feed.empty:
        feed = feed[["ts", "cycle", "kind", "underlying", "reason"]]
        st.dataframe(feed, width='stretch', hide_index=True)

# ------------------------------------------------------------- Execution ---
with tabs[3]:
    st.subheader("Open orders")
    oo = pd.DataFrame(DATA.get("open_orders", []))
    st.dataframe(oo if not oo.empty else pd.DataFrame([{"status": "none open"}]),
                 width='stretch', hide_index=True)

    st.subheader("Fills (paper)")
    fills = pd.DataFrame(DATA.get("fills", []))
    if not fills.empty:
        st.metric("Net premium collected", f"${DATA.get('premium_net_collected', 0):,.0f}")
        st.dataframe(fills.iloc[::-1], width='stretch', hide_index=True)

    st.subheader("Runtime")
    r1, r2, r3 = st.columns(3)
    r1.metric("Kill switch", "ARMED-HALT" if stats.get("kill_switch") else "off (trading enabled)")
    r2.metric("Cycles journaled", stats.get("cycles_total", 0))
    r3.metric("Paper endpoint", "paper-api.alpaca.markets")
    st.caption("Orders are submitted only by the local agent with --live; this "
               "dashboard is read-only and credential-free.")

st.divider()
st.caption("Educational hackathon build. Paper trading only — no real money, no "
           "performance guarantee, not investment advice. Options involve "
           "substantial risk. Built on Alpaca's Trading API, CLI and MCP server.")
