# Variant D — Top-5 weekly picks, equal-weight budget (1 tahun)
## Performance vs Benchmark
| | Total Return | Ann. Return | Max Drawdown | Sharpe | Final Equity |
|---|---:|---:|---:|---:|---:|
| **Strategy** | 1.15% | 1.67% | 5.71% | 0.18 | $101,146 |
| SPY buy-and-hold | 20.11% | 30.54% | 9.13% | 1.51 | $120,113 |

Window 2025-08-01 → 2026-07-31 (251 trading days), initial cash $100,000.
Every option premium is a real Alpaca option-trade daily bar; underlying bars from the
Alpaca CLI (sip, raw). Strategy rules mirror the live engine 1:1 (see `strategy_spec.json`,
`notes.md`) with zero re-tuning.

- Option legs: 90 — win rate 96.7%, profit factor 24.1
- Premiums collected (gross): $19,304 · fees modeled $373
- Assignments 9 · called away 5 · expired worthless 4 · TP closes 70
- First trade: 2025-08-04 SELL_PUT SOFI250822P00020000
- Last trade: 2026-07-30 BUY_PUT F260821P00013000

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
