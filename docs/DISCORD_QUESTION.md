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

**TERJAWAB TIDAK LANGSUNG 31 Agu siang** — admin menjawab peserta lain:
(02:33) akun brand-new wajib, akun existing/reused tak eligibel; (04:39)
akun baru di profil lama acceptable, hapus akun lama tak wajib; (04:16)
penghubung penilaian = account ID di form submission. Rencana kita persis
jalur itu — pertanyaan kita tinggal menunggu jawaban formal, keputusan
sudah final: FLIP SORE INI.
- "3 session OK, new ID only" → lanjut runbook flip sore ini tanpa perubahan.
- "3 session terlalu pendek / ideally longer" → TETAP flip secepatnya hari ini
  (kriteria #1 = P&L; tiap malam trading tambahan = nilai; tidak ada cara
  membuat waktu tambahan).
- Tidak dijawab sampai sore → flip tetap (aturan eksplisit + created_at Maret
  membuat satu-satunya jalur compliant adalah akun baru).

## Runbook flip: SUBMISSION_PLAN.md §"Runbook flip akun paper"

---

## Follow-up (31 Agu siang — post sebagai reply di thread jawaban admin)

Konteks: admin ( orang lain) sudah jawab resmi — window P&L Sen 31 Agu 09:30 ET
→ Jum 4 Sep 09:30 ET, snapshot equity total di close Thu 3 Sep, posisi expire
Jum 4 Sep dikecualikan dari pengukuran. Kunci interpretasi terakhir utk sizing:

```text
Thanks! One follow-up so we size correctly: for positions expiring Fri Sep 4
that are excluded from the measurement — the premium already received (cash in
the account) still counts toward the total equity snapshot at Thu close,
correct? i.e. only the position's mark at Thu close is excluded, not the
trade's cash. Thanks!
```

(~330 char.) Kalau admin konfirmasi → sprint 4-Sep jalan penuh Sen–Rab.
Kalau dibalik ("seluruh ekonomi trade dikecualikan") → set SPRINT_EXPIRY=None
Selasa pagi dan jalankan wheel murni — premium TP-50 buyback tetap dihitung
sebagai cash equity biasa.
