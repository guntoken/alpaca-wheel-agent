# Backtest report — wheel CSP→CC, real Alpaca option data
## Performance vs Benchmark
| | Total Return | Ann. Return | Max Drawdown | Sharpe | Final Equity |
|---|---:|---:|---:|---:|---:|
| **Strategy** | 32.18% | 18.3% | 18.25% | 0.82 | $132,182 |
| SPY buy-and-hold | 45.59% | 25.39% | 18.98% | 1.08 | $145,593 |

Window 2024-03-01 → 2026-07-31 (606 trading days), initial cash $100,000.
Every option premium is a real Alpaca option-trade daily bar; underlying bars from the
Alpaca CLI (sip, raw). Strategy rules mirror the live engine 1:1 (see `strategy_spec.json`,
`notes.md`) with zero re-tuning.

- Option legs: 175 — win rate 97.1%, profit factor 23.96
- Premiums collected (gross): $45,779 · fees modeled $1,478
- Assignments 20 · called away 15 · expired worthless 5 · TP closes 134
- First trade: 2024-03-04 SELL_PUT BABA240308P00073000
- Last trade: 2026-07-31 BUY_CC T260828C00026000

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
