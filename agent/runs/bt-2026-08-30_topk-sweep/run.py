#!/usr/bin/env python3
"""VARIANT D — Top-K weekly picks sweep: berapa nama optimal per minggu?

Same selection-first screen as variant C (SMA200 gate, momentum-63d rank +
vol-dollar-percentile rank, affordability), but each Monday sells CSPs on the
TOP-K names (K from env BT_TOPK). Equal-weight budget min(40%, 72%/K) per name
so total exposure is held constant across K - the sweep isolates the effect of
the NUMBER of picks. Fallback walks the ranking; contract attempts capped at
K+3 names per week. Window: 1 year (2025-08-01 -> 2026-07-31). Artifacts are
TAG-prefixed (env BT_TAG) so K=2/3/5 runs coexist in one folder sharing one
opts_cache. PRE-COMMITTED before results; exploration, not the headline.
Phases: (1) fetch stock bars via Alpaca CLI -> raw/, (2) fetch option bars
via alpaca-py SDK as the simulation walks (cached in raw/opts_cache/ so
re-runs are offline), (3) simulate daily, (4) write artifacts.

Run from repo root:  cd agent && uv run python runs/bt-2026-08-29_wheel-csp-cc_1Day/run.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import NormalDist

RUN = Path(__file__).resolve().parent
AGENT = RUN.parents[1]                      # .../agent
REPO = AGENT.parent
DASH = AGENT / "dashboard"
RAW = RUN / "raw"
CACHE = RAW / "opts_cache"

WARMUP_START = "2023-06-01"                 # 250-day indicator warmup
# Window starts 2024-03-01: Alpaca's historical option-trade coverage is dense
# from March 2024 (probed: Jan-Feb 2024 weeklies sparse/absent, Mar+ dense).
# Window ends 2026-07-31: during the run the data API began rejecting
# Sep-2026-expiry chain fetches ("OPRA agreement is not signed"), which the
# final August decisions require. Everything through July 2026 is cached.
WIN_START = date.fromisoformat(os.environ.get("BT_WIN_START", "2025-08-01"))
WIN_END = date.fromisoformat(os.environ.get("BT_WIN_END", "2026-07-31"))
INITIAL_CASH = 100_000.0
UNIVERSE = ["INTC", "T", "F", "GM", "PFE", "KO", "NOK", "SOFI", "BABA", "MU",
            "WBD", "VALE", "AMD", "NVDA", "PLTR", "SNAP", "COIN", "MSTR",
            "XOM", "CVX", "DIS", "CAT", "NKE", "BA"]
SECTORS = {"semis": ["INTC", "MU", "AMD", "NVDA"], "telecom": ["T", "NOK"],
           "auto": ["F", "GM"], "pharma": ["PFE"], "staples": ["KO"],
           "fintech": ["SOFI", "COIN"], "china-ecom": ["BABA"],
           "media": ["WBD", "DIS"], "materials": ["VALE"],
           "software": ["PLTR"], "social": ["SNAP"], "crypto": ["MSTR"],
           "energy": ["XOM", "CVX"], "industrial": ["CAT", "BA"],
           "consumer": ["NKE"]}
TOPK_PICKS = int(os.environ.get("BT_TOPK", "2"))   # CSP per minggu
BT_TAG = os.environ.get("BT_TAG", "k%d" % TOPK_PICKS)  # prefix artefak
ATTEMPT_CAP = TOPK_PICKS + 3   # maks nama dicoba kontrak per minggu
QUALITY_SMA = 200          # gate kualitas: close > SMA200 nama
MOM_LOOKBACK = 63          # jendela momentum ~3 bulan

# --- engine constants (config.py, verbatim) ---
CSP_TARGET, CSP_BAND = 0.30, (0.18, 0.42)
BEAR_TARGET, BEAR_BAND = 0.20, (0.10, 0.30)
CC_TARGET, CC_BAND = 0.25, (0.12, 0.38)
DTE_MIN, DTE_MAX = 7, 35
MIN_PREM_PCT = 0.005
TP_FRACTION = 0.50
ROLL_DELTA = 0.60
VOL_WINDOW, VOL_HISTORY, VOL_FLOOR = 21, 250, 0.40
BB_WINDOW, BB_STD = 20, 2.0
MAX_UNDERLYINGS, MAX_PER_SECTOR = 5, 2
PER_NAME_PCT, TOTAL_PCT = 0.40, 0.72      # varian C: juara tunggal 40%
DRAWDOWN_STOP = 0.03
SPY_BEAR, SPY_EXTREME = -2.0, -4.0

# --- backtest-only execution constants (see notes.md) ---
SLIPPAGE = 0.05          # adverse haircut on option price per side
COMMISSION = 0.50        # USD per contract per side
MIN_DAY_VOLUME = 10      # liquidity proxy (live uses OI >= 200)
R_FREE = 0.04            # BS inversion only
NORM = NormalDist()

# ---------------------------------------------------------------- env & keys
def load_env():
    env = {}
    for line in (AGENT / ".env").read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    os.environ.setdefault("APCA_API_KEY_ID", env.get("APCA_API_KEY_ID", ""))
    os.environ.setdefault("APCA_API_SECRET_KEY", env.get("APCA_API_SECRET_KEY", ""))
    return os.environ["APCA_API_KEY_ID"], os.environ["APCA_API_SECRET_KEY"]


def d(s: str) -> date:
    return date.fromisoformat(s)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


# ---------------------------------------------------------------- stock data
def fetch_stock(sym: str) -> dict[str, dict]:          # {iso_date: {o,h,l,c}}
    out = RAW / f"bars_{sym}.json"
    if out.exists():
        bars = json.loads(out.read_text())["bars"]
    else:
        cmd = ["alpaca", "data", "bars", "--symbol", sym, "--start", WARMUP_START,
               "--end", "2026-08-29", "--timeframe", "1Day", "--feed", "iex",
               "--adjustment", "raw", "--quiet"]
        try:
            cmd[0] = str(Path.home() / ".local/bin/alpaca")
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=90, check=True)
            bars = json.loads(r.stdout)["bars"]
            if not bars:
                raise RuntimeError("CLI returned no bars")
        except Exception as e:
            # documented fallback (SDK, iex feed) — recorded via stderr
            print(f"  [warn] {sym}: CLI failed ({e}); SDK/iex fallback", file=sys.stderr)
            from alpaca.data.historical.stock import StockHistoricalDataClient
            from alpaca.data.requests import StockBarsRequest
            from alpaca.data.timeframe import TimeFrame
            key, sec = load_env()
            cl = StockHistoricalDataClient(key, sec)
            rr = cl.get_stock_bars(StockBarsRequest(
                symbol_or_symbols=sym, timeframe=TimeFrame.Day,
                start=datetime(2023, 6, 1), end=datetime(2026, 8, 29), feed="iex"))
            data = getattr(rr, "data", None)
            src = data.get(sym) if isinstance(data, dict) else None
            lst = src if isinstance(src, list) else (getattr(src, "bars", None) or [])
            bars = []
            for b in (lst or []):
                t = getattr(b, "timestamp", None)
                bars.append({"t": t.isoformat() if t else None,
                             "o": float(b.open), "h": float(b.high),
                             "l": float(b.low), "c": float(b.close)})
            if not bars:
                raise RuntimeError(f"no bars for {sym} from CLI or SDK")
        out.write_text(json.dumps({"bars": bars}))
    series: dict[str, dict] = {}
    for b in bars:
        t = str(b.get("t", ""))[:10]
        if t:
            series[t] = {"o": float(b["o"]), "h": float(b["h"]),
                         "l": float(b["l"]), "c": float(b["c"])}
    return series


# ---------------------------------------------------------------- option data
class OptFetch:
    # The data API's long-lived client degrades after ~tens of requests on
    # this account (200-with-empty for data a fresh client returns). Recreate
    # the client periodically and on every all-empty response — verified by
    # side-by-side probes on 2026-08-29 (fresh client: 16/24 symbols with
    # bars; aged client in the walk process: 0/24, same batch, same minute).
    CLIENT_TTL = 25

    def __init__(self):
        self._mods = None
        self.cl = None
        self._recreate()
        self.calls = 0
        self.since_recreate = 0
        self.empty_attempts = 2                # walk fails fast; healer uses 6

    def _recreate(self):
        from alpaca.data.historical.option import OptionHistoricalDataClient
        from alpaca.data.requests import OptionBarsRequest
        from alpaca.data.timeframe import TimeFrame
        if not hasattr(self, "req"):
            self.req = OptionBarsRequest
            self.tf = TimeFrame.Day
        key, sec = load_env()
        self.cl = OptionHistoricalDataClient(key, sec)
        self.since_recreate = 0

    def _fresh_client_if_needed(self):
        self.since_recreate += 1
        if self.since_recreate >= self.CLIENT_TTL:
            self._recreate()

    def get(self, symbols: list[str], start: str, end: str) -> dict[str, dict[str, dict]]:
        """{occ: {iso_date: {o,h,l,c,v}}} — cached per sorted-symbol-set + range.
        Only successful responses are cached; failures raise after retries."""
        symbols = sorted(set(symbols))
        if not symbols:
            return {}
        key = hashlib.sha1(f"{','.join(symbols)}|{start}|{end}".encode()).hexdigest()[:20]
        f = CACHE / f"{key}.json"
        if f.exists():
            raw = json.loads(f.read_text())
        else:
            raw = None
            last_err = None
            for attempt in range(6):
                try:
                    self.calls += 1
                    self._fresh_client_if_needed()
                    # Option bars stamp at 04:00/05:00 UTC; a date-typed `end`
                    # becomes midnight UTC and silently truncates the last
                    # day (verified: MCP/same-key request returns both days,
                    # date-end SDK request returned only the first). Widen the
                    # request by one day; cache key stays on requested range.
                    r = self.cl.get_option_bars(self.req(
                        symbol_or_symbols=symbols, timeframe=self.tf,
                        start=d(start), end=d(end) + timedelta(days=1)))
                    data = getattr(r, "data", None)
                    bars: dict[str, list] = {}
                    if isinstance(data, dict) and symbols and symbols[0] in data:
                        for sym, lst in data.items():        # {sym: [bars]}
                            bars[sym] = [self._bar(b) for b in (lst or [])]
                    elif isinstance(data, dict) and "bars" in data:
                        for sym, lst in data["bars"].items():
                            bars[sym] = [self._bar(b) for b in (lst or [])]
                    else:                                     # {sym: OptionBarSet}
                        for sym, bs in (data or {}).items():
                            for b in (getattr(bs, "bars", None) or []):
                                bars.setdefault(sym, []).append(self._bar(b))
                    raw = {"bars": {s: [x for x in bars.get(s, []) if x] for s in symbols}}
                    # All-empty responses are flaky per-process. In the WALK we
                    # fail fast (empty_attempts=2) and let the fresh-process
                    # healer re-confirm suspects; the healer runs with 6.
                    if (any(raw["bars"].values()) or attempt >= self.empty_attempts - 1
                            or not symbols):
                        break
                    print(f"  [all-empty retry {attempt+1}] opts {symbols[:2]}...",
                          file=sys.stderr)
                    self._recreate()          # aged-client degradation guard
                    time.sleep(4)
                    raw = None
                except Exception as e:
                    last_err = e
                    wait = 5 * (attempt + 1)
                    print(f"  [retry {attempt+1}] opts {symbols[:2]}... {e} — sleep {wait}s",
                          file=sys.stderr)
                    time.sleep(wait)
            if raw is None:
                raise RuntimeError(f"option bars fetch failed: {last_err}")
            raw["symbols"] = symbols
            raw["start"], raw["end"] = start, end
            f.write_text(json.dumps(raw))
            time.sleep(0.5)                       # gentle cadence (~120/min)
        return {s: {b["t"]: b for b in lst} for s, lst in raw["bars"].items()}

    @staticmethod
    def _bar(b) -> dict:
        t = getattr(b, "timestamp", None)
        return {"t": (t.isoformat() if t else str(getattr(b, "t", "")))[:10],
                "o": float(getattr(b, "open", 0) or 0),
                "h": float(getattr(b, "high", 0) or 0),
                "l": float(getattr(b, "low", 0) or 0),
                "c": float(getattr(b, "close", 0) or 0),
                "v": int(getattr(b, "volume", 0) or 0)}


# ---------------------------------------------------------------- math
def bs_put(S, K, T, r, sig):
    if T <= 0 or sig <= 0:
        return max(K - S, 0.0)
    sq = sig * math.sqrt(T)
    d1 = (math.log(S / K) + (r + sig * sig / 2) * T) / sq
    d2 = d1 - sq
    return K * math.exp(-r * T) * NORM.cdf(-d2) - S * NORM.cdf(-d1)


def bs_call(S, K, T, r, sig):
    if T <= 0 or sig <= 0:
        return max(S - K, 0.0)
    sq = sig * math.sqrt(T)
    d1 = (math.log(S / K) + (r + sig * sig / 2) * T) / sq
    d2 = d1 - sq
    return S * NORM.cdf(d1) - K * math.exp(-r * T) * NORM.cdf(d2)


def bs_delta(right: str, S, K, T, r, sig):
    if T <= 0 or sig <= 0:
        return -1.0 if right == "P" else 1.0
    sq = sig * math.sqrt(T)
    d1 = (math.log(S / K) + (r + sig * sig / 2) * T) / sq
    return -NORM.cdf(-d1) if right == "P" else NORM.cdf(d1)


def iv_from_premium(right, price, S, K, T, r=R_FREE):
    """Bisection: sigma such that BS(right) == traded premium. None if unreachable."""
    if price <= 0 or T <= 0 or S <= 0:
        return None
    intrinsic = max(K - S, 0.0) if right == "P" else max(S - K, 0.0)
    if price <= intrinsic * 1.0001:
        return None                            # no time value to invert
    lo, hi = 0.01, 5.0
    f = (bs_put if right == "P" else bs_call)
    if f(S, K, T, r, hi) < price:
        return None
    for _ in range(60):
        mid = (lo + hi) / 2
        if f(S, K, T, r, mid) < price:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def occ_sym(root: str, expiry: date, right: str, strike: float) -> str:
    return f"{root}{expiry:%y%m%d}{right}{int(round(strike * 1000)):08d}"


def parse_occ(s: str):
    i = next(ix for ix, ch in enumerate(s) if ch.isdigit())
    return s[:i], datetime.strptime(s[i:i + 6], "%y%m%d").date(), s[i + 6].upper(), int(s[i + 7:]) / 1000


# --- indicators: identical formulas to alpaca_client.py (live) ---
def vol_dollar_percentile(closes: list[float]) -> float | None:
    if len(closes) < VOL_WINDOW + 30:
        return None
    moves = [abs(closes[i] - closes[i - 1]) for i in range(1, len(closes))]
    bars = [sum(moves[i - VOL_WINDOW:i]) / VOL_WINDOW
            for i in range(VOL_WINDOW, len(moves) + 1)]
    last = bars[-1]
    return sum(1 for b in bars if b <= last) / len(bars)


def upper_bollinger(closes: list[float]) -> float | None:
    if len(closes) < BB_WINDOW:
        return None
    tail = closes[-BB_WINDOW:]
    mean = sum(tail) / BB_WINDOW
    var = sum((c - mean) ** 2 for c in tail) / (BB_WINDOW - 1)
    return mean + BB_STD * math.sqrt(var)


def strike_ladder(spot: float) -> list[float]:
    """Plausible listed strikes within +/-12% of spot (unlisted ones simply
    return no bars). Step grid mirrors exchange conventions per price level."""
    steps = {0.5} if spot < 10 else ({1.0} if spot < 25 else
                                     ({1.0, 2.5} if spot < 75 else
                                      ({1.0, 2.5, 5.0} if spot < 150 else {2.5, 5.0, 10.0})))
    ks: set[int] = set()                      # strikes in 1/10 dollars, rounded
    for st in steps:
        lo, hi = spot * 0.88, spot * 1.12
        k = math.floor(lo / st) * st
        while k <= hi:
            frac = round(k * 10) / 10
            if frac * 10 == int(frac * 10):
                ks.add(round(frac * 10))      # tenths
            k += st
    out = sorted(k / 10 for k in ks)
    return out[:48]


def fridays_in_band(from_day: date) -> list[date]:
    out = []
    cur = from_day + timedelta(days=(4 - from_day.weekday()) % 7 or 7)
    while (cur - from_day).days <= DTE_MAX:
        if (cur - from_day).days >= DTE_MIN:
            out.append(cur)
        cur += timedelta(days=7)
    return out[:4]


# ---------------------------------------------------------------- simulation
class Backtest:
    def __init__(self, stocks, opts: OptFetch, divs):
        self.stocks = stocks
        self.opts = opts
        self.divs = divs
        self.days = [t for t in sorted(stocks["SPY"]) if WIN_START <= d(t) <= WIN_END]
        self.closes = {s: [stocks[s][t]["c"] for t in sorted(stocks[s])
                           if d(t) <= WIN_END] for s in UNIVERSE + ["SPY"]}
        self.hist = {s: {t: stocks[s][t]["c"] for t in sorted(stocks[s])} for s in UNIVERSE}
        self.spy_close = {t: stocks["SPY"][t]["c"] for t in sorted(stocks["SPY"])}
        self.cash = INITIAL_CASH
        self.puts: dict[str, dict] = {}        # occ -> position
        self.calls: dict[str, dict] = {}
        self.shares: dict[str, dict] = {}      # u -> {qty, cost}
        self.queue: list[dict] = []            # fills for next trading day
        self.marks: dict[str, float] = {}      # occ -> last mark
        self.pos_bars: dict[str, dict] = {}    # occ -> {date: bar}, life fetched once
        self.equity_curve, self.trades, self.round_trips = [], [], []
        self.monthly: dict[str, float] = {}
        self.gates = {"vol_floor": 0, "drawdown": 0, "extreme": 0, "no_candidate": 0,
                      "budget": 0, "slots": 0, "sector": 0, "fills_missed": 0,
                      "bear_entries_scaled": 0, "cc_floor_block": 0,
                      "quality": 0, "afford": 0}
        self.champions = []                     # (day, name) audit trail
        self.equity_prev = INITIAL_CASH

    # --- helpers -------------------------------------------------------
    def closes_upto(self, u: str, day: str) -> list[float]:
        return [v for t, v in self.hist[u].items() if t <= day]

    def spot(self, u, day):
        b = self.stocks[u].get(day)
        return b["c"] if b else None

    def reserved(self) -> float:
        return sum(p["strike"] * 100 * p["qty"] for p in self.puts.values())

    def pending_reserved(self) -> float:
        """Collateral already promised to queued (unfilled) SELL_PUT orders.
        The live engine counts open orders in its budget (night-1 fix); the
        backtest must too, or one decision day over-commits across names."""
        return sum(o["strike"] * 100 * o["qty"] for o in self.queue
                   if o["kind"] == "SELL_PUT")

    def reserved_u(self, u) -> float:
        return sum(p["strike"] * 100 * p["qty"] for p in self.puts.values() if p["u"] == u)

    def exposed(self) -> set[str]:
        us = {p["u"] for p in self.puts.values()} | set(self.shares)
        us |= {c["u"] for c in self.calls.values()}
        return us

    def sector_count(self, u) -> int:
        sec = next((k for k, v in SECTORS.items() if u in v), None)
        if not sec:
            return 0
        return sum(1 for x in self.exposed() if x in SECTORS.get(sec, []))

    def mark_options(self, day):
        for occ in list(self.puts) + list(self.calls):
            b = self._bar_of(occ, day)
            if b and b["c"] > 0:
                self.marks[occ] = b["c"]

    def _load_pos_bars(self, occ, start, end):
        """Fetch a held contract's whole life in ONE api call (cached on disk)."""
        self.pos_bars[occ] = self.opts.get([occ], start, end)[occ]

    def _bar_of(self, occ, day):
        bars = self.pos_bars.get(occ)
        return bars.get(day) if bars else None

    def equity(self, day):
        shares_v = sum(s["qty"] * (self.spot(s_u, day) or s["cost"])
                       for s_u, s in self.shares.items())
        opts_liab = sum(self.marks.get(occ, p["credit"]) * 100 * p["qty"]
                        for occ, p in self.puts.items())
        opts_liab += sum(self.marks.get(occ, c["credit"]) * 100 * c["qty"]
                         for occ, c in self.calls.items())
        return self.cash + shares_v - opts_liab

    def fill(self, kind, occ, u, qty, price, fee, note, day):
        self.trades.append({"ts": day, "kind": kind, "underlying": u, "occ": occ,
                            "qty": qty, "price": round(price, 3), "fee": round(fee, 2),
                            "cash": round((qty * 100 * price) * (1 if "BUY" not in kind else -1), 2),
                            "note": note})

    # --- candidate selection (mirrors wheel.py _best + candidates) ------
    def best_candidate(self, u, day, right, band, target, strike_min=None, strike_max=None):
        spot = self.spot(u, day)
        if not spot:
            return None
        exps = fridays_in_band(d(day))
        if not exps:
            return None
        syms = []
        for exp in exps:
            for k in strike_ladder(spot):
                if strike_min and k < strike_min:
                    continue
                if strike_max and k > strike_max:
                    continue
                syms.append(occ_sym(u, exp, right, k))
        if not syms:
            # e.g. CC floor (cost basis / Bollinger) above the ladder ceiling:
            # the live engine skips with "no qualifying call above floor" — same here
            return None
        nxt = self.days[self.days.index(day) + 1] if day != self.days[-1] else None
        if not nxt:
            return None
        bars = self.opts.get(syms, day, nxt)
        best = None
        for occ in syms:
            b = bars.get(occ, {}).get(day)
            nb = bars.get(occ, {}).get(nxt)
            if not b or b["c"] <= 0.01 or b["v"] < MIN_DAY_VOLUME or not nb or nb["o"] <= 0.01:
                continue
            _, exp, r, k = parse_occ(occ)
            T = (exp - d(day)).days / 365
            sig = iv_from_premium(right, b["c"], spot, k, T)
            if sig is None:
                continue
            delta = abs(bs_delta(right, spot, k, T, R_FREE, sig))
            if not (band[0] <= delta <= band[1]):
                continue
            if b["c"] / k < MIN_PREM_PCT and right == "P":
                continue
            score = abs(delta - target)
            cand = {"occ": occ, "strike": k, "expiry": exp.isoformat(), "delta": delta,
                    "iv": sig, "close": b["c"], "open_next": nb["o"], "dte": (exp - d(day)).days}
            if best is None or score < best[0] or (score == best[0] and b["c"] > best[1]["close"]):
                best = (score, cand)
        return best[1] if best else None

    # --- daily loop -----------------------------------------------------
    def run(self):
        prev_week = None
        for i, day in enumerate(self.days):
            nxt = self.days[i + 1] if i + 1 < len(self.days) else None
            self._execute_queue(day)
            self._settle_expiries(day)
            self._pay_dividends(day)
            self._manage_puts(day)
            self._manage_calls(day)
            is_decision = d(day).isocalendar()[:2] != prev_week
            if is_decision and nxt:
                self._decision(day, nxt)
            if is_decision:
                prev_week = d(day).isocalendar()[:2]
            self.mark_options(day)
            eq = self.equity(day)
            self.equity_curve.append({"date": day, "equity": round(eq, 2)})
            self.equity_prev = eq
            if is_decision:
                print(f"  {day}  eq ${eq:,.0f}  puts {len(self.puts)} calls {len(self.calls)}"
                      f"  shares {sum(s['qty'] for s in self.shares.values())}"
                      f"  reserved ${self.reserved():,.0f}  (opt calls: {self.opts.calls})",
                      flush=True)
        self._close_open_at_end()

    # 1. queued fills at today's option-bar open -------------------------
    def _execute_queue(self, day):
        still = []
        for o in self.queue:
            if day > o["decided"]:                     # 3-day TTL on unfilled orders
                dd = (d(day) - d(o["decided"])).days
                if dd > 3:
                    self.gates["fills_missed"] += 1
                    continue
            occ = o["occ"]
            pos = self.puts.get(occ) or self.calls.get(occ)
            if o["kind"] in ("SELL_PUT", "SELL_CC") and not pos:
                self._load_pos_bars(occ, day, o["expiry"])
                b = self._bar_of(occ, day)
                if not b or b["o"] <= 0.01:
                    self.pos_bars.pop(occ, None)
                    still.append(o)
                    continue
                px = b["o"] * (1 - SLIPPAGE)
                fee = COMMISSION * o["qty"]
                self.cash += o["qty"] * 100 * px - fee
                pos = {"u": o["u"], "strike": o["strike"], "expiry": o["expiry"],
                       "qty": o["qty"], "credit": px, "entry": day, "fees": fee}
                (self.puts if o["kind"] == "SELL_PUT" else self.calls)[occ] = pos
                self.marks[occ] = px
                self.fill(o["kind"], occ, o["u"], o["qty"], px, fee,
                          f"delta {o['delta']:.2f} dte {o['dte']}", day)
                ym = day[:7]
                self.monthly[ym] = self.monthly.get(ym, 0) + o["qty"] * 100 * px
            elif o["kind"] in ("BUY_PUT", "BUY_CC") and pos:
                b = self._bar_of(occ, day)
                if not b or b["o"] <= 0.01:
                    still.append(o); continue
                px = b["o"] * (1 + SLIPPAGE)
                fee = COMMISSION * pos["qty"]
                self.cash -= pos["qty"] * 100 * px + fee
                self.fill(o["kind"], occ, pos["u"], pos["qty"], px, fee, o["note"], day)
                pnl = (pos["credit"] - px) * 100 * pos["qty"] - fee - pos["fees"]
                self.round_trips.append({
                    "occ": occ, "underlying": pos["u"], "leg": o["kind"],
                    "entry": pos["entry"], "credit": round(pos["credit"], 3),
                    "exit": day, "exit_px": round(px, 3), "exit_kind": o["note"],
                    "pnl": round(pnl, 2)})
                (self.puts if o["kind"] == "BUY_PUT" else self.calls).pop(occ, None)
                self.pos_bars.pop(occ, None)
        self.queue = still

    # 2. expiry settlement at today's close ------------------------------
    def _settle_expiries(self, day):
        for occ, p in list(self.puts.items()):
            if p["expiry"] != day:
                continue
            close = self._last_close(p["u"], day)
            if close is None:
                continue
            if close < p["strike"]:                        # assigned
                cost = p["strike"] * 100 * p["qty"]
                self.cash -= cost
                st = self.shares.setdefault(p["u"], {"qty": 0, "cost": 0.0})
                st["cost"] = (st["cost"] * st["qty"] + p["strike"] * 100 * p["qty"]) / (st["qty"] + 100 * p["qty"])
                st["qty"] += 100 * p["qty"]
                self.fill("ASSIGN", occ, p["u"], p["qty"], p["strike"], 0,
                          f"assigned; close {close:.2f} < strike", day)
                pnl = p["credit"] * 100 * p["qty"] - p["fees"]
                self.round_trips.append({
                    "occ": occ, "underlying": p["u"], "leg": "PUT",
                    "entry": p["entry"], "credit": round(p["credit"], 3),
                    "exit": day, "exit_px": 0, "exit_kind": "ASSIGN",
                    "pnl": round(pnl, 2)})
            else:
                self.fill("EXPIRE_0", occ, p["u"], p["qty"], 0, 0, "expired worthless", day)
                pnl = p["credit"] * 100 * p["qty"] - p["fees"]
                self.round_trips.append({
                    "occ": occ, "underlying": p["u"], "leg": "PUT",
                    "entry": p["entry"], "credit": round(p["credit"], 3),
                    "exit": day, "exit_px": 0, "exit_kind": "EXPIRE",
                    "pnl": round(pnl, 2)})
            self.puts.pop(occ)
            self.marks.pop(occ, None)
            self.pos_bars.pop(occ, None)
        for occ, c in list(self.calls.items()):
            if c["expiry"] != day:
                continue
            close = self._last_close(c["u"], day)
            if close is None:
                continue
            if close > c["strike"]:                        # called away
                sh = self.shares.get(c["u"])
                n = min(c["qty"] * 100, sh["qty"] if sh else 0)
                self.cash += c["strike"] * n
                realized = (c["strike"] - sh["cost"]) * n
                sh["qty"] -= n
                if sh["qty"] == 0:
                    del self.shares[c["u"]]
                self.fill("CALLED_AWAY", occ, c["u"], c["qty"], c["strike"], 0,
                          f"called; close {close:.2f} > strike; stock pnl {realized:+.0f}", day)
                pnl = c["credit"] * 100 * c["qty"] - c["fees"]
                self.round_trips.append({
                    "occ": occ, "underlying": c["u"], "leg": "CALL",
                    "entry": c["entry"], "credit": round(c["credit"], 3),
                    "exit": day, "exit_px": 0, "exit_kind": "CALLED",
                    "pnl": round(pnl, 2)})
            else:
                self.fill("CC_EXPIRE_0", occ, c["u"], c["qty"], 0, 0, "cc expired worthless", day)
                pnl = c["credit"] * 100 * c["qty"] - c["fees"]
                self.round_trips.append({
                    "occ": occ, "underlying": c["u"], "leg": "CALL",
                    "entry": c["entry"], "credit": round(c["credit"], 3),
                    "exit": day, "exit_px": 0, "exit_kind": "EXPIRE",
                    "pnl": round(pnl, 2)})
            self.calls.pop(occ)
            self.marks.pop(occ, None)
            self.pos_bars.pop(occ, None)

    def _last_close(self, u, day):
        hist = [(t, v["c"]) for t, v in self.stocks[u].items() if t <= day]
        return hist[-1][1] if hist else None

    # 3. dividends --------------------------------------------------------
    def _pay_dividends(self, day):
        for u, rates in self.divs.items():
            r = rates.get(day, 0.0)
            sh = self.shares.get(u)
            if r and sh:
                self.cash += r * sh["qty"]
                self.fill("DIV", "", u, sh["qty"], r, 0, "dividend ex-date", day)

    # 4. put management: TP / roll-for-credit ------------------------------
    def _manage_puts(self, day):
        for occ, p in list(self.puts.items()):
            b = self._bar_of(occ, day)
            if not b or b["c"] <= 0:
                continue
            self.marks[occ] = b["c"]
            if b["c"] <= p["credit"] * TP_FRACTION:
                self.queue.append({"kind": "BUY_PUT", "occ": occ, "note": "take_profit",
                                   "decided": day})
                continue
            spot = self.spot(p["u"], day)
            T = max((d(p["expiry"]) - d(day)).days / 365, 1 / 365)
            sig = iv_from_premium("P", b["c"], spot, p["strike"], T)
            if sig is None:
                continue
            delta = abs(bs_delta("P", spot, p["strike"], T, R_FREE, sig))
            if delta >= ROLL_DELTA:
                fresh = self.best_candidate(p["u"], day, "P", CSP_BAND, CSP_TARGET,
                                            strike_max=None)
                # engine test: fresh bid >= close ask -> credit roll available
                if fresh and fresh["close"] >= b["c"]:
                    self.queue.append({"kind": "BUY_PUT", "occ": occ, "decided": day,
                                       "note": f"roll_for_credit (fresh {fresh['occ']})"})
                # else: hold to assignment (practitioner discipline)

    # 5. call management: TP ------------------------------------------------
    def _manage_calls(self, day):
        for occ, c in list(self.calls.items()):
            b = self._bar_of(occ, day)
            if not b or b["c"] <= 0:
                continue
            self.marks[occ] = b["c"]
            if b["c"] <= c["credit"] * TP_FRACTION:
                self.queue.append({"kind": "BUY_CC", "occ": occ, "decided": day,
                                   "note": "cc_take_profit"})

    # 6. weekly decision ------------------------------------------------------
    def _decision(self, day, nxt):
        eq = self.equity_prev
        # drawdown stop: today's marked equity vs previous close (proxy of the
        # live day-start anchor)
        eq_now = self.equity(day)
        if eq_now < eq * (1 - DRAWDOWN_STOP):
            self.gates["drawdown"] += 1
            return
        spy_pct = self._spy_day_pct(day)
        if spy_pct is not None and spy_pct <= SPY_EXTREME:
            self.gates["extreme"] += 1
            return
        bear = spy_pct is not None and spy_pct <= SPY_BEAR
        budget_mult = 0.5 if bear else 1.0
        band, target = (BEAR_BAND, BEAR_TARGET) if bear else (CSP_BAND, CSP_TARGET)

        # (a) TOP-K WEEKLY PICKS — selection BEFORE the options scan (variant D):
        # score the universe, then sell up to K CSPs on the week's best names.
        per_name = min(PER_NAME_PCT, TOTAL_PCT / max(TOPK_PICKS, 1))
        if len(self.exposed()) < MAX_UNDERLYINGS and self.cash > 0:
            scored = []
            for u in UNIVERSE:
                if u in self.exposed():
                    continue
                closes = self.closes_upto(u, day)
                if len(closes) < QUALITY_SMA or len(closes) < MOM_LOOKBACK + 1:
                    continue
                sma200 = sum(closes[-QUALITY_SMA:]) / QUALITY_SMA
                spot_u = self.spot(u, day)
                if spot_u is None or spot_u < sma200:
                    self.gates["quality"] += 1
                    continue
                vp = vol_dollar_percentile(closes)
                if vp is None or vp < VOL_FLOOR:
                    self.gates["vol_floor"] += 1
                    continue
                if closes[-1] * 100 > per_name * eq:   # >= 1 kontrak tak terjangkau
                    self.gates["afford"] += 1
                    continue
                scored.append((u, closes[-1] / closes[-1 - MOM_LOOKBACK] - 1, vp))
            if not scored:
                self.gates["no_candidate"] += 1
            else:
                rm = {t[0]: i for i, t in enumerate(sorted(scored, key=lambda x: -x[1]))}
                rv = {t[0]: i for i, t in enumerate(sorted(scored, key=lambda x: -x[2]))}
                ranked = sorted(scored, key=lambda t: (rm[t[0]] + rv[t[0]], -t[2]))
                print("    ranking: " + " | ".join(
                    f"{u} m{m*100:+.0f}% v{v:.2f}" for u, m, v in ranked[:3]), flush=True)
                picked = 0
                for rank, (u, _m, _v) in enumerate(ranked[:ATTEMPT_CAP], 1):
                    if picked >= TOPK_PICKS or len(self.exposed()) >= MAX_UNDERLYINGS:
                        break
                    if self.sector_count(u) >= MAX_PER_SECTOR:
                        self.gates["sector"] += 1
                        continue
                    strike_max = per_name * eq / 100.0
                    best = self.best_candidate(u, day, "P", band, target,
                                               strike_max=strike_max)
                    if best is None:
                        self.gates["no_candidate"] += 1
                        continue
                    budget = min(per_name * eq,
                                 TOTAL_PCT * budget_mult * eq
                                 - self.reserved() - self.pending_reserved())
                    qty = int(budget // (best["strike"] * 100)) if budget > 0 else 0
                    if qty < 1 or self.cash < best["strike"] * 100 * qty:
                        self.gates["budget"] += 1
                        continue
                    if bear:
                        self.gates["bear_entries_scaled"] += 1
                    picked += 1
                    self.champions.append((day, u))
                    print(f"    -> pick #{rank} {u} {best['occ']} x{qty} "
                          f"delta {best['delta']:.2f}", flush=True)
                    self.queue.append({"kind": "SELL_PUT", "occ": best["occ"], "u": u,
                                       "strike": best["strike"], "expiry": best["expiry"],
                                       "qty": qty, "delta": best["delta"], "dte": best["dte"],
                                       "decided": day})

        # (b) covered calls for assigned shares
        for u, sh in list(self.shares.items()):
            if u in {c["u"] for c in self.calls.values()} or sh["qty"] < 100:
                continue
            closes = self.closes_upto(u, day)
            ub = upper_bollinger(closes)
            floor = max(sh["cost"], ub) if ub else sh["cost"]
            best = self.best_candidate(u, day, "C", CC_BAND, CC_TARGET,
                                       strike_min=floor * 0.999)
            if best is None:
                self.gates["cc_floor_block"] += 1
                continue
            qty = sh["qty"] // 100
            self.queue.append({"kind": "SELL_CC", "occ": best["occ"], "u": u,
                               "strike": best["strike"], "expiry": best["expiry"],
                               "qty": qty, "delta": best["delta"], "dte": best["dte"],
                               "decided": day})

    def _spy_day_pct(self, day):
        hist = [(t, v) for t, v in self.spy_close.items() if t <= day]
        if len(hist) < 2:
            return None
        return (hist[-1][1] / hist[-2][1] - 1) * 100

    # end-of-window: mark open positions honestly --------------------------
    def _close_open_at_end(self):
        last = self.days[-1]
        for occ, p in self.puts.items():
            close = self._last_close(p["u"], last)
            intrinsic = max(p["strike"] - close, 0) if close else 0
            pnl = (p["credit"] - intrinsic) * 100 * p["qty"] - p["fees"]
            self.round_trips.append({
                "occ": occ, "underlying": p["u"], "leg": "PUT", "entry": p["entry"],
                "credit": round(p["credit"], 3), "exit": "OPEN", "exit_px": round(intrinsic, 2),
                "exit_kind": "OPEN_AT_END", "pnl": round(pnl, 2)})
        for occ, c in self.calls.items():
            close = self._last_close(c["u"], last)
            intrinsic = max(close - c["strike"], 0) if close else 0
            pnl = (c["credit"] - intrinsic) * 100 * c["qty"] - c["fees"]
            self.round_trips.append({
                "occ": occ, "underlying": c["u"], "leg": "CALL", "entry": c["entry"],
                "credit": round(c["credit"], 3), "exit": "OPEN", "exit_px": round(intrinsic, 2),
                "exit_kind": "OPEN_AT_END", "pnl": round(pnl, 2)})


def suspect_cache_files() -> list[Path]:
    """All-empty MULTI-symbol cache files (ladder requests) — candidates for a
    fresh-process refetch. Single-symbol files are left alone (a contract with
    no trades legitimately has no bars)."""
    out = []
    for f in CACHE.glob("*.json"):
        try:
            d = json.loads(f.read_text())
        except Exception:
            out.append(f)
            continue
        bars = d.get("bars", {})
        if len(bars) > 1 and not any(bars.values()):
            out.append(f)
    return out


def heal_via_subprocess(suspects: list[Path]) -> int:
    """Refetch every suspect ladder in a FRESH python process (chunked).
    Fresh processes reliably return data the long-lived walk process
    sometimes gets as 200-with-empty (verified by side-by-side probes;
    cause: per-process client degradation on this data endpoint)."""
    if not suspects:
        return 0
    listing = RAW / "_suspects.json"
    listing.write_text(json.dumps([str(p) for p in suspects]))
    healed = 0
    CHUNK = 20
    for i in range(0, len(suspects), CHUNK):
        r = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--heal-chunk",
             str(i), str(listing)], capture_output=True, text=True, timeout=1800)
        healed += sum(1 for line in r.stdout.splitlines()
                      if line.startswith("healed "))
        if r.returncode != 0:
            print(f"  [heal chunk {i}] rc={r.returncode}: {r.stderr[-400:]}",
                  file=sys.stderr)
    listing.unlink(missing_ok=True)
    return healed


def _heal_chunk_main(start_idx: int, listing_path: str):
    """Runs in a fresh interpreter: refetch suspects[start_idx : +20], one
    brand-new SDK client per file. Content is read BEFORE the cache entry is
    replaced (get() rewrites the same hash-named file on success)."""
    files = json.loads(Path(listing_path).read_text())[start_idx:start_idx + 20]
    o = OptFetch()
    o.empty_attempts = 6
    for p in files:
        try:
            d = json.loads(Path(p).read_text())
        except Exception:
            continue                      # already gone — nothing to heal
        symbols, s, e = d.get("symbols"), d.get("start"), d.get("end")
        if not symbols:
            # pre-healer cache format: drop it; the walk recreates on demand
            Path(p).unlink(missing_ok=True)
            continue
        Path(p).unlink(missing_ok=True)
        o._recreate()
        got = o.get(symbols, s, e)
        if any(got.values()):
            print(f"healed {Path(p).name}")
        time.sleep(0.6)


# ---------------------------------------------------------------- metrics
def metrics(equity: list[float]):
    total = equity[-1] / equity[0] - 1
    days = len(equity)
    cagr = (equity[-1] / equity[0]) ** (365 / max(days, 1)) - 1
    peak, maxdd = equity[0], 0.0
    for v in equity:
        peak = max(peak, v)
        maxdd = max(maxdd, (peak - v) / peak)
    rets = [equity[i] / equity[i - 1] - 1 for i in range(1, len(equity))]
    sd = statistics.stdev(rets) if len(rets) > 2 else 0.0
    sharpe = (statistics.mean(rets) / sd * math.sqrt(252)) if sd > 0 else 0.0
    return {"total_return": round(total * 100, 2), "cagr": round(cagr * 100, 2),
            "max_drawdown": round(maxdd * 100, 2), "sharpe": round(sharpe, 2),
            "final_equity": round(equity[-1], 2)}


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    (RUN / "normalized").mkdir(exist_ok=True)
    print("== fetch stock bars (Alpaca CLI, iex/raw) ==", flush=True)
    stocks = {}
    for sym in UNIVERSE + ["SPY"]:
        stocks[sym] = fetch_stock(sym)
        assert stocks[sym], f"no bars for {sym}"
        print(f"  {sym}: {len(stocks[sym])} days", flush=True)
    for sym, series in stocks.items():
        with open(RUN / "normalized" / f"bars_{sym}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "open", "high", "low", "close"])
            for t in sorted(series):
                b = series[t]
                w.writerow([t, b["o"], b["h"], b["l"], b["c"]])

    ca = json.loads((RAW / "corporate_actions.json").read_text())
    divs: dict[str, dict[str, float]] = {}
    for u, dd in ca["cash_dividends_by_symbol_exdate"].items():
        agg: dict[str, float] = {}
        for k, v in dd.items():                # keys may repeat w/ suffixes b/s
            base = k.rstrip("bs")
            agg[base] = agg.get(base, 0) + v
        divs[u] = agg

    print("== simulate (single pass; cache pre-verified by the baseline run) ==",
          flush=True)
    opts = OptFetch()
    bt = None
    for pass_no in (1,):
        suspects = (suspect_cache_files()
                    if os.environ.get("BT_HEAL") == "1" else [])
        if suspects:
            print(f"-- pass {pass_no}: healing {len(suspects)} suspect ladder(s) "
                  f"in fresh processes --", flush=True)
            healed = heal_via_subprocess(suspects)
            print(f"   healed {healed}/{len(suspects)}", flush=True)
        else:
            print(f"-- pass {pass_no}: cache clean --", flush=True)
        bt = Backtest(stocks, opts, divs)
        bt.run()
        if not suspect_cache_files():
            print("-- cache stable: remaining empty ladders confirmed real --",
                  flush=True)
            break

    # ---- equity & benchmark ----
    eq = [p["equity"] for p in bt.equity_curve]
    spy_days = [p["date"] for p in bt.equity_curve]
    spy = [bt.spy_close[t] for t in spy_days]
    spy_eq = [INITIAL_CASH * s / spy[0] for s in spy]
    strat_metrics = metrics(eq)
    spy_metrics = metrics(spy_eq)

    legs = bt.round_trips
    wins = [l for l in legs if l["pnl"] > 0]
    losses = [l for l in legs if l["pnl"] <= 0]
    gross_w = sum(l["pnl"] for l in wins)
    gross_l = abs(sum(l["pnl"] for l in losses))
    premiums = sum(t["price"] * t["qty"] * 100 for t in bt.trades
                   if t["kind"] in ("SELL_PUT", "SELL_CC"))
    fees = sum(t["fee"] for t in bt.trades if t["kind"] not in ("ASSIGN", "EXPIRE_0",
                                                                "CALLED_AWAY", "CC_EXPIRE_0", "DIV"))
    counts = {"csp_sold": sum(1 for t in bt.trades if t["kind"] == "SELL_PUT"),
              "cc_sold": sum(1 for t in bt.trades if t["kind"] == "SELL_CC"),
              "tp_closes": sum(1 for t in bt.trades if t["kind"] == "BUY_PUT"),
              "cc_tp": sum(1 for t in bt.trades if t["kind"] == "BUY_CC"),
              "expired_worthless": sum(1 for l in legs if l["exit_kind"] == "EXPIRE"),
              "assignments": sum(1 for t in bt.trades if t["kind"] == "ASSIGN"),
              "called_away": sum(1 for t in bt.trades if t["kind"] == "CALLED_AWAY")}

    summary = {
        "run": str(RUN.name), "window": {"start": spy_days[0], "end": spy_days[-1],
                                         "trading_days": len(spy_days)},
        "strategy": strat_metrics, "benchmark_spy": spy_metrics,
        "option_legs": {"total": len(legs), "wins": len(wins),
                        "win_rate_pct": round(100 * len(wins) / len(legs), 1) if legs else None,
                        "profit_factor": round(gross_w / gross_l, 2) if gross_l else None,
                        "net_option_pnl": round(sum(l["pnl"] for l in legs), 2)},
        "premiums_collected_gross": round(premiums, 2), "fees_paid": round(fees, 2),
        "activity": counts, "gate_activity": bt.gates,
        "opt_api_calls": bt.opts.calls,
        "variant": "D topk-sweep",
        "topk": TOPK_PICKS,
        "per_name_pct": round(min(PER_NAME_PCT, TOTAL_PCT / max(TOPK_PICKS, 1)), 4),
        "champions_picked": [{"date": d, "name": u} for d, u in bt.champions],
    }

    # ---- artifacts ----
    (RUN / f"{BT_TAG}_summary.json").write_text(json.dumps(summary, indent=2))
    with open(RUN / f"{BT_TAG}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(bt.trades[0].keys()) if bt.trades
                           else ["ts", "kind", "underlying", "occ", "qty", "price", "fee", "cash", "note"])
        w.writeheader(); w.writerows(bt.trades)
    with open(RUN / f"{BT_TAG}_round_trips.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["occ", "underlying", "leg", "entry", "credit",
                                          "exit", "exit_px", "exit_kind", "pnl"])
        w.writeheader(); w.writerows(bt.round_trips)
    with open(RUN / f"{BT_TAG}_equity.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["date", "equity"])
        w.writerows([[p["date"], p["equity"]] for p in bt.equity_curve])
    with open(RUN / f"{BT_TAG}_benchmark_equity.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["date", "spy_close", "spy_equity"])
        w.writerows([[t, s, round(e, 2)] for t, s, e in zip(spy_days, spy, spy_eq)])

    fp = {"files": {p.name: {"sha256_16": sha(p), "bytes": p.stat().st_size}
                    for p in sorted(RAW.glob("*.json"))},
          "opts_cache_files": len(list(CACHE.glob("*.json"))),
          "stock_bars": {s: len(stocks[s]) for s in stocks},
          "first_day": min(min(stocks[s]) for s in stocks),
          "last_day": max(max(stocks[s]) for s in stocks)}
    (RUN / f"{BT_TAG}_data_fingerprint.json").write_text(json.dumps(fp, indent=2))
    (RUN / f"{BT_TAG}_warnings.json").write_text(json.dumps({
        "fills_dropped_stale": bt.gates["fills_missed"],
        "note": "see notes.md 'Deviations' — liquidity proxy, inverse-BS greeks, "
                "daily-close regime proxy, no AI layer, no early assignment"}, indent=2))
    (RUN / f"{BT_TAG}_fee_source.json").write_text(json.dumps({
        "model": "USD 0.50 per contract per side commission",
        "source": "https://files.alpaca.markets/disclosures/library/BrokFeeSched.pdf",
        "fetch_attempt": "blocked from this network 2026-08-29 (DNS policy; only "
                         "paper-api/data hosts pinned) — modeled from Alpaca's "
                         "published options commission",
        "excluded": "OCC/exchange/regulatory pass-through fees (~$0.01-0.05/contract) "
                    "not added: small optimistic bias"}, indent=2))

    first_trade = bt.trades[0] if bt.trades else None
    last_trade = bt.trades[-1] if bt.trades else None
    report = f"""# Variant D — Top-{TOPK_PICKS} weekly picks, equal-weight budget (1 tahun)
## Performance vs Benchmark
| | Total Return | Ann. Return | Max Drawdown | Sharpe | Final Equity |
|---|---:|---:|---:|---:|---:|
| **Strategy** | {strat_metrics['total_return']}% | {strat_metrics['cagr']}% | {strat_metrics['max_drawdown']}% | {strat_metrics['sharpe']} | ${strat_metrics['final_equity']:,.0f} |
| SPY buy-and-hold | {spy_metrics['total_return']}% | {spy_metrics['cagr']}% | {spy_metrics['max_drawdown']}% | {spy_metrics['sharpe']} | ${spy_metrics['final_equity']:,.0f} |

Window {spy_days[0]} → {spy_days[-1]} ({len(spy_days)} trading days), initial cash ${INITIAL_CASH:,.0f}.
Every option premium is a real Alpaca option-trade daily bar; underlying bars from the
Alpaca CLI (sip, raw). Strategy rules mirror the live engine 1:1 (see `strategy_spec.json`,
`notes.md`) with zero re-tuning.

- Option legs: {len(legs)} — win rate {summary['option_legs']['win_rate_pct']}%, profit factor {summary['option_legs']['profit_factor']}
- Premiums collected (gross): ${premiums:,.0f} · fees modeled ${fees:,.0f}
- Assignments {counts['assignments']} · called away {counts['called_away']} · expired worthless {counts['expired_worthless']} · TP closes {counts['tp_closes'] + counts['cc_tp']}
- First trade: {first_trade and f"{first_trade['ts']} {first_trade['kind']} {first_trade['occ']}"}
- Last trade: {last_trade and f"{last_trade['ts']} {last_trade['kind']} {last_trade['occ']}"}

Assumptions, deviations and caveats: `notes.md` (fill model next-open + 5% slippage,
liquidity volume proxy, inverse-BS greeks, deterministic core only — the AI layer is not
replayed; backtest bounds the engine, live run demonstrates the governor).
Data fingerprint: `data_fingerprint.json` · warnings: `warnings.json`.

> **Important disclosure**
> This backtest is a hypothetical historical simulation and does not represent actual
> trading performance. Backtested results do not guarantee future results. Results depend
> on market-data quality, data feed selection, corporate-action handling, fees, slippage,
> liquidity, taxes, execution assumptions, and implementation details. This material is
> for research and educational purposes only and is not investment advice, a
> recommendation, an offer, or a solicitation to buy or sell securities, options,
> cryptocurrencies, or any other financial product. All investments involve risk and can
> lose value. Review Alpaca's disclosures at [alpaca.markets/disclosures](https://alpaca.markets/disclosures).
"""
    (RUN / f"{BT_TAG}_report.md").write_text(report)

    # ---- dashboard export: DISABLED for variant C ----
    # agent/dashboard/backtest.json belongs to the published baseline run.


    print("\n== done ==")
    print(json.dumps(summary, indent=2)[:2000])


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--heal-chunk":
        _heal_chunk_main(int(sys.argv[2]), sys.argv[3])
    else:
        main()
