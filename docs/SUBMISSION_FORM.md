# SUBMISSION_FORM — teks final untuk formulir lablab (paste-ready)

Sumber batasan: panduan resmi lablab.ai (9 field checklist). Semua teks di
bawah sudah dihitung panjangnya. Status: **draft final** — review pemilik,
lalu paste ke formulir saat dry-run Rabu 2 Sep. Video URL diisi setelah
rekam Selasa.

---

## 1. Project Title

```
OWL Agent — an autonomous options wheel whose AI can only say NO
```

(64 karakter; tidak ada batas resmi, jelas & deskriptif.)

Alternatif bila ingin lebih pendek:
- `OWL (Option-WheeL) Agent` (24)
- `OWL Agent — AI risk governor on an options wheel` (49)

## 2. Short Description (≤255 char — terpakai 244)

```
An autonomous options-wheel agent on Alpaca paper trading: a deterministic engine sells cash-secured puts and covered calls on hard-coded rails, while a Claude layer reads the market regime and vetoes risky entries — an AI that can only say NO.
```

## 3. Long Description (≥100 kata — terpakai 195)

```
Retail options income should be boring: sell cash-secured puts, take profit at 50%, roll for credit, sell covered calls if assigned. In practice it is manual, emotional, and error-prone — and the usual "AI trading agent" (an LLM picking trades) makes it worse. LLMs hallucinate, drift, and cannot be held to a risk mandate.

OWL Agent inverts that design. A deterministic engine does 100% of the trading on hard-coded rails — the classic wheel — live and unattended on Alpaca paper trading since day 1 of the hackathon. Above it sits a Claude layer with exactly two powers: read the market regime, and veto a new entry. It can never place, size, or force a trade, and it can never block an exit. An AI that can only say NO is an AI you can actually trust on a broker.

The audience is retail traders earning options income. Evidence: a 2.5-year backtest on real Alpaca option-trade bars (live-engine rules returned +32.2% with drawdown control; a pre-committed selection-first variant beat SPY +54.6% vs +45.6%), a read-only hosted dashboard with a live stress test, and a public decision journal — every order, every regime read, failures included.
```

## 4. Technology & Category Tags

Dipilih dari daftar tag lablab saat submit (urutan preferensi):

- `AI Agents` / `Autonomous Agents`
- `Fintech` / `Finance`
- `Trading` / `Trading Bots`
- `Python`
- `API`

## 5. Cover Image — ✅ SIAP

`docs/cover-16x9.png` (PNG, 16:9, headline K=3 +54.6% vs SPY).

## 6. Video Presentation (≤5 mnt, MP4) — rekam Selasa 1 Sep

- Skrip + shot list + checklist rekam: `docs/VIDEO_SCRIPT.md`
- Speaker notes per slide: `docs/SLIDE_NOTES.md`
- Rekam browser fullscreen di **https://alpaca-wheel-agent.streamlit.app**
- Simpan `docs/demo-video.mp4`; unggah ke platform submission → tempel URL
  ke formulir (jangan commit bila >50 MB)

## 7. Slide Presentation (PDF) — ✅ SIAP

`docs/slides.pdf` — 10 halaman 16:9, EN, 2–3 kalimat/slide.

## 8. GitHub Repository — ✅ LIVE

```
https://github.com/guntoken/alpaca-wheel-agent
```

Publik, commit harian sepanjang window lomba. Catatan "IBM Bob report" di
panduan = boilerplate template dari hackathon IBM; padanan agent-native kami
(tercantum juga di README): decision journal `agent/journal.jsonl` (setiap
order + alasan + regime read + error), `docs/RESEARCH_NOTES.md` (setiap
adopsi/penolakan desain bersumber), dan `agent/runs/` (artifact backtest
lengkap, kegagalan termasuk).

## 9. Application URL — ✅ LIVE

```
https://alpaca-wheel-agent.streamlit.app
```

Dashboard read-only 6 tab (Command Center / Risk Lab + stress test /
AI Brain / Execution Desk / About + FAQ), tanpa kredensial apa pun.

---

## Checklist dry-run Rabu 2 Sep

- [ ] Semua field di atas dipaste (title, short, long, tags)
- [ ] Cover + slides.pdf terunggah
- [ ] Video URL terisi (dari Selasa)
- [ ] Repo + demo URL valid saat di-preview
- [ ] Judged run berjalan di akun paper BARU $100k (flip keys Selasa)
- [ ] Post sosial final terkirim; kumpulkan ≤5 URL link untuk form
