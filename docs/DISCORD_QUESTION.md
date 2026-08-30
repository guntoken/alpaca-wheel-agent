# Draft pertanyaan Discord event — klarifikasi aturan "brand-new account"

Tujuan: memastikan interpretasi syarat akun SEBELUM flip Senin sore.
Default tetap FLIP (aman di kedua interpretasi); jawaban organizer hanya
mengubah keputusan kalau mereka bilang eksplisit akun dev sekarang boleh.
Post di Discord event (channel help/questions), tag mentor bila diizinkan.
Fakta akun diverifikasi 31 Agu pagi: 4 posisi short put terbuka, 0 order
terbuka, equity $99.698,16, semua order via API (tanpa trade manual).

Batas Discord non-Nitro = 2.000 char. Versi utama di bawah = 1.161 char
✓ aman (judul +42 char bila ikut tercopy).

---

## Versi utama (1.161 char — aman di bawah batas 2.000)

```text
Hi organizers — quick clarification on the "brand-new account" rule before we submit.

Our paper account was created specifically for this hackathon (Aug 28, $100,000 start) and never used for anything else — no manual trades; every order came from our options-wheel agent via the Trading API. It has traded live since day 1 and still holds open short puts from the first sessions. One caveat: our code iterated during the event (bugs found and fixed mid-week), so its history spans a few code versions.

The rules say a submission must use "a brand-new Alpaca paper trading account dedicated to this hackathon" and that "projects run on an existing or reused account will not be eligible for judging."

Questions:
1. Does our account count as "brand-new / dedicated" since it was created for this event — despite carrying dev-phase history and open positions?
2. If we must create a fresh $100k account, is a judged run of ~3 trading sessions before the deadline acceptable?
3. If so, do we submit only the new account ID (dev history stays as build evidence in our repo/journal)?

Happy to flip either way — we just want to submit in the intended way. Thanks!
```

## Versi mini (fallback, ~600 char)

```text
Quick check on the "brand-new account" rule: our paper account was created for this hackathon at kickoff (Aug 28, $100k, agent-only trades, never used for anything else) and now holds open positions from week 1. Does it count as "a brand-new account dedicated to this hackathon", or must we create a fresh account at submission? If fresh is required, is a ~3-day judged run before the deadline OK?
```

## Setelah dijawab

- Organizer: "current account OK" → keputusan pemilik: tetap flip (default,
  bersih + sesuai teks) ATAU pertahankan akun (track record lebih panjang,
  tapi posisi kode-lama tetap menodai atribusi P&L — saya tetap rekomendasi flip).
- Organizer: "fresh account required" → lanjut runbook flip Senin sore tanpa
  keraguan (SUBMISSION_PLAN.md).
- Tidak dijawab sampai Senin sore → flip sesuai default (teks aturan eksplisit).
