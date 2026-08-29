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

# --- theme: modern-dark fintech (ui-ux-pro-max guidance, MIT) with an
# Alpaca-inspired mint-teal accent; financial semantics green/red stay native
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, button, [class*="css"], [data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {
    font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
}
h1, h2, h3 {letter-spacing: -0.02em;}
section[data-testid="stMetric"] {
    background: #0D0F12;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 14px 16px 10px 16px;
}
section[data-testid="stMetric"] > div > label {
    color: #8A8F98 !important;
    text-transform: uppercase;
    font-size: 0.70rem;
    letter-spacing: 0.05em;
    font-weight: 600;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px 9px 0 0;
    padding: 8px 18px;
    color: #8A8F98;
    font-weight: 500;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: #0D0F12;
    color: #00D3A7 !important;
    font-weight: 650;
    border-bottom: 2px solid #00D3A7;
}
[data-testid="stHeader"] {background: transparent;}
[data-testid="stHeadingContainer"] h2 {
    border-left: 3px solid #00D3A7;
    padding-left: 10px;
}
div[data-testid="stDataFrame"] {border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; overflow: hidden;}
/* hide default streamlit chrome (deploy button, status) for a product feel */
[data-testid="stToolbar"], [data-testid="stStatusWidget"],
[class="stDeployButton"] {display: none !important;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)


def fmt_usd(v, signed: bool = False) -> str:
    if v is None:
        return "—"
    if signed:
        return ("−" if v < 0 else "+") + f"${abs(v):,.0f}"
    return f"${v:,.0f}"


def _card(label: str, value: str, sub: str | None = None,
          tone: str | None = None) -> str:
    """A metric card with real surface, border and financial color semantics
    (profit green / loss red / accent teal / neutral off-white)."""
    color = {"good": "#22C55E", "bad": "#EF4444",
             "accent": "#00D3A7"}.get(tone or "", "#EDEDEF")
    subh = (f'<div style="color:#8A8F98;font-size:0.76rem;margin-top:3px">{sub}</div>'
            if sub else "")
    return (f'<div style="flex:1;min-width:130px;background:#0D0F12;'
            f'border:1px solid rgba(255,255,255,0.08);border-radius:12px;'
            f'padding:13px 15px;">'
            f'<div style="color:#8A8F98;font-size:0.66rem;font-weight:700;'
            f'letter-spacing:0.07em;text-transform:uppercase;">{label}</div>'
            f'<div style="color:{color};font-size:1.5rem;font-weight:700;'
            f'margin-top:4px;letter-spacing:-0.02em;">{value}</div>{subh}</div>')


def card_row(html: str) -> None:
    st.markdown(f'<div style="display:flex;gap:10px;margin:4px 0 8px 0;">{html}</div>',
                unsafe_allow_html=True)

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
    upl = stats.get("unrealized_pl", 0) or 0
    prem = DATA.get("premium_net_collected", 0) or 0
    card_row(
        _card("Equity", fmt_usd(acct.get("equity", 0)),
              sub=f"day anchor {fmt_usd(acct.get('day_start_equity'))}")
        + _card("Net premium collected", fmt_usd(prem, signed=True),
                sub=f"{stats.get('fills', 0)} fills", tone="good" if prem >= 0 else "bad")
        + _card("Unrealized P&L", fmt_usd(upl, signed=True),
                sub="mark-to-market", tone="good" if upl >= 0 else "bad")
        + _card("Open positions", str(len(DATA.get("positions", []))),
                sub=f"{stats.get('live_cycles', 0)} live cycles")
    )

    curve = pd.DataFrame(DATA.get("equity_curve", []))
    if not curve.empty:
        curve = curve.set_index("ts")["equity"]
        st.subheader("Equity curve (every cycle, from the decision journal)")
        st.line_chart(curve, height=260)

    st.subheader("Market regime — two independent readers, tighter one governs")
    hist = DATA.get("regime_history", [])
    if hist:
        last = hist[-1]
        card_row(
            _card("AI regime (Claude)", last.get("regime") or "—",
                  sub=f"SPY {last.get('spy_pct'):+.2f}% d/d" if last.get("spy_pct") is not None else "LLM judgment",
                  tone="good" if last.get("regime") == "RISK_ON"
                  else ("bad" if last.get("regime") == "RISK_OFF" else "accent"))
            + _card("Deterministic anchor", last.get("det") or "—",
                    sub="SPY-intraday tiers · cannot flicker")
        )
        st.info(f"🧠 Claude said: “{last.get('reason')}”", icon="🧠")

    st.subheader("Macro context the AI reads (all Alpaca-native data)")
    macro = (DATA.get("market_context") or {}).get("macro", {})
    if macro:
        names = {"GLD": "gold · flight to safety", "VIXY": "priced fear",
                 "BTC": "risk appetite"}
        parts = ""
        for name, label in names.items():
            m = macro.get(name) or {}
            day = m.get("day_pct", 0) or 0
            vs20 = m.get("vs_sma20_pct")
            tone = "bad" if (name == "VIXY" and day > 2) or (
                name in ("GLD", "BTC") and day < -3) else None
            parts += _card(name, f"{day:+.2f}% d/d",
                           sub=f"vs SMA20 {vs20:+.1f}%" if vs20 is not None else label,
                           tone=tone)
        news = macro.get("news") or {}
        n_avg = news.get("avg_sentiment")
        parts += _card("News (Alpaca)",
                       f"{n_avg:+.2f}" if n_avg is not None else f"{len(news.get('headlines', []))} h/l",
                       sub=f"{len(news.get('headlines', []))} headlines · LLM reads them")
        card_row(parts)
        if news.get("headlines"):
            for h in news["headlines"][:5]:
                s = h.get("sentiment") or 0
                emoji = "🟢" if s > 0.15 else ("🔴" if s < -0.15 else "⚪")
                st.markdown(f"{emoji} &nbsp;{h['headline']} "
                            f"`sent {h.get('sentiment')}`")

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
    rows = []
    cards = ""
    for sh in shocks:
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
        cards += _card(f"SPY {sh:+.0%}", fmt_usd(book_pl, signed=True),
                       sub=f"{len(itm)} put(s) ITM · risk {fmt_usd(at_risk)}",
                       tone="good" if book_pl >= 0 else "bad")
        rows.append({"shock": f"{sh:+.0%}", "est. book P&L": fmt_usd(book_pl, signed=True),
                     "collateral at risk": fmt_usd(at_risk),
                     "ITM underlyings": ", ".join(sorted(set(itm))) or "—"})
    card_row(cards)
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
    card_row(_card("Entries vetoed by the AI", str(len(vetoes)),
                   sub="it can only say NO", tone="accent"))
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
    card_row(
        _card("Kill switch", "ARMED — HALT" if stats.get("kill_switch") else "off",
              sub="agent/KILL file", tone="bad" if stats.get("kill_switch") else "accent")
        + _card("Cycles journaled", str(stats.get("cycles_total", 0)),
                sub=f"{stats.get('live_cycles', 0)} live")
        + _card("Paper endpoint", "paper-api", sub="alpaca.markets · read-only dashboard")
    )
    st.caption("Orders are submitted only by the local agent with --live; this "
               "dashboard is read-only and credential-free.")

st.divider()
st.caption("Educational hackathon build. Paper trading only — no real money, no "
           "performance guarantee, not investment advice. Options involve "
           "substantial risk. Built on Alpaca's Trading API, CLI and MCP server.")
