"""Wheel Agent — live dashboard (read-only, zero credentials).

Serves dashboard/data.json, snapshotted from the trading agent's journal and
the Alpaca PAPER account. Hosted copy on Streamlit Community Cloud reads the
file from this repo; nothing here can place an order or see an API key.

Design system: four-tier Alpaca-mint palette with gold reserved for premium
ceremony (pattern adapted from web-design-enhancer, Apache-2.0), 8px spacing
rhythm, tabular numerals, whisper-layered shadows.

Run locally:  streamlit run agent/dashboard/app.py   (from repo root)
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Wheel Agent — Alpaca Hackathon",
                   page_icon="🦉", layout="wide")

HERE = Path(__file__).parent
DATA = json.loads((HERE / "data.json").read_text())

# ------------------------------------------------------------------ tokens ---
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {
  --bg: #050507; --surface: #0D0F12; --raised: #12151A;
  --border: rgba(255,255,255,0.08); --border-soft: rgba(255,255,255,0.05);
  --text: #EDEDEF; --muted: #8A8F98; --faint: #5B616B;
  --teal-300: #5FE8C9; --teal-500: #00D3A7; --teal-900: #07231C;
  --teal-wash: rgba(0,211,167,0.09);
  --gold: #E8C475; --gold-wash: rgba(232,196,117,0.10);
  --good: #22C55E; --bad: #EF4444; --warn: #F5A524;
}
html, body, [class*="css"] {font-family: 'Inter', -apple-system, sans-serif;
  color: var(--text);}
[data-testid="stMainBlockContainer"] {padding-top: 12px !important;
  padding-bottom: 4px !important;}
[data-testid="stAppViewContainer"] > .main > div {padding-top: 8px !important;}
h1, h2, h3, .wa-title {letter-spacing: -0.16px;}
[data-testid="stHeader"] {background: transparent;}
[data-testid="stHeadingContainer"] h2 {border-left: 3px solid var(--teal-500);
  padding-left: 10px; margin-top: 22px;}
[data-testid="stToolbar"], [data-testid="stStatusWidget"],
[class="stDeployButton"] {display: none !important;}
#MainMenu, footer {visibility: hidden;}

/* hero band (dark bookend) */
.wa-hero {background: linear-gradient(120deg, var(--teal-900) 0%, var(--bg) 65%);
  border: 1px solid var(--border); border-radius: 16px;
  padding: 18px 22px; display: flex; align-items: center;
  justify-content: space-between; gap: 16px; flex-wrap: wrap;
  box-shadow: 0 1px 2px rgba(0,0,0,.28), 0 10px 24px rgba(0,0,0,.16);}
.wa-mark {width: 46px; height: 46px; border-radius: 12px;
  background: var(--teal-wash); border: 1px solid rgba(95,232,201,.25);
  display: flex; align-items: center; justify-content: center;}
.wa-title {font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em;}
.wa-tag {color: var(--muted); font-size: .82rem; margin-top: 2px;}
.wa-pills {display: flex; gap: 8px; flex-wrap: wrap;}
.wa-pill {font-size: .68rem; font-weight: 700; letter-spacing: .06em;
  text-transform: uppercase; padding: 5px 11px; border-radius: 999px;
  border: 1px solid var(--border); color: var(--muted); white-space: nowrap;}
.wa-pill.ok {color: var(--teal-300); border-color: rgba(95,232,201,.3);
  background: var(--teal-wash);}
.wa-pill.warn {color: var(--warn); border-color: rgba(245,165,36,.3);
  background: rgba(245,165,36,.08);}

/* regime ribbon */
.wa-ribbon {border-radius: 12px; padding: 12px 18px; margin: 10px 0 6px 0;
  display: flex; gap: 12px; align-items: baseline; flex-wrap: wrap;
  border: 1px solid var(--border); background: var(--surface);}
.wa-ribbon .quote {color: var(--text); font-size: .95rem;}
.wa-ribbon .who {color: var(--muted); font-size: .75rem;}

/* cards */
.wa-row {display: flex; gap: 10px; margin: 6px 0 10px 0; flex-wrap: wrap;}
.wa-card {flex: 1; min-width: 138px; background: var(--surface);
  border: 1px solid var(--border); border-radius: 12px; padding: 13px 15px;
  box-shadow: 0 1px 2px rgba(0,0,0,.22), 0 6px 14px rgba(0,0,0,.12);}
.wa-label {color: var(--muted); font-size: .64rem; font-weight: 700;
  letter-spacing: .08em; text-transform: uppercase;}
.wa-value {font-size: 1.5rem; font-weight: 750; margin-top: 4px;
  letter-spacing: -0.02em; font-variant-numeric: tabular-nums;}
.wa-sub {color: var(--faint); font-size: .75rem; margin-top: 3px;
  font-variant-numeric: tabular-nums;}

/* wheel stepper */
.wa-steps {display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
  margin: 4px 0 14px 0;}
.wa-step {font-size: .78rem; font-weight: 600; padding: 6px 12px;
  border-radius: 999px; border: 1px solid var(--border); color: var(--faint);
  background: transparent; white-space: nowrap;}
.wa-step.on {color: #062B23; background: var(--teal-500);
  border-color: var(--teal-500); font-weight: 700;}
.wa-arrow {color: var(--faint); font-size: .8rem;}

/* data tables */
.wa-table {width: 100%; border-collapse: collapse; font-size: .82rem;
  font-variant-numeric: tabular-nums;}
.wa-table th {text-align: left; color: var(--muted); font-size: .64rem;
  text-transform: uppercase; letter-spacing: .07em; font-weight: 700;
  padding: 8px 10px; border-bottom: 1px solid var(--border);}
.wa-table td {padding: 8px 10px; border-bottom: 1px solid var(--border-soft);}
.wa-table tr:hover td {background: rgba(255,255,255,0.025);}
.wa-table .num {text-align: right;}
.wa-wrap {border: 1px solid var(--border); border-radius: 12px;
  overflow: hidden; background: var(--surface);}
.mono {font-variant-numeric: tabular-nums;}

/* news list */
.wa-news {border-left: 2px solid var(--border); padding: 2px 0 2px 12px;
  margin: 4px 0;}
.wa-news .h {color: var(--text); font-size: .85rem;}
.wa-news .m {color: var(--faint); font-size: .72rem;}

/* footer band (dark bookend) */
.wa-foot {margin-top: 26px; background: var(--teal-900);
  border-radius: 12px; padding: 14px 18px; color: rgba(255,255,255,.72);
  font-size: .74rem; line-height: 1.6;}
.stTabs [data-baseweb="tab-list"] {gap: 4px;
  border-bottom: 1px solid var(--border);}
.stTabs [data-baseweb="tab"] {border-radius: 9px 9px 0 0; padding: 8px 18px;
  color: var(--muted); font-weight: 500;}
.stTabs [data-baseweb="tab"][aria-selected="true"] {background: var(--surface);
  color: var(--teal-500) !important; font-weight: 650;
  border-bottom: 2px solid var(--teal-500);}
div[data-testid="stDataFrame"] {border: 1px solid var(--border);
  border-radius: 12px; overflow: hidden;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------------------------- helpers ---
def fmt_usd(v, signed=False):
    if v is None:
        return "—"
    if signed:
        return ("−" if v < 0 else "+") + f"${abs(v):,.0f}"
    return f"${v:,.0f}"


def _tone_color(tone):
    return {"good": "var(--good)", "bad": "var(--bad)",
            "gold": "var(--gold)", "accent": "var(--teal-500)",
            "warn": "var(--warn)"}.get(tone or "", "var(--text)")


def card(label, value, sub=None, tone=None):
    subh = (f'<div class="wa-sub">{sub}</div>' if sub else "")
    return (f'<div class="wa-card"><div class="wa-label">{label}</div>'
            f'<div class="wa-value" style="color:{_tone_color(tone)}">'
            f'{value}</div>{subh}</div>')


def row(html):
    st.markdown(f'<div class="wa-row">{html}</div>', unsafe_allow_html=True)


def pill(text, cls=""):
    return f'<span class="wa-pill {cls}">{text}</span>'


def html_table(headers, rows_html):
    head = "".join(f'<th class="{"num" if h.startswith("#") else ""}">'
                   f'{h.lstrip("#")}</th>' for h in headers)
    body = "".join(f'<tr>{r}</tr>' for r in rows_html)
    st.markdown(f'<div class="wa-wrap"><table class="wa-table">'
                f'<thead><tr>{head}</tr></thead><tbody>{body}</tbody>'
                f'</table></div>', unsafe_allow_html=True)


def td(v, cls="", color=None):
    c = f' style="color:{color}"' if color else ""
    return f'<td class="{cls}"{c}>{v}</td>'


acct = DATA.get("account", {})
stats = DATA.get("stats", {})
rl = DATA.get("risk_limits", {})

# ------------------------------------------------------------ hero band ---
updated = str(DATA.get("updated", ""))[:16].replace("T", " ")
OWL_SVG = ('<svg viewBox="0 0 32 32" width="28" height="28" aria-label="owl">'
           '<circle cx="16" cy="16" r="12.5" stroke="#5FE8C9" stroke-width="2" fill="none"/>'
           '<circle cx="11.5" cy="13" r="2.7" fill="#00D3A7"/>'
           '<circle cx="20.5" cy="13" r="2.7" fill="#00D3A7"/>'
           '<path d="M16 17.5 L14.2 21.5 H17.8 Z" fill="#00D3A7"/>'
           '<path d="M7 21 Q11 26.5 16 26.5 Q21 26.5 25 21" stroke="#5FE8C9"'
           ' stroke-width="2" fill="none"/></svg>')

st.markdown(
    f'<div class="wa-hero"><div style="display:flex;gap:14px;align-items:center">'
    f'<div class="wa-mark">{OWL_SVG}</div><div><div class="wa-title">WHEEL AGENT</div>'
    f'<div class="wa-tag">autonomous options wheel · AI-vetoed · built on Alpaca</div>'
    f'</div></div><div class="wa-pills">'
    + pill("paper only", "ok")
    + pill(("market open" if DATA.get("market_open") else "market closed"),
           "ok" if DATA.get("market_open") else "")
    + pill(f"updated {updated} UTC")
    + "</div></div>", unsafe_allow_html=True)

tabs = st.tabs(["🕹 Command Center", "🧪 Risk Lab", "🧠 AI Brain", "⚙️ Execution Desk"])

# ---------------------------------------------------------------- Command ---
with tabs[0]:
    upl = stats.get("unrealized_pl", 0) or 0
    prem = DATA.get("premium_net_collected", 0) or 0
    row(
        card("Equity", fmt_usd(acct.get("equity")),
             sub=f"anchor {fmt_usd(acct.get('day_start_equity'))}")
        + card("Premium collected", fmt_usd(prem, signed=True),
               sub=f"{stats.get('fills', 0)} fills — the wheel's income",
               tone="gold" if prem >= 0 else "bad")
        + card("Unrealized P&L", fmt_usd(upl, signed=True), sub="mark-to-market",
               tone="good" if upl >= 0 else "bad")
        + card("Open positions", str(len(DATA.get("positions", []))),
               sub=f"{stats.get('live_cycles', 0)} live cycles"))

    st.subheader("Equity curve — every cycle, from the decision journal")
    curve = pd.DataFrame(DATA.get("equity_curve", []))
    if not curve.empty:
        try:
            import altair as alt
            df = curve[["equity"]].reset_index()
            df.columns = ["i", "equity"]
            lo, hi = float(df.equity.min()), float(df.equity.max())
            pad = max((hi - lo) * 0.35, 120.0)
            grad = alt.LinearGradient(
                x1=1, x2=1, y1=1, y2=0,
                stops=[alt.GradientStop(color="rgba(0,211,167,0.35)", offset=0),
                       alt.GradientStop(color="rgba(0,211,167,0.02)", offset=1)])
            base = alt.Chart(df).encode(
                x=alt.X("i:O", axis=None, title=None),
                y=alt.Y("equity:Q", scale=alt.Scale(domain=[lo - pad, hi + pad]),
                        title=None,
                        axis=alt.Axis(format="$,.0", tickCount=4,
                                      labelColor="#8A8F98")),
                tooltip=[alt.Tooltip("i:O", title="cycle"),
                         alt.Tooltip("equity:Q", format="$,.0f")])
            chart = (base.mark_area(color=grad, interpolate="monotone")
                     + base.mark_line(color="#00D3A7", strokeWidth=2,
                                      interpolate="monotone")
                     ).properties(height=250).configure_view(stroke=None
                     ).configure_axisX(grid=False, domain=False, labels=False,
                                       ticks=False
                     ).configure_axisY(gridColor="rgba(255,255,255,0.05)",
                                       domainColor="rgba(255,255,255,0.10)",
                                       ticks=False, titleColor="#8A8F98")
            st.altair_chart(chart, use_container_width=True)
        except Exception as e:
            st.line_chart(curve.set_index("ts")["equity"], height=250)
            st.caption(f"(fallback chart: {e})")

    # regime ribbon
    hist = DATA.get("regime_history", [])
    if hist:
        last = hist[-1]
        tone = {"RISK_ON": ("var(--teal-300)", "rgba(0,211,167,.08)"),
                "RISK_OFF": ("var(--bad)", "rgba(239,68,68,.08)"),
                }.get(last.get("regime"), ("var(--warn)", "rgba(245,165,36,.07)"))
        st.markdown(
            f'<div class="wa-ribbon" style="border-color:{tone[1]}">'
            f'<span class="wa-pill" style="color:{tone[0]};border-color:{tone[1]};'
            f'background:{tone[1]}">{last.get("regime")}</span>'
            f'<span class="quote">“{last.get("reason")}”</span>'
            f'<span class="who">— Claude, this cycle · anchor says '
            f'{last.get("det") or "—"}'
            + (f' · SPY {last.get("spy_pct"):+.2f}%' if last.get("spy_pct") is not None else "")
            + '</span></div>', unsafe_allow_html=True)

    st.subheader("The wheel, per underlying")
    by_under: dict[str, list] = {}
    for p in DATA.get("positions", []):
        by_under.setdefault(p["underlying"], []).append(p)
    if by_under:
        steps_def = ["① cash", "② sell CSP", "③ assigned", "④ covered call"]
        for u, plist in by_under.items():
            kinds = {p["kind"] for p in plist}
            if "equity" in kinds:
                active = 4 if any("call" in k for k in kinds) else 3
            elif any("put" in k for k in kinds):
                active = 2
            else:
                active = 1
            steps = "".join(
                f'<span class="wa-step{" on" if i == active else ""}">{s}</span>'
                + ('<span class="wa-arrow">→</span>' if i < 3 else "")
                for i, s in enumerate(steps_def, start=1))
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:12px">'
                f'<span style="font-weight:800;font-size:1.05rem">{u}</span>'
                f'<div class="wa-steps" style="margin:2px 0">{steps}</div></div>',
                unsafe_allow_html=True)
    else:
        st.write("No open positions — stage ① (cash, scanning).")

    st.subheader("Macro context the AI reads (all Alpaca-native data)")
    macro = (DATA.get("market_context") or {}).get("macro", {})
    if macro:
        parts = ""
        for name in ("GLD", "VIXY", "BTC"):
            m = macro.get(name) or {}
            day = m.get("day_pct", 0) or 0
            tone = ("bad" if (name == "VIXY" and day > 2)
                    or (name in ("GLD", "BTC") and day < -3) else None)
            parts += card(name, f"{day:+.2f}%",
                          sub=(f"vs SMA20 {m.get('vs_sma20_pct'):+.1f}%"
                               if m.get("vs_sma20_pct") is not None else ""), tone=tone)
        news = macro.get("news") or {}
        parts += card("News", f"{len(news.get('headlines', []))} h/l",
                      sub="LLM reads them raw")
        row(parts)
        for h in news.get("headlines", [])[:5]:
            st.markdown(f'<div class="wa-news"><div class="h">{h["headline"]}</div>'
                        f'<div class="m">{h.get("source","")} · '
                        f'{str(h.get("ts",""))[:16]}</div></div>',
                        unsafe_allow_html=True)

# ------------------------------------------------------------------ Risk ---
with tabs[1]:
    st.subheader("Positions")
    pos = DATA.get("positions", [])
    if pos:
        rows_html = []
        for p in sorted(pos, key=lambda x: x["underlying"]):
            pl = p.get("unrealized_pl") or 0
            rows_html.append(
                td(f"<b>{p['underlying']}</b>")
                + td(p["kind"])
                + td(f"{p['strike']:.2f}" if p.get("strike") else "—")
                + td(p.get("expiry") or "—", cls="", )
                + td(int(abs(p.get("qty") or 0)), cls="num")
                + td(f"{p['avg_entry']:.2f}" if p.get("avg_entry") else "—", cls="num")
                + td(f"{p['mark']:.2f}" if p.get("mark") else "—", cls="num")
                + td(fmt_usd(pl, signed=True), cls="num",
                     color=("var(--good)" if pl >= 0 else "var(--bad)"))
                + td(fmt_usd(p.get("collateral")), cls="num"))
        html_table(["underlying", "kind", "strike", "expiry", "#qty",
                    "#entry", "#mark", "#uP&L", "#collateral"], rows_html)
        cap = (acct.get("equity", 0) or 0) * rl.get("max_collateral_pct", 0)
        st.caption(f"Per-underlying collateral cap: {fmt_usd(cap)} "
                   f"({rl.get('max_collateral_pct', 0):.0%} of equity) · max "
                   f"{rl.get('max_underlyings')} underlyings · "
                   f"{rl.get('max_per_sector')} per sector")

    st.subheader("Stress test — what a selloff tonight would do")
    cards = ""
    rows_stress = []
    for sh in (-0.01, -0.02, -0.05):
        book_pl, at_risk, itm = 0.0, 0.0, []
        for p in DATA.get("positions", []):
            if "put" not in (p.get("kind") or ""):
                continue
            spot, strike = p.get("spot") or 0, p.get("strike") or 0
            qty = abs(p.get("qty") or 0)
            prem = (p.get("avg_entry") or 0) * 100 * qty
            owed = max(0.0, strike - spot * (1 + sh)) * 100 * qty
            book_pl += prem - owed
            if strike > spot * (1 + sh):
                at_risk += p.get("collateral") or 0
                itm.append(p["underlying"])
        cards += card(f"SPY {sh:+.0%}", fmt_usd(book_pl, signed=True),
                      sub=f"{len(itm)} ITM · risk {fmt_usd(at_risk)}",
                      tone="good" if book_pl >= 0 else "bad")
        rows_stress.append(
            td(f"{sh:+.0%}")
            + td(fmt_usd(book_pl, signed=True), cls="num",
                 color=("var(--good)" if book_pl >= 0 else "var(--bad)"))
            + td(fmt_usd(at_risk), cls="num")
            + td(", ".join(sorted(set(itm))) or "—"))
    row(cards)
    html_table(["shock", "#est. book P&L", "#collateral at risk", "ITM underlyings"],
               rows_stress)
    st.caption("Uniform-shock approximation (beta 1, no vol expansion) — a floor, not a forecast.")

    st.subheader("Safety rails (hard-coded, not decorations)")
    rails = [
        ("Paper-only", "PAPER=True hard-coded; live endpoint not resolvable"),
        ("Collateral caps", f"{rl.get('max_collateral_pct', 0):.0%}/underlying · "
         f"{rl.get('max_total_collateral_pct', 0):.0%} total · clamped to broker options BP"),
        ("Diversification", f"max {rl.get('max_underlyings')} underlyings · "
         f"{rl.get('max_per_sector')} per sector"),
        ("Entry quality", f"CSP Δ≈{rl.get('csp_target_delta')} · OI ≥ 200 · spread ≤ 15% · "
         "vol percentile ≥ 40th of own history"),
        ("Exits", f"{rl.get('tp_close_fraction', 0):.0%} take-profit · roll only for credit · "
         "never buy back a challenged put at a big debit"),
        ("Drawdown stop", f"no new entries past −{rl.get('daily_drawdown_stop', 0):.0%}/day"),
        ("Kill switch", "agent/KILL file halts all submissions"),
    ]
    html_table(["rail", "detail"],
               [td(f"<b>{a}</b>") + td(b) for a, b in rails])

# -------------------------------------------------------------- AI Brain ---
with tabs[2]:
    st.markdown("#### The AI that can only say NO")
    st.caption("Claude never places or sizes a trade. Each cycle it reads the "
               "market summary, classifies the regime, and may veto proposed "
               "entries — verbatim reasoning below, straight from the journal.")
    if hist:
        rows_reg = []
        for h in reversed(hist[-12:]):
            tone = ("var(--teal-300)" if h.get("regime") == "RISK_ON"
                    else "var(--bad)" if h.get("regime") == "RISK_OFF"
                    else "var(--warn)")
            rows_reg.append(
                td(str(h.get("ts", ""))[:16])
                + td(f"<b style='color:{tone}'>{h.get('regime')}</b>")
                + td(h.get("det") or "—")
                + td(f"{h.get('spy_pct'):+.2f}%" if h.get("spy_pct") is not None else "—", cls="num")
                + td(h.get("reason") or ""))
        html_table(["ts (UTC)", "AI regime", "anchor", "#SPY %", "Claude's reasoning"],
                   rows_reg)
    vetoes = DATA.get("ai_vetoes", [])
    row(card("Entries vetoed by the AI", str(len(vetoes)),
             sub="it can only say NO", tone="accent"))
    if vetoes:
        html_table(["ts", "contract", "reason"],
                   [td(str(v.get("ts", ""))[:16]) + td(v.get("occ", "")) + td(v.get("note", ""))
                    for v in vetoes])

    st.subheader("Decision feed (deterministic engine)")
    feed = pd.DataFrame(DATA.get("decisions_feed", [])[-40:])
    if not feed.empty:
        st.dataframe(feed[["ts", "cycle", "kind", "underlying", "reason"]],
                     width='stretch', hide_index=True)

# ------------------------------------------------------------ Execution ---
with tabs[3]:
    st.subheader("Fills (paper)")
    fills = DATA.get("fills", [])
    if fills:
        row(card("Net premium collected", fmt_usd(DATA.get("premium_net_collected", 0), signed=True),
                 sub=f"{len(fills)} fills", tone="gold"))
        html_table(["ts", "contract", "side", "#qty", "#price", "#notional"],
                   [td(str(f.get("ts", ""))[:16])
                    + td(f["symbol"])
                    + td(f["side"], color=("var(--good)" if f["side"] == "sell" else "var(--bad)"))
                    + td(int(f["qty"]), cls="num")
                    + td(f"{f['price']:.2f}", cls="num")
                    + td(fmt_usd(f["notional"]), cls="num")
                    for f in reversed(fills)])
    st.subheader("Open orders")
    oo = DATA.get("open_orders", [])
    if oo:
        html_table(["contract", "side", "#qty", "#limit", "status"],
                   [td(o["symbol"])
                    + td(o["side"])
                    + td(int(o["qty"] or 0), cls="num")
                    + td(f"{o['limit']:.2f}" if o.get("limit") else "—", cls="num")
                    + td(o.get("status", "")) for o in oo])
    else:
        st.caption("none open")
    st.subheader("Runtime")
    row(card("Kill switch", "ARMED — HALT" if stats.get("kill_switch") else "off",
             sub="agent/KILL file",
             tone="bad" if stats.get("kill_switch") else "accent")
        + card("Cycles journaled", str(stats.get("cycles_total", 0)),
               sub=f"{stats.get('live_cycles', 0)} live")
        + card("Endpoint", "paper-api", sub="alpaca.markets · dashboard is read-only"))

st.markdown(
    '<div class="wa-foot">🦉 <b>Wheel Agent</b> — Alpaca AI Trading Agents '
    'Hackathon 2026 · paper trading only · no real money · no performance '
    'guarantee · not investment advice · options involve substantial risk · '
    'built on Alpaca Trading API, CLI and MCP server.</div>',
    unsafe_allow_html=True)
