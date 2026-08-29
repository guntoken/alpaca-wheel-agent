# Wheel Agent — Technical Write-up

One page on how the agent thinks, how it stays safe, and what it is built on.
Live on Alpaca paper since 28 Aug 2026. Facts below are read from the agent's
own decision journal, and — for the deterministic core — from a 2.5-year
backtest on real Alpaca option-trade bars (2024-03 → 2026-07: **+32.2% vs SPY
buy-and-hold +45.6%, max drawdown 18.3% vs 19.0%, Sharpe 0.82 vs 1.08**; rules
mirrored 1:1 from the live engine with zero re-tuning, every premium a real
traded option bar — full artifacts in
`agent/runs/bt-2026-08-29_wheel-csp-cc_1Day/`). The wheel deliberately trades
upside for drawdown control; the AI governor layer is live-only by design.

## 1. The idea: an AI that can only say NO

Retail options income is manual, emotional, and error-prone: traders sell the
wrong delta, panic-buy back challenged puts, and oversize one ticker. The usual
"AI trading agent" answer — let an LLM pick trades — makes this worse: LLMs
hallucinate, drift, and cannot be held to a risk mandate.

We invert the design. A **deterministic engine** does 100% of the trading on
hard-coded rails (the classic wheel: sell cash-secured puts → take profit at
50% or roll for credit → if assigned, sell covered calls → repeat). A **Claude
layer** sits above it as a risk governor with exactly two powers:

1. **Read the regime** — each cycle Claude receives an Alpaca-native market
   summary (SPY/QQQ SMA trend, SPY dollar-volatility percentile, GLD/VIXY/BTC
   moves, filtered news headlines) and classifies the tape RISK_ON / NEUTRAL /
   RISK_OFF with a stated reason.
2. **Veto new entries** — every proposed entry order is shown to Claude; one
   refusal with a reason kills it for the cycle.

The AI can never place, size, or force a trade, and it can never veto an exit
or a buy-back — de-risking is always allowed. The regime also scales the
engine's budget (RISK_ON → 72% of equity as collateral, NEUTRAL → 36%,
RISK_OFF → no new entries). Because an LLM can flicker between cycles, a
**deterministic SPY-intraday anchor** (≤−4% EXTREME / ≤−2% BEAR / else
neutral-bull) runs beside it, and **the tighter of the two always governs**.

In the judged window so far: 39 cycles (25 live), regime read every cycle —
31× RISK_ON, 8× NEUTRAL (those cycles ran at halved budget), 0 vetoes; the
veto path is exercised in dry-runs. Claude's verbatim reasoning is journaled
and shown on the dashboard's *AI Brain* tab.

## 2. Strategy and risk gates (all hard-coded)

Per underlying, the engine sells CSPs at **Δ 0.18–0.42** (target 0.30, widened
to 0.20 in a weak tape), **DTE 7–35**, **OI ≥ 200**, **spread ≤ 15%**,
**vol-percentile ≥ 40th** of the underlying's own dollar-vol history (premium
selling is skipped when options are cheap vs. their own history — adapted from
Rustamov et al. 2024, inverted for short vol). Covered calls only after
assignment, strike ≥ max(cost basis, SMA20+2σ upper Bollinger).

Portfolio rails: ≤ 5 underlyings, ≤ 18% equity per name, ≤ 72% total collateral
(halved in NEUTRAL / BEAR, zero in RISK_OFF / EXTREME), ≤ 2 names per correlated
sector, earnings blackout, −3% daily drawdown stops new entries, marketable
limit orders only, exits always before entries, unfilled entries re-priced after
20 minutes (chase-capped), `agent/KILL` file halts all submissions, paper-only
endpoint hard-coded. Every adoption and rejection is sourced in
[RESEARCH_NOTES.md](RESEARCH_NOTES.md).

## 3. Built agent-native on all three Alpaca surfaces

- **Trading API via alpaca-py** — the engine itself: positions, options chain
  with OPRA greeks, order submission, buying-power clamping.
- **Alpaca CLI** — operations and monitoring (`doctor` before every session,
  account/order inspection alongside the agent's own `status` command).
- **Alpaca MCP server** — connected to the Claude Code session that built and
  supervises the agent, so the same broker surface is available conversationally.

The build itself is agent-native: Claude Code wrote the engine, ran the live
loops, diagnosed its own production bugs from the journal (a py3.10 enum quirk
that blinded position detection; a budget that ignored open orders — both fixed
live on night 1), and authored this document. The decision journal
(`agent/journal.jsonl` → `dashboard/data.json`) is the paper trail: equity
curve, every order with its reason, every regime read, every error.

Night 1 result: 4 fills, **$1,753 net premium collected**, equity $99,699 on a
$100,000 paper account while short 4 puts — with the AI layer, the rails, and
the journal running unattended.

## 4. What this is not

Not investment advice, not a live-money system. It is a hackathon build whose
claim is narrower and, we think, more interesting: **LLMs make better risk
governors than trade pickers**, and an agent that can only refuse is an agent
you can actually trust on a broker.
