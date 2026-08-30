# Draft pertanyaan Discord event — klarifikasi aturan "brand-new account"

Tujuan: memastikan interpretasi syarat akun SEBELUM flip Senin sore.
Default tetap FLIP (aman di kedua interpretasi); jawaban organizer hanya
mengubah keputusan kalau mereka bilang eksplisit akun dev sekarang boleh.
Post di Discord event (channel help/questions), tag mentor bila diizinkan.
Fakta akun diverifikasi 31 Agu pagi: 4 posisi short put terbuka, 0 order
terbuka, equity $99.698,16, semua order via API (tanpa trade manual).

---

## Versi lengkap (disarankan)

```text
Clarification on the "brand-new account" rule — dev account created at kickoff, now holding open positions

Hi organizers — we'd like to double-check the account requirement before
finalizing our submission.

Our situation:

- We built an autonomous options-wheel trading agent using the Trading API,
  the Alpaca CLI, and the Alpaca MCP server.
- Our paper account was created specifically for this hackathon at the very
  start of the event window (Aug 28), with the $100,000 starting balance,
  and it has never been used for anything else — no manual trades; every
  order was submitted programmatically by the agent via the API.
- It has been trading live since day 1 and currently holds open short-put
  positions that were opened during the first market sessions.
- Like most builds, our code iterated during the event (two bugs found via
  the agent's own decision journal and fixed mid-week), so the account's
  history spans a few code versions.

The rules say: "For your final submission, create a brand-new Alpaca paper
trading account dedicated to this hackathon. Projects run on an existing or
reused account will not be eligible for judging."

Our questions:

1. Does our account qualify as "brand-new ... dedicated to this hackathon" —
   given it was created for this event — even though it already carries
   development-phase trading history and open positions?
2. If not, we will create a fresh $100,000 account for the judged run. Is it
   acceptable for that fresh account to start trading only a few days before
   the submission deadline (~3 trading sessions), or do you expect a longer
   judged window?
3. If a fresh account is required, should the submission include only the
   new account ID, with the dev account's history kept purely as build
   evidence (journal / README / social posts)?

Happy to flip to a fresh account either way — we just want to submit in the
intended way. Thank you!
```

## Versi singkat (fallback bila channel ketat)

```text
Quick check on the "brand-new account" rule: our paper account was created
specifically for this hackathon right at the start (Aug 28), funded at
$100,000, used only by our agent (no manual trades), and it now holds open
positions from the first sessions. Does that count as "a brand-new account
dedicated to this hackathon", or must we create a fresh account at
submission time? If fresh is required, is a judged run of ~3 trading days
before the deadline acceptable?
```

## Setelah dijawab

- Organizer: "current account OK" → keputusan pemilik: tetap flip (default,
  bersih + sesuai teks) ATAU pertahankan akun (track record lebih panjang,
  tapi posisi kode-lama tetap menodai atribusi P&L — saya tetap rekomendasi flip).
- Organizer: "fresh account required" → lanjut runbook flip Senin sore tanpa
  keraguan (SUBMISSION_PLAN.md).
- Tidak dijawab sampai Senin sore → flip sesuai default (teks aturan eksplisit).
