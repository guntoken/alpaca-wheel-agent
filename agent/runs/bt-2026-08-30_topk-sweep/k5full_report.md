# k5full — Top-5 selection-first, window penuh 2,5 tahun (run konfirmasi 1 Sep 2026)

Run lanjutan sweep Top-K untuk mengisi matriks: K=5 di window 2024-03-01 →
2026-07-31 (606 hari trading), identik dengan k3full kecuali `BT_TOPK=5`
(budget per-nama 14,4%, fee/fill/benchmark/opts_cache sama — lineage di
notes.md §"Run lanjutan 1 Sep 2026"). Diputuskan/run SETELAH top-3 dipilih
(30 Agu), jadi berstatus **konfirmasi post-seleksi**, bukan dasar seleksi.

## Performance vs Benchmark

| | Total Return | Ann. Return | Max Drawdown | Sharpe | Final Equity |
|---|---:|---:|---:|---:|---:|
| **Strategy (K=5)** | **+5.0%** | 3.0% | 17.8% | 0.22 | $104,977 |
| SPY buy-and-hold | +45.6% | 25.4% | 18.98% | 1.08 | $145,593 |

134 leg (WR 93,3%, PF 21,4) · premium kotor $26.128 · fee $422 ·
69 CSP / 65 CC / 14 assignment / 9 called away.

## Matriks sweep lengkap (window 2,5 tahun)

| Mode | Return | maxDD | vs SPY +45,6% |
|---|---:|---:|---|
| K=1 champion (champion-25mo) | +35,3% | 27,2% | kalah |
| K=3 (k3full) | **+54,6%** | 21,5% | **menang** |
| **K=5 (k5full, run ini)** | **+5,0%** | 17,8% | **kalah jauh** |
| Baseline live-engine rules | +32,2% | 18,3% | kalah |
| SPY | +45,6% | 19,0% | — |

Interpretasi: kurva konsentrasi — K=3 puncaknya. Menambah nama #4–#5
(momentum ekor + fallback rank 6–8) mengencerkan edge seleksi sampai hampir
habis (+5% dari +54,6%), sementara drawdown tidak turun sebanding (17,8% vs
21,5%). Konsisten dengan hasil 1-tahun K=5 (+1,1% vs SPY +20,1%): bukan
kebetulan window.

## Asumsi penting & deviasi

Sama persis dengan k3full (notes.md "Deviations"): liquidity proxy, inverse-BS
greeks, daily-close regime proxy, tanpa layer AI, tanpa early assignment,
fills dari option-trade bar ASLI Alpaca. Data fingerprint: `k5full_data_fingerprint.json`.

> **Important disclosure**
> This backtest is a hypothetical historical simulation and does not represent
> actual trading performance. Backtested results do not guarantee future
> results. Results depend on market-data quality, data feed selection,
> corporate-action handling, fees, slippage, liquidity, taxes, execution
> assumptions, and implementation details. This material is for research and
> educational purposes only and is not investment advice, a recommendation,
> an offer, or a solicitation to buy or sell securities, options,
> cryptocurrencies, or any financial product. All investments involve risk and
> may lose value. Review Alpaca's disclosures and agreements at
> [alpaca.markets/disclosures](https://alpaca.markets/disclosures).

Fee model: [Alpaca Brokerage Fee Schedule](https://files.alpaca.markets/disclosures/library/BrokFeeSched.pdf)
(revisi & kategori di `k5full_fee_source.json`).
