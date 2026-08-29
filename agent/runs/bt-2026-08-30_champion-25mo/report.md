# Variant C report — Weekly Champion Wheel (1 tahun, selection-first)
## Performance vs Benchmark
| | Total Return | Ann. Return | Max Drawdown | Sharpe | Final Equity |
|---|---:|---:|---:|---:|---:|
| **Strategy** | 35.34% | 20.0% | 27.15% | 0.6 | $135,342 |
| SPY buy-and-hold | 45.59% | 25.39% | 18.98% | 1.08 | $145,593 |

Window 2024-03-01 → 2026-07-31 (606 trading days), initial cash $100,000.
Every option premium is a real Alpaca option-trade daily bar; underlying bars from the
Alpaca CLI (sip, raw). Strategy rules mirror the live engine 1:1 (see `strategy_spec.json`,
`notes.md`) with zero re-tuning.

- Option legs: 113 — win rate 100.0%, profit factor None
- Premiums collected (gross): $95,387 · fees modeled $907
- Assignments 13 · called away 9 · expired worthless 4 · TP closes 85
- First trade: 2024-03-26 SELL_PUT COIN240419P00255000
- Last trade: 2026-07-28 SELL_CC F260821C00016000

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
