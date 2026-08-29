# Run notes — VARIANT D: Top-K weekly picks sweep (berapa nama per minggu?)

## Usulan pemilik (30 Agu 2026)

*"Setiap minggu pick 1 saham. Tapi jika pick 2-3 saham menghasilkan performance
1 tahun jauh lebih baik, buat 2-3 atau lebih. Fokus: performance makin optimal."*

## Desain (pre-committed sebelum hasil dilihat)

Identik dengan varian C (selection-first: gate SMA200, ranking momentum-63h +
vol-dollar percentile, affordability, fallback menyusuri ranking), beda SATU hal:
**tiap Senin jual CSP di K nama teratas**, K dari env `BT_TOPK` (2, 3, 5; K=1 =
hasil varian C, tidak diulang).

- **Equal-weight budget**: per-nama `min(40%, 72%/K)` → K=2: 36%, K=3: 24%,
  K=5: 14,4%. Total pajanan ±konstan antar-K sehingga sweep mengisolasi efek
  JUMLAH PILIHAN, bukan jumlah uang keluar.
- Percobaan kontrak dibatasi K+3 nama peringkat teratas per minggu (bind fetch).
- Window sama: 2025-08-01 → 2026-07-31. Engine/fee/fill model = baseline.
- Artefak di-TAG (k2_, k3_, k5_) dalam SATU folder berbagi opts_cache.

## Pertanyaan yang dijawab

Diversifikasi antar top-momentum: apakah menambah nama menaikkan return
(reward jika #2..#K ikut kuat) atau menurunkan (pengenceran dari juara #1)?
Dan bagaimana drawdown-nya? Hipotesis netral: return K>1 sedikit di bawah K=1,
drawdown lebih kecil — data yang memutuskan.

## Kontrol interpretasi

- Bandingkan K=1 (varian C) vs K=2/3/5 vs SPY vs baseline-wheel, window sama.
- K tetap seleksi momentum: menang di rezim momentum, membeli puncak di
  mean-reversion — berlaku untuk semua K.
- 1 tahun = 1 sampel per K.
