# Draft pertanyaan Discord event — klarifikasi run pendek di akun fresh

**KOREKSI FAKTA PENTING (31 Agu ~11:15 WIB):** versi lama pertanyaan ini
mengklaim akun dev "dibuat khusus untuk hackathon (28 Agu)". **KLAIM ITU
SALAH** — diverifikasi via API 31 Agu pagi:

- account_number `PA3BYE908A4N`, ID `678f4c0a-6b5f-499f-970c-b8b5f4dfe85b`
- `created_at` = **2026-03-26**, dengan JNLC +$100.000 tgl 25–26 Maret
- **nol aktivitas 26 Maret → 28 Agu** (fee trade pertama 28 Agu 14:59 UTC,
  kickoff). Akun idle 5 bulan, lalu 100% dipakai project ini.
- Kondisi 31 Agu pagi: 4 posisi short put terbuka (F×13, INTC×5), 0 order
  terbuka, equity $99.698,16, semua order via API.

Artinya akun dev = "existing account" menurut teks aturan apa pun →
**FLIP KE AKUN BARU KINI WAJIB, bukan default.** Pertanyaan lama ("apakah
akun kami dianggap brand-new") MATI — jangan pernah diposting (premisnya
terbantahkan `created_at`; organizer bisa cek sendiri via account ID).

Yang masih layak ditanyakan: durasi run penilaian pendek + pemisahan akun.
Semua cabang jawaban → tetap flip hari ini; jawaban hanya informatif.

---

## Versi utama (~880 char — aman di bawah batas 2.000)

```text
Hi organizers — quick check on the "brand-new account" rule before we submit.

Our agent has run on paper since kickoff day (first order Aug 28), but on a paper account we'd created months earlier — it sat idle at $100k with zero trades until the event started. Reading the rule strictly ("a brand-new account dedicated to this hackathon"), we're treating that account as build evidence only and creating a fresh $100k paper account today for the judged run.

Two quick checks:
1. Is a judged run of ~3 trading sessions (fresh account → Sep 4 deadline) acceptable?
2. We'd submit only the new account ID, with the earlier run documented in our public repo/journal as build evidence — is that the intended split?

Thanks!
```

## Versi mini (fallback, ~400 char)

```text
Quick check on the "brand-new account" rule: our agent has traded paper since kickoff (Aug 28), but on an account created months earlier (idle, $100k, zero trades before the event). We're creating a fresh $100k account today for the judged run. Is a ~3-session run to the Sep 4 deadline acceptable, with the earlier account documented in our repo as build evidence? Thanks!
```

## Setelah dijawab (semua cabang → flip tetap hari ini)
- "3 session OK, new ID only" → lanjut runbook flip sore ini tanpa perubahan.
- "3 session terlalu pendek / ideally longer" → TETAP flip secepatnya hari ini
  (kriteria #1 = P&L; tiap malam trading tambahan = nilai; tidak ada cara
  membuat waktu tambahan).
- Tidak dijawab sampai sore → flip tetap (aturan eksplisit + created_at Maret
  membuat satu-satunya jalur compliant adalah akun baru).

## Runbook flip: SUBMISSION_PLAN.md §"Runbook flip akun paper"
