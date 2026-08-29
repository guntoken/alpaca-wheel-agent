# Run notes — VARIANT B: quality screen + regime delta + cash yield (walk-forward)

## Status: EXPLORATION, bukan pengganti run terbitan

Baseline terbitan = `bt-2026-08-29_wheel-csp-cc_1Day` (mirror 1:1 live engine, zero
re-tuning, +32,2% vs SPY +45,6%). Varian ini menjawab pertanyaan pemilik 29 Agu 2026:
*"carikan strategy di mana Wheel Agent lebih baik daripada SPY buy-hold"* — dengan
protokol anti-overfit yang ketat. Data, fill model, fee, dan seluruh engine identik
dengan baseline; hanya TIGA lever ditambahkan.

## Tiga lever (pre-committed SEBELUM melihat hasil OOS)

1. **Saringan kualitas SMA200** — CSP baru hanya jika close nama > SMA200-nya sendiri
   (WheelMetrics, "start with the stock… no low-quality high-premium traps"; konsisten
   literatur trend-following). Fase CC pada saham hasil assignment TETAP berjalan
   (assignment tidak bisa ditinggalkan). Motivasi spesifik dari baseline: DD Agu-2024
   18,3% (vs SPY 8,4%) dipicu assignment besar di nama high-IV yang jatuh (mis. SOFI
   22 kontrak).
2. **Delta by trend-regime SPY (daily close, tanpa lookahead)** — RISK_ON (SPY>SMA50
   dan SMA50 menaik vs 20 sesi lalu): band 0,30–0,45 target **0,40** + band CC
   Bollinger **1,5σ** (lebih longgar, kurangi called-away di bull); NEUTRAL: perilaku
   baseline (0,18–0,42 target 0,30; CC 2σ); RISK_OFF (SPY<SMA200): band BEAR
   (0,10–0,30 target 0,20) + budget ×0,5. Pemetaan tier konservatif/moderat/agresif
   WheelMetrics (20-25 / 25-35 / 40+).
3. **Cash yield 4% APR** — bunga harian (252 hari bursa) pada seluruh `cash`
   (termasuk kolateral CSP yang di dunia riil tetap menghasilkan bunga sampai
   assignment). Baseline memodelkan 0%. Tingkat 4% = kira-kira bunga kas bebas risiko
   2024–25.

## Protokol walk-forward

- **IS (in-sample)**: 2024-03-01 → 2025-06-30. **OOS**: 2025-07-01 → 2026-07-31.
- Semua parameter varian dipilih berdasarkan penalaran/literatur dan data IS saja,
  lalu DIKOMIT sebelum simulasi OOS dilihat. TIDAK ada re-tuning setelah melihat OOS —
  hasil OOS apa adanya.
- Keseluruhan window tetap disimulasikan sekali; summary.json memuat metrik
  IS / OOS / full.

## Deviasi tambahan dari baseline

- Simulasi **single-pass** (cache opsi sudah terverifikasi 3-pass oleh run baseline;
  93 ladder kosong terkonfirmasi memang tanpa trade — healing diulang = buang 2 jam).
- `agent/dashboard/backtest.json` TIDAK ditimpa (milik run terbitan).
- Kolom `cash` di trades.csv tetap notional `qty×100×price` (kosmetik baseline;
  matematika ekuitas memakai `self.cash` yang benar — lihat catatan baseline).

## Pertanyaan yang dijawab laporan ini

Apakah wheel + 3 lever defensible mengalahkan SPY buy-hold pada window yang sama?
Jawaban apa punnya dicatat apa adanya di `report.md` — termasuk jika tetap kalah
(bull window memang medan paling buruk bagi wheel menurut WheelMetrics sendiri).
