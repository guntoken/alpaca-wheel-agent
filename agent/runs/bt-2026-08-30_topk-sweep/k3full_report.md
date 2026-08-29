# Variant D — Top-3 weekly picks, equal-weight budget (1 tahun)
## Performance vs Benchmark
| | Total Return | Ann. Return | Max Drawdown | Sharpe | Final Equity |
|---|---:|---:|---:|---:|---:|
| **Strategy** | 54.63% | 30.02% | 21.53% | 0.98 | $154,625 |
| SPY buy-and-hold | 45.59% | 25.39% | 18.98% | 1.08 | $145,593 |

Window 2024-03-01 → 2026-07-31 (606 trading days), initial cash $100,000.
Every option premium is a real Alpaca option-trade daily bar; underlying bars from the
Alpaca CLI (sip, raw). Strategy rules mirror the live engine 1:1 (see `strategy_spec.json`,
`notes.md`) with zero re-tuning.

- Option legs: 177 — win rate 97.7%, profit factor 172.14
- Premiums collected (gross): $92,181 · fees modeled $1,056
- Assignments 14 · called away 10 · expired worthless 5 · TP closes 147
- First trade: 2024-03-26 SELL_PUT MU240412P00112000
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
