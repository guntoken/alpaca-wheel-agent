# Variant C report — Weekly Champion Wheel (1 tahun, selection-first)
## Performance vs Benchmark
| | Total Return | Ann. Return | Max Drawdown | Sharpe | Final Equity |
|---|---:|---:|---:|---:|---:|
| **Strategy** | 46.44% | 74.14% | 18.64% | 1.76 | $146,437 |
| SPY buy-and-hold | 20.11% | 30.54% | 9.13% | 1.51 | $120,113 |

Window 2025-08-01 → 2026-07-31 (251 trading days), initial cash $100,000.
Every option premium is a real Alpaca option-trade daily bar; underlying bars from the
Alpaca CLI (sip, raw). Strategy rules mirror the live engine 1:1 (see `strategy_spec.json`,
`notes.md`) with zero re-tuning.

- Option legs: 54 — win rate 98.1%, profit factor 47.24
- Premiums collected (gross): $58,758 · fees modeled $560
- Assignments 10 · called away 7 · expired worthless 1 · TP closes 34
- First trade: 2025-08-04 SELL_PUT SOFI250822P00020000
- Last trade: 2026-07-29 BUY_PUT KO260814P00082000

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
