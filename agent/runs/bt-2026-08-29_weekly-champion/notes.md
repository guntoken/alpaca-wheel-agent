# Run notes — VARIANT C: Weekly Champion Wheel (selection-first, 1 tahun)

## Pertanyaan pemilik (30 Agu 2026)

*"Apakah strategy bisa dioptimalkan memakai 1 saham pilihan mingguan di mana saham
ini benar-benar sudah dipilih oleh bot? Seperti WheelMetrics — stock selection dulu.
Backtest 1 tahun saja dulu. Asumsi saya: PnL jauh lebih baik dari SPY buy-hold."*

Asumsi pemilik DIUJI, bukan dikonfirmasi. Aturan di-commit SEBELUM melihat hasil.

## Desain (pre-committed)

Filosofi WheelMetrics "start with the stock, not the premium" — versi ekstrem:
**satu CSP per minggu, hanya di juara seleksi.**

- **Universe 24 nama likuid**: 12 baseline + AMD, NVDA, PLTR, SNAP, COIN, MSTR,
  XOM, CVX, DIS, CAT, NKE, BA. Data saham via CLI (iex/raw, warmup 2023-06);
  ladder opsi hanya di-fetch untuk kandidat terpilih.
- **Skor mingguan (Senin)**: wajib lulus gate kualitas close > SMA200 nama;
  ranking gabungan = rank(momentum 63 hari) + rank(vol-dollar percentile, floor
  40 persen); syarat 1 kontrak terjangkau budget. Juara dipilih; jika kontraknya
  tak viable (ladder kosong/filter), turun ke peringkat 2 lalu 3. Tidak ada
  CSP di minggu itu bila semua gagal (dry powder).
- **Konsentrasi**: budget per-nama 18% → **40%** ekuitas (inilah premis
  konsentrasi pemilik). Total cap 72% tetap.
- **Selebihnya baseline murni**: delta 0,30 (BEAR 0,20), DTE 7–35, premium
  ≥ 0,5% kolateral, TP 50%, roll-for-credit di delta 0,60, assignment → CC
  delta 0,25 strike ≥ max(cost, Bollinger 2σ), drawdown stop 3%, gate SPY
  harian −2%/−4%. Bunga kas TIDAK dimodelkan (isolasi efek seleksi+konsentrasi).
- **Window 1 tahun**: 2025-08-01 → 2026-07-31 (12 bulan terakhir lengkap).
- CC pada saham hasil assignment tetap dijalankan nama apapun; CSP baru hanya
  untuk juara minggu (nama yang sedang dipegang dikecualikan dari seleksi).

## Kontrol interpretasi (dibaca saat analisis, bukan tuning)

- Bandingkan vs **SPY buy-hold window sama** dan vs **baseline wheel di-slice
  window sama** (equity.csv baseline, 2025-08→2026-07).
- Menang/menguasai bisa karena (a) skill seleksi, (b) sekadar konsentrasi beta,
  atau (c) luck satu tahun. Kontrol (a): distribusi champion yang dipilih vs
  return nama-nama itu. Tahun tunggal = bukan bukti statistik — klaim apa pun
  dibatasi window ini.
- Risiko model: 1 nama = gap earnings/blackout tidak dimodelkan bisa menghantam
  penuh 40% posisi (deviasi baseline: blackout kosong).

## Deviasi teknis

- Single-pass, tanpa healing (cache opts terverifikasi run baseline; ladder
  nama baru di-fetch on-demand saat walk).
- `agent/dashboard/backtest.json` tidak ditimpa (milik baseline).
- Kolom `cash` trades.csv tetap notional display (warisan baseline).
