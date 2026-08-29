# Run notes — wheel CSP→CC backtest on real Alpaca option-trade data

## Original request

Owner (29 Aug 2026): "backtest wajib dibuatkan dulu dengan memakai data real
dari data alpaca" — a backtest of the live agent's actual strategy using real
Alpaca data, to power the dashboard's About/FAQ tabs. Horizon left to the
agent ("berapa tahun backtest nya: silakan anda sebagai AI yang menentukan").

## Why 2.5 years (Mar 2024 – Aug 2026)

Alpaca historical *option* bar coverage on this account begins between Aug
2023 (absent) and Jan 2024 (present) — but January–February 2024 weekly
contracts are patchy (probed 29 Aug 2026: INTC 19-Jan-2024 weekly put ✗, F
19-Jan-2024 weekly put has bars only Thu–Fri), while March 2024 onward is
dense (INTC 15-Mar-2024 weekly put: 283 trades on the Monday). The window
therefore starts 2024-03-01 — every premium in the backtest comes from a real
option trade. The window still contains two major stress events (5 Aug 2024
VIX spike; Apr 2025 tariff drawdown) plus the 2024–25 bull run.

## Strategy (mirror of the live engine, zero re-tuning)

Rules are transcribed 1:1 from `agent/src/agent/wheel.py` + `config.py` —
the same code that trades the paper account. **No parameter was fitted to
this backtest; none was changed after seeing results.**

- Universe (scan order fixed): INTC, T, F, GM, PFE, KO, NOK, SOFI, BABA, MU, WBD, VALE
- New CSP, weekly scan (Mondays; next trading day if holiday), only when flat
  in that name: Δ band 0.18–0.42 (target 0.30; 0.10–0.30, target 0.20 in BEAR),
  DTE 7–35, premium ≥ 0.5% of strike-collateral, day volume ≥ 10 contracts
  (liquidity proxy — see deviations), vol-dollar percentile ≥ 40th of own
  250-day history (Rustamov et al. 2024, inverted), pick candidate nearest
  target delta (exactly `_best()` in wheel.py)
- Sizing: floor(min(18% equity per-name budget, 72%×regime-mult total budget
  − reserved) / (strike×100)), min 1 contract else skip
- Put management daily: take-profit when mark ≤ 50% of credit received;
  roll ONLY for net credit when Δ ≥ 0.60 (fresh target-delta CSP bid ≥ close
  price); otherwise hold to assignment (practitioner discipline)
- Assignment at expiry Friday: stock close < strike → buy 100 shares/contract
  at strike (cash-secured)
- Covered calls when shares ≥ 100: Δ band 0.12–0.38 (target 0.25), strike ≥
  max(cost basis, SMA20+2σ upper Bollinger), DTE 7–35; called away at expiry
  if stock close > strike; re-sell next Monday while shares remain
- CC take-profit when mark ≤ 50% of credit
- Gates: ≤ 5 underlyings exposed, ≤ 2 per correlated sector (sector map from
  config), no new entries (CSP or CC) after −3% daily drawdown vs previous
  close equity (daily-close proxy of the live intraday anchor — see deviations)
- Deterministic SPY regime anchor (daily close-to-close as proxy of the live
  intraday tiers): ≤ −4% → no new entries; ≤ −2% → budget ×0.5, sell further
  OTM (Δ target 0.20)

**The AI layer is NOT replayed.** Claude's regime read and veto are live-only;
a backtest of them would be circular. This run bounds the deterministic core.
Since the AI can only remove risk (veto entries, halve budget), the backtest
is an upper bound on activity, not a claim about the AI's contribution.

## Data

- **Option premiums: real Alpaca option-trade daily bars** (OHLCV per
  contract) via `alpaca-py OptionHistoricalDataClient` — the same API family
  the live engine quotes from. Probed live through the Alpaca MCP server
  before the run. Coverage from Jan 2024.
- **Stock/underlying daily bars: Alpaca CLI** `alpaca data bars --feed iex
  --adjustment raw` (13 symbols + SPY, fetched from 2023-06-01 so the
  250-day vol-percentile and Bollinger indicators have full warmup at the
  first decision). The `iex` feed is the same feed the live engine quotes
  from (`alpaca_client.daily_closes`); the `sip` feed returned intermittent
  403s on this account for long ranges. IEX closes track consolidated closes
  closely but not identically (noted as a data-quality caveat). Raw
  (unadjusted) is used deliberately so stock prices and option strikes live
  in the same coordinate system; verified via the corporate-actions API that
  **no universe symbol split** in the window.
- **Dividends**: Alpaca corporate-actions API (MCP `get_corporate_actions`,
  saved verbatim to `raw/corporate_actions.json`); paid on ex-dates while
  shares are held. Foreign withholding not modeled.
- **Benchmark**: SPY buy-and-hold, same window, same feed, close-to-close.
- CLI note: the CLI (v0.0.13) exposes stock bars only, so option bars come
  from the official SDK — documented deviation from the skill's
  CLI-for-data default; both raw sources are saved under `raw/`.

## Execution model (deliberately conservative)

- Signal at decision-day **close**; fill at **next trading day's option-bar
  open** (`next_open` model — no same-bar fills, no look-ahead)
- Slippage: 5% adverse haircut on the option price per side
  (sell at open×0.95, buy back at open×1.05)
- Commission $0.50/contract per side (Alpaca options fee schedule,
  https://files.alpaca.markets/disclosures/library/BrokFeeSched.pdf —
  PDF not fetchable from this network 29 Aug 2026, DNS-pinned host;
  regulatory/OCC pass-through fees ~$0.01–0.05/contract NOT added, a small
  optimistic bias noted in caveats)
- Assignment/call-away settled against the underlying's close on expiry day
- Δ and IV for selection are computed by inverting Black-Scholes (bisection,
  r = 4%, q = 0) from the **real traded premium** — the live engine uses
  exchange OPRA greeks; backtest deltas are derived, not streamed (deviation)

## Deviations from the live engine (all forced by data availability)

1. Liquidity filter: day trade volume ≥ 10 contracts instead of open
   interest ≥ 200 (historical OI is not served); no bid/ask spread filter
   (historical quotes not served) — mitigated by the 5% slippage haircut.
2. Selection greeks: inverse-BS from traded premiums instead of OPRA greeks.
3. Regime/drawdown anchors: daily close-to-close proxies of the live
   intraday SPY tiers and day-start equity anchor.
4. AI regime/veto layer not replayed (see above).
5. Weekly entry cadence (live loop scans every 5–15 min; TP/roll/CC-expiry
   management is still daily here).
6. Earnings blackout not modeled (live config was empty for the window too).

## Known biases & caveats

- Survivorship: the universe was listed for the whole window (chosen for
   liquidity/size before the backtest ran, not optimized on it — but the
   choice itself was made with hindsight of what stayed liquid).
- Results are hypothetical, fill-model dependent, and exclude early-assignment
  (American puts are often assigned early when deep ITM — the engine's
  delta-0.60 roll gate reduces but does not eliminate this; backtest assumes
  assignment only at expiry, an optimistic bias).
- Penny-priced far-OTM strikes occasionally print one trade at a stale price;
  the volume ≥ 10 filter plus next-day-open fills blunt most of it.

## Artifacts

`run.py` (single-file, deterministic), `strategy_spec.json`, `config.json`,
`raw/` (CLI stock bars + cached SDK option bars + corporate actions),
`normalized/bars_*.csv`, `trades.csv`, `round_trips.csv`, `equity.csv`,
`benchmark_equity.csv`, `summary.json`, `report.md`, `data_fingerprint.json`,
`warnings.json`, `fee_source.json`. Dashboard export:
`agent/dashboard/backtest.json`.
