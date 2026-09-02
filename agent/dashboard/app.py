"""OWL (Option-WheeL) Agent — live dashboard (read-only, zero credentials).

Serves dashboard/data.json, snapshotted from the trading agent's journal and
the Alpaca PAPER account. Hosted copy on Streamlit Community Cloud reads the
file from this repo; nothing here can place an order or see an API key.

Design system: four-tier Alpaca-mint palette with gold reserved for premium
ceremony (pattern adapted from web-design-enhancer, Apache-2.0), 8px spacing
rhythm, tabular numerals, whisper-layered shadows.

Run locally:  streamlit run agent/dashboard/app.py   (from repo root)
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="OWL Agent — Alpaca Hackathon",
                   layout="wide")

HERE = Path(__file__).parent
DATA = json.loads((HERE / "data.json").read_text())
# Backtest export (agent/dashboard/backtest.json). Optional so the hosted
# dashboard never breaks if a deploy predates the backtest run.
try:
    BT = json.loads((HERE / "backtest.json").read_text())
except Exception:
    BT = None

# ------------------------------------------------------------------ tokens ---
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {
  --bg: #F3E6C5; --surface: #FFFFFF; --raised: #F8EFD9;
  --border: rgba(63,50,15,0.18); --border-soft: rgba(63,50,15,0.10);
  --text: #1F2430; --muted: #635B4B; --faint: #6B6353;
  --brand: #FFC61A; --brand-deep: #A87B00; --brand-wash: rgba(255,198,26,0.22);
  --navy: #14181F; --navy-2: #1E242E;
  --good: #15803D; --bad: #C62828; --warn: #9A6700;
}
html, body, [class*="css"] {font-family: 'Inter', -apple-system, sans-serif;
  color: var(--text);}
[data-testid="stMainBlockContainer"] {padding-top: 12px !important;
  padding-bottom: 4px !important;}
[data-testid="stAppViewContainer"] > .main > div {padding-top: 8px !important;}
h1, h2, h3, .wa-title {letter-spacing: -0.16px;}
[data-testid="stHeader"] {background: transparent;}
[data-testid="stHeadingContainer"] h2 {border-left: 3px solid var(--brand);
  padding-left: 10px; margin-top: 22px;}
[data-testid="stToolbar"], [data-testid="stStatusWidget"],
[class="stDeployButton"] {display: none !important;}
/* altair chart element menu ("Show data" etc.) — a raw i/equity table is
   noise for judges; the chart itself carries the information */
[data-testid="stElementToolbar"] {display: none !important;}
#MainMenu, footer {visibility: hidden;}

/* hero band (navy bookend, yellow accents — the alpaca identity) */
.wa-hero {background: linear-gradient(120deg, var(--navy) 0%, #2A2410 90%);
  border: 1px solid rgba(255,214,102,0.25); border-radius: 16px;
  padding: 18px 22px; display: flex; align-items: center;
  justify-content: space-between; gap: 16px; flex-wrap: wrap;
  box-shadow: 0 1px 2px rgba(63,50,15,.20), 0 10px 24px rgba(63,50,15,.14);}
.wa-hero .wa-title {color: #FFFDF6;}
.wa-hero .wa-tag {color: rgba(255,253,246,0.66);}
.wa-mark {width: 52px; height: 52px; border-radius: 14px;
  background: rgba(242,183,5,0.14); border: 1px solid rgba(255,214,102,0.35);
  display: flex; align-items: center; justify-content: center;}
.wa-title {font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em;}
.wa-tag {color: var(--muted); font-size: .82rem; margin-top: 2px;}
.wa-pills {display: flex; gap: 8px; flex-wrap: wrap;}
.wa-pill {font-size: .68rem; font-weight: 700; letter-spacing: .06em;
  text-transform: uppercase; padding: 5px 11px; border-radius: 999px;
  border: 1px solid var(--border); color: var(--muted); white-space: nowrap;
  background: var(--surface);}
.wa-hero .wa-pill {background: transparent; color: rgba(255,253,246,0.62);
  border-color: rgba(255,253,246,0.22);}
.wa-hero .wa-pill.ok {color: #FFD666; border-color: rgba(255,214,102,0.45);
  background: rgba(242,183,5,0.14);}

/* regime ribbon */
.wa-ribbon {border-radius: 12px; padding: 12px 18px; margin: 10px 0 6px 0;
  display: flex; gap: 12px; align-items: baseline; flex-wrap: wrap;
  border: 1px solid var(--border); background: var(--surface);
  box-shadow: 0 1px 2px rgba(63,50,15,.10);}
.wa-ribbon .quote {color: var(--text); font-size: .95rem;}
.wa-ribbon .who {color: var(--muted); font-size: .75rem;}

/* cards */
.wa-row {display: flex; gap: 10px; margin: 6px 0 10px 0; flex-wrap: wrap;}
.wa-card {flex: 1; min-width: 138px; background: var(--surface);
  border: 1px solid var(--border); border-radius: 12px; padding: 13px 15px;
  box-shadow: 0 1px 2px rgba(63,50,15,.10), 0 5px 12px rgba(63,50,15,.06);}
.wa-card.gold {background: var(--brand); border-color: var(--brand-deep);
  box-shadow: 0 2px 4px rgba(63,50,15,.18), 0 8px 18px rgba(196,138,0,.22);}
.wa-card.gold .wa-label {color: rgba(31,36,48,0.72);}
.wa-card.gold .wa-sub {color: rgba(31,36,48,0.66);}
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
  background: var(--surface); white-space: nowrap;}
.wa-step.on {color: var(--navy); background: var(--brand);
  border-color: var(--brand-deep); font-weight: 700;}
.wa-arrow {color: var(--faint); font-size: .8rem;}

/* data tables */
.wa-table {width: 100%; border-collapse: collapse; font-size: .82rem;
  font-variant-numeric: tabular-nums;}
.wa-table th {text-align: left; color: var(--muted); font-size: .64rem;
  text-transform: uppercase; letter-spacing: .07em; font-weight: 700;
  padding: 8px 10px; border-bottom: 1px solid var(--border);
  background: var(--raised);}
.wa-table td {padding: 8px 10px; border-bottom: 1px solid var(--border-soft);
  color: var(--text);}
.wa-table tr:hover td {background: var(--brand-wash);}
.wa-table .num {text-align: right;}
.wa-wrap {border: 1px solid var(--border); border-radius: 12px;
  overflow: hidden; background: var(--surface);
  box-shadow: 0 1px 2px rgba(63,50,15,.08);}
.mono {font-variant-numeric: tabular-nums;}

/* news list */
.wa-news {border-left: 3px solid var(--brand); padding: 2px 0 2px 12px;
  margin: 4px 0;}
.wa-news .h {color: var(--text); font-size: .85rem;}
.wa-news .m {color: var(--faint); font-size: .72rem;}

/* footer band (navy bookend) */
.wa-foot {margin-top: 26px; background: var(--navy);
  border-radius: 12px; padding: 14px 18px; color: rgba(255,253,246,0.75);
  font-size: .74rem; line-height: 1.6;}
.stTabs [data-baseweb="tab-list"] {gap: 4px;
  border-bottom: 1px solid var(--border);}
.stTabs [data-baseweb="tab"] {border-radius: 9px 9px 0 0; padding: 8px 18px;
  color: var(--muted); font-weight: 500;}
.stTabs [data-baseweb="tab"][aria-selected="true"] {background: var(--surface);
  color: var(--brand-deep) !important; font-weight: 650;
  border-bottom: 2px solid var(--brand);}
div[data-testid="stDataFrame"] {border: 1px solid var(--border);
  border-radius: 12px; overflow: hidden;}

/* about / faq */
.wa-note {border: 1px solid var(--border); border-left: 3px solid var(--brand);
  background: var(--raised); border-radius: 10px; padding: 11px 15px;
  font-size: .84rem; color: var(--text); line-height: 1.65;}
.wa-disc {border: 1px dashed var(--border); border-radius: 10px;
  padding: 10px 14px; font-size: .7rem; color: var(--faint);
  line-height: 1.6; margin-top: 8px;}
.wa-links {display: flex; flex-wrap: wrap; gap: 8px; margin: 6px 0 4px 0;}
.wa-link {font-size: .78rem; font-weight: 600; color: var(--brand-deep);
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 999px; padding: 6px 13px; text-decoration: none;
  white-space: nowrap; box-shadow: 0 1px 2px rgba(63,50,15,.08);}
.wa-link:hover {background: var(--brand-wash);}
.wa-legend {display: flex; gap: 18px; font-size: .76rem; color: var(--muted);
  margin: 2px 0 6px 0; align-items: center;}
.wa-legend .sw {display: inline-block; width: 22px; height: 3px;
  border-radius: 2px; margin-right: 6px; vertical-align: middle;}
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
            "gold": "var(--navy)", "accent": "var(--brand-deep)",
            "warn": "var(--warn)"}.get(tone or "", "var(--text)")


def card(label, value, sub=None, tone=None, cls=""):
    subh = (f'<div class="wa-sub">{sub}</div>' if sub else "")
    return (f'<div class="wa-card {cls}"><div class="wa-label">{label}</div>'
            f'<div class="wa-value" style="color:{_tone_color(tone)}">'
            f'{value}</div>{subh}</div>')


def row(html):
    st.markdown(f'<div class="wa-row">{html}</div>', unsafe_allow_html=True)


def _smooth_path(pts):
    """Catmull-Rom to cubic bezier — gentle curves, no stiff segments."""
    if len(pts) < 3:
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[0]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def sparkline_html(entries, w=1100, h=290, pad_l=64, pad_r=64,
                   pad_t=20, pad_b=34):
    """Interactive equity curve: smooth gold area+line, dollar y-labels, UTC
    time x-labels, hover crosshair with live tooltip, draw-in animation.
    Pure server-rendered SVG + vanilla JS inside the components iframe."""
    import json as _json
    vals = [e["equity"] for e in entries]
    if len(vals) < 2:
        return None
    lo, hi = min(vals), max(vals)
    if hi - lo < 1:
        hi = lo + 1.0
    vpad = (hi - lo) * 0.18
    lo, hi = lo - vpad, hi + vpad
    n = len(vals)
    xs = [pad_l + (w - pad_l - pad_r) * i / (n - 1) for i in range(n)]
    ys = [pad_t + (h - pad_t - pad_b) * (1 - (v - lo) / (hi - lo))
          for v in vals]
    pts = list(zip(xs, ys))
    line = _smooth_path(pts)
    area = (line + f" L{xs[-1]:.1f},{h - pad_b:.1f} "
            f"L{xs[0]:.1f},{h - pad_b:.1f} Z")

    grid = []
    for k in range(4):
        v = lo + (hi - lo) * k / 3
        y = pad_t + (h - pad_t - pad_b) * (1 - k / 3)
        grid.append(
            f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w - pad_r}" y2="{y:.1f}" '
            f'stroke="rgba(63,50,15,0.10)"/>'
            f'<text x="{pad_l - 9}" y="{y + 4:.1f}" text-anchor="end" '
            f'font-size="11" fill="#6F6757">${v / 1000:.1f}k</text>')
    for k in range(5):
        i = round((n - 1) * k / 4)
        x = xs[i]
        ts = str(entries[i].get("ts", ""))
        label = (ts[5:10] + " " + ts[11:16]) if k == 0 else ts[11:16]
        grid.append(
            f'<line x1="{x:.1f}" y1="{h - pad_b}" x2="{x:.1f}" '
            f'y2="{h - pad_b + 5}" stroke="rgba(63,50,15,0.25)"/>'
            f'<text x="{x:.1f}" y="{h - pad_b + 19}" text-anchor="middle" '
            f'font-size="10.5" fill="#8A8272">{label}</text>')
    grid.append(
        f'<text x="{w - pad_r}" y="{h - pad_b + 19}" text-anchor="end" '
        f'font-size="10" fill="#8A8272" opacity="0">UTC</text>')

    pdata = _json.dumps([
        {"x": round(x, 1), "y": round(y, 1),
         "t": str(e.get("ts", ""))[11:16], "d": str(e.get("ts", ""))[5:10],
         "v": round(v, 0)}
        for x, y, v, e in zip(xs, ys, vals, entries)])

    js = """
<script>
(function(){
  var PTS = __PDATA__;
  var W = __W__, H = __H__;
  var svg = document.getElementById('waSpark');
  var tip = document.getElementById('waTip');
  var cross = document.getElementById('waCross');
  var dot = document.getElementById('waDot');
  svg.addEventListener('mousemove', function(ev){
    var r = svg.getBoundingClientRect();
    var vx = (ev.clientX - r.left) * (W / r.width);
    var best = 0, bd = 1e12;
    for (var i = 0; i < PTS.length; i++){
      var d = Math.abs(PTS[i].x - vx);
      if (d < bd){ bd = d; best = i; }
    }
    var p = PTS[best];
    cross.setAttribute('x1', p.x); cross.setAttribute('x2', p.x);
    cross.style.display = '';
    dot.setAttribute('cx', p.x); dot.setAttribute('cy', p.y);
    dot.style.display = '';
    tip.style.display = 'block';
    tip.innerHTML = '<b style="color:#FFC61A">$' + p.v.toLocaleString() +
      '</b>&nbsp; ' + p.d + ' ' + p.t + ' UTC · cycle ' + (best + 1);
    var px = r.left + p.x * (r.width / W);
    var py = r.top + p.y * (r.height / H);
    tip.style.left = Math.max(px - tip.offsetWidth / 2, 8) + 'px';
    tip.style.top = (py - tip.offsetHeight - 14) + 'px';
  });
  svg.addEventListener('mouseleave', function(){
    tip.style.display = 'none';
    cross.style.display = 'none'; dot.style.display = 'none';
  });
})();
</script>"""
    js = js.replace("__PDATA__", pdata).replace("__W__", str(w)).replace("__H__", str(h))

    return (
        '<div style="position:relative;font-family:Inter,-apple-system,sans-serif">'
        f'<svg id="waSpark" viewBox="0 0 {w} {h}" width="100%" '
        'style="display:block;cursor:crosshair;background:#FFFFFF;'
        'border:1px solid rgba(63,50,15,0.16);border-radius:12px">'
        '<defs><linearGradient id="eqg" x1="0" y1="1" x2="0" y2="0">'
        '<stop offset="0" stop-color="rgba(201,138,0,0.02)"/>'
        '<stop offset="1" stop-color="rgba(201,138,0,0.32)"/>'
        '</linearGradient></defs>'
        + "".join(grid)
        + f'<path d="{area}" fill="url(#eqg)" style="animation:wafade .8s ease"/>'
        f'<path d="{line}" fill="none" stroke="#C98A00" stroke-width="2.4" '
        'class="wa-line"/>'
        f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="4.5" fill="#C98A00" '
        f'stroke="#FFFFFF" stroke-width="1.5"/>'
        f'<text x="{xs[-1]:.1f}" y="{ys[-1] - 10:.1f}" text-anchor="end" '
        f'font-size="11.5" font-weight="700" fill="#635B4B">'
        f'${vals[-1]:,.0f}</text>'
        '<line id="waCross" y1="' + str(pad_t) + '" y2="' + str(h - pad_b) +
        '" stroke="rgba(63,50,15,0.35)" stroke-dasharray="3 3" style="display:none"/>'
        '<circle id="waDot" r="5" fill="#FFC61A" stroke="#14181F" '
        'stroke-width="1.5" style="display:none"/>'
        '</svg>'
        '<div id="waTip" style="position:fixed;display:none;pointer-events:none;'
        'background:#14181F;color:#FFFDF6;font-size:12px;padding:6px 11px;'
        'border-radius:8px;white-space:nowrap;box-shadow:0 6px 18px rgba(0,0,0,.3);'
        'z-index:99"></div>'
        '<style>@keyframes wafade{from{opacity:0}to{opacity:1}}'
        '.wa-line{stroke-dasharray:4000;stroke-dashoffset:4000;'
        'animation:wadraw 1.1s ease forwards}'
        '@keyframes wadraw{to{stroke-dashoffset:0}}</style>'
        + js + '</div>')


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


def dual_line_html(entries, w=1100, h=300, pad_l=64, pad_r=70,
                   pad_t=16, pad_b=32):
    """Backtest equity: strategy (gold) vs SPY buy-and-hold (muted navy).
    Same visual language as the live sparkline; hover shows both values."""
    import json as _json
    if len(entries) < 2:
        return None
    vals_s = [e["strategy"] for e in entries]
    vals_b = [e["spy"] for e in entries]
    lo, hi = min(vals_s + vals_b), max(vals_s + vals_b)
    vpad = (hi - lo) * 0.14 or 1.0
    lo, hi = lo - vpad, hi + vpad
    n = len(entries)
    xs = [pad_l + (w - pad_l - pad_r) * i / (n - 1) for i in range(n)]
    ys_s = [pad_t + (h - pad_t - pad_b) * (1 - (v - lo) / (hi - lo))
            for v in vals_s]
    ys_b = [pad_t + (h - pad_t - pad_b) * (1 - (v - lo) / (hi - lo))
            for v in vals_b]
    line_s = _smooth_path(list(zip(xs, ys_s)))
    line_b = _smooth_path(list(zip(xs, ys_b)))

    grid = []
    for k in range(4):
        v = lo + (hi - lo) * k / 3
        y = pad_t + (h - pad_t - pad_b) * (1 - k / 3)
        grid.append(
            f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w - pad_r}" y2="{y:.1f}" '
            'stroke="rgba(63,50,15,0.10)"/>'
            f'<text x="{pad_l - 9}" y="{y + 4:.1f}" text-anchor="end" '
            'font-size="11" fill="#6F6757">$%sk</text>' % round(v / 1000))
    months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
              "Sep", "Oct", "Nov", "Dec"]
    for k in range(5):
        i = round((n - 1) * k / 4)
        x = xs[i]
        dt = str(entries[i].get("date", ""))
        label = f"{months[int(dt[5:7])]} {dt[2:4]}" if dt else ""
        grid.append(
            f'<line x1="{x:.1f}" y1="{h - pad_b}" x2="{x:.1f}" '
            f'y2="{h - pad_b + 5}" stroke="rgba(63,50,15,0.25)"/>'
            f'<text x="{x:.1f}" y="{h - pad_b + 19}" text-anchor="middle" '
            f'font-size="10.5" fill="#8A8272">{label}</text>')

    pdata = _json.dumps([
        {"x": round(x, 1), "sy": round(a, 1), "by": round(b, 1),
         "d": str(e.get("date", ""))[5:10], "sv": round(s, 0), "bv": round(v, 0)}
        for x, a, b, e, s, v in zip(xs, ys_s, ys_b, entries, vals_s, vals_b)])
    js = """
<script>
(function(){
  var P = __PDATA__, W = __W__, H = __H__;
  var svg = document.getElementById('waBt');
  var tip = document.getElementById('waBtTip');
  var cross = document.getElementById('waBtCross');
  svg.addEventListener('mousemove', function(ev){
    var r = svg.getBoundingClientRect();
    var vx = (ev.clientX - r.left) * (W / r.width);
    var best = 0, bd = 1e12;
    for (var i = 0; i < P.length; i++){
      var dd = Math.abs(P[i].x - vx); if (dd < bd){ bd = dd; best = i; }
    }
    var p = P[best];
    cross.setAttribute('x1', p.x); cross.setAttribute('x2', p.x);
    cross.style.display = '';
    tip.style.display = 'block';
    var ds = (p.sv - 100000) / 1000, db = (p.bv - 100000) / 1000;
    tip.innerHTML = '<b style="color:#FFC61A">wheel $' + p.sv.toLocaleString() +
      '</b> (' + (ds >= 0 ? '+' : '') + ds.toFixed(1) + 'k)<br>' +
      '<span style="color:#9AA3B2">SPY $' + p.bv.toLocaleString() + '</span> (' +
      (db >= 0 ? '+' : '') + db.toFixed(1) + 'k)&nbsp;· ' + p.d;
    var px = r.left + p.x * (r.width / W);
    var py = r.top + p.sy * (r.height / H);
    tip.style.left = Math.max(px - tip.offsetWidth / 2, 8) + 'px';
    tip.style.top = (py - tip.offsetHeight - 12) + 'px';
  });
  svg.addEventListener('mouseleave', function(){
    tip.style.display = 'none'; cross.style.display = 'none';
  });
})();
</script>"""
    js = js.replace("__PDATA__", pdata).replace("__W__", str(w)).replace("__H__", str(h))
    return (
        '<div style="position:relative;font-family:Inter,-apple-system,sans-serif">'
        f'<svg id="waBt" viewBox="0 0 {w} {h}" width="100%" '
        'style="display:block;cursor:crosshair;background:#FFFFFF;'
        'border:1px solid rgba(63,50,15,0.16);border-radius:12px">'
        + "".join(grid)
        + f'<path d="{line_b}" fill="none" stroke="#7A8494" stroke-width="1.7" '
        'stroke-dasharray="1 0" opacity="0.85"/>'
        + f'<path d="{line_s}" fill="none" stroke="#C98A00" stroke-width="2.4"/>'
        + f'<circle cx="{xs[-1]:.1f}" cy="{ys_s[-1]:.1f}" r="4" fill="#C98A00" '
        'stroke="#FFFFFF" stroke-width="1.4"/>'
        + f'<text x="{xs[-1]:.1f}" y="{ys_s[-1] - 9:.1f}" text-anchor="end" '
        'font-size="11" font-weight="700" fill="#635B4B">$%s</text>'
        % f"{vals_s[-1] / 1000:,.1f}k"
        + '<line id="waBtCross" y1="' + str(pad_t) + '" y2="' + str(h - pad_b) +
        '" stroke="rgba(63,50,15,0.35)" stroke-dasharray="3 3" style="display:none"/>'
        '</svg>'
        '<div id="waBtTip" style="position:fixed;display:none;pointer-events:none;'
        'background:#14181F;color:#FFFDF6;font-size:12px;padding:6px 11px;'
        'border-radius:8px;white-space:nowrap;box-shadow:0 6px 18px rgba(0,0,0,.3);'
        'z-index:99;line-height:1.5"></div>' + js + '</div>')


def monthly_bars_html(monthly, w=1100, h=120, pad_b=22, pad_t=14):
    """Monthly gross premium collected — small gold bars, native SVG tooltips."""
    if not monthly:
        return None
    vals = [m["premium"] for m in monthly]
    hi = max(vals) or 1.0
    n = len(monthly)
    gap = 3
    bw = (w - 8 - gap * (n - 1)) / n
    bars = []
    for i, m in enumerate(monthly):
        bh = max((h - pad_b - pad_t) * m["premium"] / hi, 1.5)
        x = 4 + i * (bw + gap)
        y = h - pad_b - bh
        label = (m["month"][5:7] if i == 0 else
                 (m["month"][5:7] if i % 4 == 0 else ""))
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
            'rx="2" fill="#C98A00" opacity="0.92">'
            f'<title>{m["month"]}: ${m["premium"]:,.0f} premium</title></rect>')
        if label:
            bars.append(
                f'<text x="{x + bw / 2:.1f}" y="{h - 7}" text-anchor="middle" '
                f'font-size="9.5" fill="#8A8272">{label}</text>')
    return (
        f'<svg viewBox="0 0 {w} {h}" width="100%" style="display:block;'
        'background:#FFFFFF;border:1px solid rgba(63,50,15,0.16);'
        'border-radius:12px">' + "".join(bars) + '</svg>')


acct = DATA.get("account", {})
stats = DATA.get("stats", {})
rl = DATA.get("risk_limits", {})

# ------------------------------------------------------------ hero band ---
# "updated" in data.json is tz-aware (US/Eastern) — normalize to UTC for the
# label so the suffix below is truthful.
try:
    updated = (datetime.fromisoformat(str(DATA.get("updated", "")))
               .astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M"))
except ValueError:
    updated = str(DATA.get("updated", ""))[:16].replace("T", " ")
# Minimalist geometric owl — thin gold strokes on the navy hero, angular
# head with ear tufts, ring eyes, diamond beak (institutional-terminal look).
OWL_SVG = ('<svg viewBox="0 0 36 36" width="34" height="34" aria-label="owl">'
           '<path d="M7 5.5 L12.5 9 L23.5 9 L29 5.5 L29 19 L26 28 L18 31 '
           'L10 28 L7 19 Z" fill="none" stroke="#FFD666" stroke-width="1.8" '
           'stroke-linejoin="round"/>'
           '<circle cx="13.2" cy="16.5" r="4.2" fill="none" stroke="#FFD666" '
           'stroke-width="1.8"/>'
           '<circle cx="22.8" cy="16.5" r="4.2" fill="none" stroke="#FFD666" '
           'stroke-width="1.8"/>'
           '<circle cx="13.2" cy="16.5" r="1.5" fill="#FFD666"/>'
           '<circle cx="22.8" cy="16.5" r="1.5" fill="#FFD666"/>'
           '<path d="M18 21.5 L16.5 24.3 L18 26 L19.5 24.3 Z" fill="#FFD666"/>'
           '</svg>')

st.markdown(
    f'<div class="wa-hero"><div style="display:flex;gap:14px;align-items:center">'
    f'<div class="wa-mark">{OWL_SVG}</div><div><div class="wa-title">OWL Agent</div>'
    f'<div class="wa-tag">autonomous OWL-Options WheeL agent · AI-vetoed · built '
    f'on Alpaca hackathon Lablab.ai</div>'
    f'</div></div><div class="wa-pills">'
    + pill("paper only", "ok")
    + pill(("market open" if DATA.get("market_open") else "market closed"),
           "ok" if DATA.get("market_open") else "")
    + pill(f"updated {updated} UTC")
    + "</div></div>", unsafe_allow_html=True)

tabs = st.tabs(["Command Center", "Risk Lab", "AI Brain",
                "Execution Desk", "About", "FAQ"])

# ---------------------------------------------------------------- Command ---
with tabs[0]:
    upl = stats.get("unrealized_pl", 0) or 0
    prem = DATA.get("premium_net_collected", 0) or 0
    realized = DATA.get("realized_closed_legs", 0) or 0
    # Run anchor = equity at the first journaled cycle of this account. Alpaca's
    # day_start_equity resets every trading day, which would drift the anchor
    # across a multi-day judged run.
    curve = DATA.get("equity_curve") or []
    anchor = (curve[0].get("equity") if curve else None) \
        or acct.get("day_start_equity")
    row(
        card("Equity", fmt_usd(acct.get("equity")),
             sub=f"anchor {fmt_usd(anchor)}")
        + card("Premium secured", fmt_usd(prem, signed=True),
               sub=(f"{stats.get('fills', 0)} fills · incl. "
                    f"{fmt_usd(realized, signed=True)} realized (closed leg)"
                    if realized else
                    f"{stats.get('fills', 0)} fills · realized cash income"),
               cls="gold" if prem >= 0 else "",
               tone=None if prem >= 0 else "bad")
        + card("Unrealized P&L", fmt_usd(upl, signed=True),
               sub="premium vs. cost-to-close · not realized",
               tone="good" if upl >= 0 else "bad")
        + card("Open positions", str(len(DATA.get("positions", []))),
               sub=f"{stats.get('live_cycles', 0)} live "
                   f"cycle{'s' if stats.get('live_cycles', 0) != 1 else ''}"))
    st.caption("Premium secured is realized cash — banked at fill, kept whether the "
               "open shorts expire worthless Friday or get assigned. Unrealized P&L "
               "is only the cost to close those shorts today; it converges to the "
               "full premium if the puts stay out of the money.")

    st.subheader("Equity curve — every cycle, from the decision journal")
    entries = [e for e in DATA.get("equity_curve", [])
               if e.get("equity") is not None]
    html = sparkline_html(entries)
    if html:
        # components.html bypasses the markdown pipeline, which truncates
        # inline SVG (learned the hard way: DOM stopped after first </text>)
        import streamlit.components.v1 as components
        components.html(html, height=320, scrolling=False)
        st.caption(f"{len(entries)} cycles · hover the chart: crosshair + tooltip per cycle · server-rendered SVG, no charting library")

    # regime ribbon
    hist = DATA.get("regime_history", [])
    if hist:
        last = hist[-1]
        tone = {"RISK_ON": ("var(--good)", "rgba(21,128,61,.10)"),
                "RISK_OFF": ("var(--bad)", "rgba(198,40,40,.10)"),
                }.get(last.get("regime"), ("var(--warn)", "rgba(154,103,0,.10)"))
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
                 sub=f"{len(fills)} fills", cls="gold"))
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

# ------------------------------------------------------------------ About ---
with tabs[4]:
    st.subheader("Why this exists")
    st.markdown(
        '<div class="wa-note">Retail options income is <b>manual, emotional and '
        'error-prone</b>: the wrong delta, panic buy-backs, one ticker oversized. '
        'The usual "AI trading agent" answer — let an LLM pick trades — makes that '
        'worse: LLMs hallucinate, drift, and cannot be held to a risk mandate.<br><br>'
        '<b>The OWL Agent inverts the design.</b> A deterministic engine does 100% '
        'of the trading on hard-coded rails. A Claude layer sits above it with '
        'exactly two powers: <b>read the regime</b> and <b>veto a new entry</b>. '
        'It can never place, size or force a trade — and it can never block an exit. '
        'An AI that can only refuse is an AI you can actually trust on a broker.</div>',
        unsafe_allow_html=True)

    st.subheader("One cycle, six steps")
    st.markdown(
        '<div class="wa-steps">'
        '<span class="wa-step on">1 · Observe</span><span class="wa-arrow">→</span>'
        '<span class="wa-step on">2 · Gate</span><span class="wa-arrow">→</span>'
        '<span class="wa-step on">3 · Decide</span><span class="wa-arrow">→</span>'
        '<span class="wa-step on">4 · AI veto</span><span class="wa-arrow">→</span>'
        '<span class="wa-step on">5 · Execute</span><span class="wa-arrow">→</span>'
        '<span class="wa-step on">6 · Journal</span></div>'
        '<div class="wa-note" style="border-left-color:var(--navy)">Every cycle: '
        'account & market snapshot (broker is the source of truth) → kill-switch, '
        'drawdown stop and <i>two</i> regime readers (Claude\'s judgment <b>and</b> a '
        'deterministic SPY anchor — the tighter of the two governs) → per-name wheel '
        'decisions on hard quality filters → Claude reviews each proposed entry, one '
        'refusal with a reason kills it → marketable-limit orders only, exits before '
        'entries → everything appended to a public JSONL decision journal.</div>',
        unsafe_allow_html=True)

    # ------------------------------------------------------------ backtest ---
    st.subheader("Backtested on real Alpaca data — 2.5 years, the bot picks 3 stocks a week")
    if BT:
        s, b = BT["strategy"], BT["benchmark_spy"]
        win = BT.get("window", {})
        legs = BT.get("option_legs", {})
        cal_s = s["cagr"] / max(s["max_drawdown"], 0.01)
        cal_b = b["cagr"] / max(b["max_drawdown"], 0.01)
        row(
            card("Total return", f"{s['total_return']:+.1f}%",
                 sub=f"selection-first variant — SPY {b['total_return']:+.1f}%, "
                     "beats the index; live 5-name engine's run: +32.2%",
                 tone="good" if s["total_return"] >= b["total_return"] else "warn",
                 cls="gold" if s["total_return"] >= b["total_return"] else "")
            + card("Calmar (CAGR÷DD)", f"{cal_s:.2f}",
                   sub=f"SPY {cal_b:.2f} — more growth per unit of drawdown",
                   tone="good" if cal_s >= cal_b else "warn")
            + card("Max drawdown", f"{s['max_drawdown']:.1f}%",
                   sub=f"SPY {b['max_drawdown']:.1f}% — the price of concentration",
                   tone="good" if s["max_drawdown"] <= b["max_drawdown"] else "warn")
            + card("Option legs", str(legs.get("total", "—")),
                   sub=f"win rate {legs.get('win_rate_pct', '—')}% · "
                       f"PF {legs.get('profit_factor', '—')}")
            + card("Premium collected", fmt_usd(BT.get("premiums_collected_gross", 0)),
                   sub=f"{win.get('start', '')} → {win.get('end', '')}"))
        st.markdown(
            '<div class="wa-note" style="margin-top:4px"><b>What this run is.</b> '
            "The <b>selection-first variant</b>: each Monday the bot scores a "
            "24-name universe (SMA200 quality gate + 63-day momentum + premium "
            "richness) and sells cash-secured puts on the <b>top 3 names only</b>, "
            "equal-weight 24% each. Engine rules, fees and fill model are "
            "identical to the live agent; no parameter was fitted to this "
            "window. The <b>live engine</b> currently runs the diversified "
            "5-name version — its own 2.5-year run on this same window and data "
            "(+32.2%, max DD 18.3%, every premium a real traded option bar) is "
            "published alongside in "
            '<a href="https://github.com/guntoken/alpaca-wheel-agent/tree/main/'
            'agent/runs/bt-2026-08-29_wheel-csp-cc_1Day" target="_blank">'
            "agent/runs/</a>; the K=1/2/3/5 sweep that selected this mode is in "
            '<a href="https://github.com/guntoken/alpaca-wheel-agent/tree/main/'
            'agent/runs/bt-2026-08-30_topk-sweep" target="_blank">the sweep '
            "folder</a>.</div>", unsafe_allow_html=True)
        chart = dual_line_html(BT.get("equity_curve", []))
        if chart:
            st.markdown(
                '<div class="wa-legend"><span><span class="sw" '
                'style="background:#C98A00"></span>Top-3 weekly picks '
                '(2.5-yr backtest)</span>'
                '<span><span class="sw" style="background:#7A8494"></span>SPY '
                'buy-and-hold</span><span style="margin-left:auto;color:var(--faint)"> '
                'hover for detail</span></div>', unsafe_allow_html=True)
            # components.html bypasses the markdown pipeline, which truncates
            # inline SVG after the first </text>
            import streamlit.components.v1 as components
            components.html(chart, height=330, scrolling=False)
        bars = monthly_bars_html(BT.get("monthly_premium", []))
        if bars:
            st.markdown(
                '<div class="wa-legend" style="margin-top:10px"><span><span class="sw" '
                'style="background:#C98A00"></span>Gross premium written, by month'
                '</span></div>', unsafe_allow_html=True)
            import streamlit.components.v1 as components
            components.html(bars, height=150, scrolling=False)
        st.markdown(
            '<div class="wa-note"><b>Methodology.</b> '
            + " · ".join(BT.get("methodology", [])) +
            '<br><b>Data.</b> ' + BT.get("data", "") +
            '<br><b>Honesty clause.</b> ' + BT.get("caveats", "") + '</div>',
            unsafe_allow_html=True)
        st.markdown(
            '<div class="wa-disc"><b>Disclosure.</b> ' + BT.get("disclosure", "") +
            ' Fees modeled at $0.50/contract/side (Alpaca fee schedule). Full run '
            'artifacts — notes, spec, trades, equity curve, data fingerprint — in '
            'the run folder linked below.</div>', unsafe_allow_html=True)
    else:
        st.info("Backtest export not found (agent/dashboard/backtest.json) — "
                "the run folder keeps the full methodology either way.")

    st.subheader("Methodology & paper trail — everything is auditable")
    st.markdown(
        '<div class="wa-links">'
        '<a class="wa-link" href="https://github.com/guntoken/alpaca-wheel-agent/'
        'blob/main/agent/journal.jsonl">Live decision journal (JSONL)</a>'
        '<a class="wa-link" href="https://github.com/guntoken/alpaca-wheel-agent/'
        'tree/main/agent/runs/bt-2026-08-29_wheel-csp-cc_1Day">Backtest run '
        'folder (full artifacts)</a>'
        '<a class="wa-link" href="https://github.com/guntoken/alpaca-wheel-agent/'
        'blob/main/docs/RESEARCH_NOTES.md">Research notes — every source, '
        'adopt or reject</a>'
        '<a class="wa-link" href="https://github.com/guntoken/alpaca-wheel-agent/'
        'blob/main/docs/WRITEUP.md">One-page technical write-up</a>'
        '<a class="wa-link" href="https://github.com/guntoken/alpaca-wheel-agent/'
        'blob/main/docs/BUSINESS_CASE.md">Business case</a>'
        '<a class="wa-link" href="https://github.com/guntoken/alpaca-wheel-agent/'
        'blob/main/README.md">README</a></div>'
        '<div class="wa-note" style="border-left-color:var(--good)">The strategy '
        'is not invented for the demo: parameters are validated source-by-source '
        'in RESEARCH_NOTES.md (Alpaca\'s official wheel guide, peer-reviewed '
        'volatility research — Rustamov et al. 2024, inverted for premium selling '
        '— practitioner consensus, and a production-grade open agent system), '
        'with every adoption <i>and</i> rejection written down. The live agent '
        'has run unattended on Alpaca paper since day 1 of the hackathon, and '
        'its own journal caught two production bugs on night 1 — both fixed '
        'live, both public.</div>',
        unsafe_allow_html=True)

    st.subheader("Built on all three Alpaca surfaces")
    row(card("Trading API", "alpaca-py", sub="the engine — orders, OPRA greeks")
        + card("CLI", "alpaca 0.0.13", sub="ops & monitoring · backtest data")
        + card("MCP server", "connected", sub="broker surface in the AI session"))

# --------------------------------------------------------------------- FAQ ---
with tabs[5]:
    st.subheader("Questions we get — answered honestly")
    faqs = [
        ("Is this trading real money?",
         "No. The account is <b>Alpaca paper</b> and the paper endpoint is "
         "hard-coded — the code cannot reach a live-money endpoint even by "
         "mistake. The dashboard is read-only and contains zero credentials."),
        ("What does the AI actually do?",
         "Two things only. Each cycle Claude reads an Alpaca-native market "
         "summary (SPY/QQQ trend, SPY dollar-vol percentile, GLD/VIXY/BTC "
         "moves, filtered news) and classifies the tape RISK_ON / NEUTRAL / "
         "RISK_OFF with a stated reason — which scales the engine's budget. "
         "Then it reviews every proposed <i>entry</i>; one veto with a reason "
         "kills it. It cannot place, size or force trades, and it cannot veto "
         "an exit or a buy-back — de-risking is always allowed."),
        ("Why an AI that can only say NO?",
         "Because that is the part of an LLM you can actually trust. A veto-only "
         "layer cannot hallucinate a trade, cannot churn the account for "
         "engagement, and its every refusal is journaled verbatim on the AI "
         "Brain tab. Deterministic rails do the trading; the LLM is the risk "
         "governor. Incentive alignment by construction."),
        ("Backtest or live run — which one proves it?",
         "Both, for different claims. Two 2.5-year backtests are published, on "
         "the same window and the same real Alpaca option-trade data: the "
         "<b>live engine's own rules</b> (+32.2%, max DD 18.3%, zero re-tuning) "
         "and the <b>selection-first variant</b> shown above (+54.6% vs SPY "
         "+45.6%, Calmar 1.39 vs 1.34 — the bot picks 3 stocks a week). The "
         "window includes the Aug-2024 VIX spike and the Apr-2025 tariff "
         "drawdown, and the concentrated mode's deeper drawdown (21.5%) is "
         "shown, not hidden. The <b>live run</b> shows the full system — engine "
         "plus AI governor — trading unattended on Alpaca paper since day 1 of "
         "the hackathon, journal and all. The AI layer is deliberately not "
         "replayed in any backtest: a backtest of the judge would be circular."),
        ("What happens in a crash?",
         "Hard gates, not vibes: budget halves in a weak tape and goes to zero "
         "at SPY −4% intraday; no new entries after a −3% daily drawdown; at "
         "most 5 names, 2 per correlated sector, 72% of equity as total "
         "collateral; exit quality floors on every entry; a kill-switch file "
         "halts all submissions. Try the live stress test on the Risk Lab tab, "
         "and the Aug-2024 / Apr-2025 episodes on the About tab's equity curve."),
        ("What if a put gets assigned?",
         "That is the wheel working, not failing. Assignment converts the "
         "collateral into shares at the strike; the engine then sells covered "
         "calls above max(cost basis, upper Bollinger) until called away — and "
         "a challenged put is only ever bought back when a fresh put's premium "
         "covers the closing cost (roll for credit, else hold). No panic "
         "buy-backs by design."),
        ("Why these twelve tickers?",
         "Liquid US names with weekly options whose contract size fits a "
         "$100k account, spanning nine sectors so the sector cap means "
         "something. They were chosen for liquidity and size before the "
         "backtest ran — not picked by optimizing on the backtest window."),
        ("How do I know the numbers are real?",
         "Everything is public: the live decision journal (agent/journal.jsonl) "
         "with every order and reason, the commit history (bugs found and fixed "
         "in the open), and the backtest run folder with notes, spec, trade "
         "list, equity curve and a data fingerprint of every raw file. No "
         "screenshot you have to take on faith."),
        ("Can it lose money?",
         "Yes. Short puts keep stock-like downside below the strike, covered "
         "calls cap upside, and a sideways-crash sequence can draw the book "
         "down — that is what every gate on the Risk Lab tab exists to bound, "
         "not eliminate. Paper trading, educational build, not investment "
         "advice."),
        ("What is next?",
         "A defined-risk spreads sleeve (the account tier already permits it), "
         "walk-forward re-validation of the gates, multi-account support, and "
         "the same veto-only governor pattern offered as a safety layer for "
         "anyone else's trading agent. One direction is already explored and "
         "measured above: <b>selection-first picking</b>, where the bot scores "
         "a 24-name universe and wheels only the week's best names. The full "
         "sweep is public in <i>agent/runs/</i>: picking the single best name "
         "returned +46% in one year but lost its edge over the full 2.5-year "
         "window (a starting-state lesson we published rather than hid), "
         "while the balanced <b>top-3 mode beat SPY over 2.5 years</b> "
         "(+54.6% vs +45.6%) at the cost of a deeper drawdown. It would ship "
         "opt-in behind tighter drawdown limits — momentum screens buy tops "
         "in mean-reverting years, and we say so on the slide, not in a "
         "footnote."),
    ]
    for q, a in faqs:
        with st.expander(q):
            st.markdown(a, unsafe_allow_html=True)

st.markdown(
    '<div class="wa-foot"><b>OWL Agent</b> — Alpaca AI Trading Agents '
    'Hackathon 2026 · paper trading only · no real money · no performance '
    'guarantee · not investment advice · options involve substantial risk · '
    'built on Alpaca Trading API, CLI and MCP server.</div>',
    unsafe_allow_html=True)
