# Variant B report — quality screen + regime delta + cash yield
## Performance vs Benchmark
| | Total Return | Ann. Return | Max Drawdown | Sharpe | Final Equity |
|---|---:|---:|---:|---:|---:|
| **Strategy** | 34.21% | 19.39% | 12.85% | 0.87 | $134,236 |
| SPY buy-and-hold | 45.59% | 25.39% | 18.98% | 1.08 | $145,593 |

Window 2024-03-01 → 2026-07-31 (606 trading days), initial cash $100,000.
Variant levers: SMA200 quality screen · regime delta (RISK_ON 0.4 / NEUTRAL 0.3 / RISK_OFF 0.2) · CC band 1.5σ in RISK_ON · cash 4% APR (accrued $5,878).

## Walk-forward — parameters pre-committed before OOS; split after 2025-06-30
| Segment | Strategy | SPY buy-hold |
|---|---|---|
| IS  | 14.8% · DD 12.85% · Sharpe 0.72 | 20.45% · DD 18.98% · Sharpe 0.88 |
| OOS | 16.92% · DD 12.23% · Sharpe 1.09 | 20.87% · DD 9.13% · Sharpe 1.47 |
Every option premium is a real Alpaca option-trade daily bar; underlying bars from the
Alpaca CLI (sip, raw). Strategy rules mirror the live engine 1:1 (see `strategy_spec.json`,
`notes.md`) with zero re-tuning.

- Option legs: 148 — win rate 96.6%, profit factor 19.34
- Premiums collected (gross): $58,765 · fees modeled $982
- Assignments 17 · called away 12 · expired worthless 5 · TP closes 113
- First trade: 2024-03-04 SELL_PUT BABA240308P00073000
- Last trade: 2026-07-21 SELL_CC GM260821C00083000

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
