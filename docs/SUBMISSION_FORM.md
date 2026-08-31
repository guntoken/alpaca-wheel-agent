# SUBMISSION_FORM — teks final untuk formulir lablab (paste-ready)

Batasan diverifikasi dari (a) panduan resmi lablab 9-field, (b) FORM ASLI
Step 1/3 yang dilihat pemilik 30 Agu, (c) halaman event Alpaca (syarat akun,
account ID, kriteria juri). Form = 3 step. Status: **draft final** — buka
draft di lablab lebih awal, paste semua kecuali video URL & account ID,
submit final Rabu 2 Sep.

---

## 1. Submission Title (form: 0/50 char, min 5)

```
OWL Agent — an options wheel whose AI says only NO
```

(50 char — PAS batas; counter JS em-dash = 1 char.)

Alternatif bila counter menolak tepat-50:
- `OWL Agent: options wheel, AI can only say NO` (44)
- `OWL (Option-WheeL) Agent — AI can only say NO` (45)

## 2. Short Description (form: 0/255 char, min 50 — terpakai 244)

```
An autonomous options-wheel agent on Alpaca paper trading: a deterministic engine sells cash-secured puts and covered calls on hard-coded rails, while a Claude layer reads the market regime and vetoes risky entries — an AI that can only say NO.
```

## 3. Long Description (form: 0/2000 char, min 600 — terpakai 1.149 char / 195 kata)

```
Retail options income should be boring: sell cash-secured puts, take profit at 50%, roll for credit, sell covered calls if assigned. In practice it is manual, emotional, and error-prone — and the usual "AI trading agent" (an LLM picking trades) makes it worse. LLMs hallucinate, drift, and cannot be held to a risk mandate.

OWL Agent inverts that design. A deterministic engine does 100% of the trading on hard-coded rails — the classic wheel — live and unattended on Alpaca paper trading since day 1 of the hackathon. Above it sits a Claude layer with exactly two powers: read the market regime, and veto a new entry. It can never place, size, or force a trade, and it can never block an exit. An AI that can only say NO is an AI you can actually trust on a broker.

The audience is retail traders earning options income. Evidence: a 2.5-year backtest on real Alpaca option-trade bars (live-engine rules returned +32.2% with drawdown control; a pre-committed selection-first variant beat SPY +54.6% vs +45.6%), a read-only hosted dashboard with a live stress test, and a public decision journal — every order, every regime read, failures included.
```

## 4. Categories — Event Tracks + Technologies Used

- **Event Tracks** (pilihan track event; ikuti yang tersedia di form):
  `Options Alpha Agents` (main challenge resmi).
- **Technologies Used**: `Alpaca Trading API` · `Alpaca MCP Server` ·
  `Alpaca CLI` · `Python` (+ `Streamlit` bila ada).

## 5. Social Media Post Link 1–5 (extra challenge "Build in Public")

Halaman event menyebut eksplisit **X dan LinkedIn**, tag @lablabai + @Alpaca,
maksimal 5 link. 5 field = MAX, bukan kuota — kualitas > jumlah. Rencana:

| # | Platform | Konten | Waktu |
|---|---|---|---|
| 1 | X (thread) | night recap + angka live + link dashboard (`SOCIAL_POST_2.md`) | Senin 31 Agu |
| 2 | LinkedIn | versi ~120 kata (`SOCIAL_POST_2.md`) | Senin 31 Agu |
| 3 | X | hasil backtest 2,5 th + pelajaran K=1 gagal | Selasa/Rabu |
| 4 | X/LinkedIn | final results + video | Kamis 3 Sep |

(Facebook/Medium tidak disebut event — skip; Medium opsional Kamis bila
sisa waktu, republish WRITEUP.)

## 6. Cover Image — ✅ SIAP

`docs/cover-16x9.png` (PNG, 16:9, headline K=3 +54.6% vs SPY).

## 7. Video Presentation (≤5 mnt, MP4) — rekam Selasa 1 Sep

- Skrip + shot list + checklist rekam: `docs/VIDEO_SCRIPT.md`
- Speaker notes per slide: `docs/SLIDE_NOTES.md`
- Rekam browser fullscreen di **https://alpaca-wheel-agent.streamlit.app**
- Simpan `docs/demo-video.mp4`; unggah ke platform submission → tempel URL
  ke formulir (jangan commit bila >50 MB)

## 8. Slide Presentation (PDF) — ✅ SIAP

`docs/slides.pdf` — 10 halaman 16:9, EN, 2–3 kalimat/slide.

## 9. GitHub Repository — ✅ LIVE

```
https://github.com/guntoken/alpaca-wheel-agent
```

Publik, commit harian sepanjang window lomba. Catatan "IBM Bob report" di
panduan = boilerplate template dari hackathon IBM; padanan agent-native kami
(tercantum juga di README): decision journal `agent/journal.jsonl` (setiap
order + alasan + regime read + error), `docs/RESEARCH_NOTES.md` (setiap
adopsi/penolakan desain bersumber), dan `agent/runs/` (artifact backtest
lengkap, kegagalan termasuk).

## 10. Application URL — ✅ LIVE

```
https://alpaca-wheel-agent.streamlit.app
```

Dashboard read-only 6 tab (Command Center / Risk Lab + stress test /
AI Brain / Execution Desk / About + FAQ), tanpa kredensial apa pun.

## 11. Alpaca paper trading account ID — ⚠️ WAJIB — ✅ TERISI

> "Your final submission must include the Alpaca paper trading account ID
> used for the hackathon. This allows the judging team to identify your
> trading activity and evaluate your P&L performance."

**`84705518-320e-457b-a68e-46c099b8ff06`**

Akun judged: `PA3F0TJJ7C7W`, dibuat 31 Agu 2026 12:04 WIB (brand-new,
$100.000 flat, options lv 3/3), diverifikasi via API. Jendela skor resmi:
Sen 31 Agu 09:30 ET → snapshot close Thu 3 Sep (SUBMISSION_PLAN §Jendela
skor). ⚠️ Jangan top-up/reset akun selama window — snapshot = total equity.

---

## Fakta eligibilitas penting (halaman event, 30 Agu)

- **Akun HARUS baru**: "create a brand-new Alpaca paper trading account
  dedicated to this hackathon. Projects run on an existing or reused
  account will not be eligible for judging." Starting balance $100.000.
  → runbook flip ada di SUBMISSION_PLAN.md.
- **Kriteria juri (urutan resmi)**: 1) P&L Performance 2) Technology
  Implementation 3) Creativity & Originality 4) Presentation & Execution.
  P&L dinilai → makin malam berjalan akun judged = makin baik → flip
  akun SEBAIKNYA Senin malam, bukan Selasa.
- One-page write-up wajib (AI logic, risk gates, Alpaca infra) → ✅
  `docs/WRITEUP.md`.

## Checklist dry-run Rabu 2 Sep

- [ ] Semua field di atas dipaste (title, short, long, categories, tech)
- [ ] Alpaca account ID terisi (akun baru $100k)
- [ ] Social link 1–3 (min. X + LinkedIn) terisi
- [ ] Cover + slides.pdf terunggah
- [ ] Video URL terisi (dari Selasa)
- [ ] Repo + demo URL valid saat di-preview
- [ ] Loop live masih berjalan di akun judged (jangan matikan sampai 4 Sep)
- [ ] Post sosial final terkirim; kumpulkan URL-nya
