# OWL Agent — demo video script (3–4 minutes, English TTS narration)

**v2 — Rabu 2 Sep 2026**: dipendekkan 4:22 → **3:43** (~470 kata), slide-1 baru
(rails/leash), kalimat identitas diganti ke metafora rails/leash. Video = TTS
(`en-US-AndrewMultilingualNeural`, rate −6%) di atas still 1080p30 — build
script `/tmp/video-build/build.py` (venv `/tmp/videnv`: edge-tts +
imageio-ffmpeg; ffmpeg sistem tidak ada). Output: `docs/demo-video.mp4`
(10,7 MB, H.264+AAC).

Sumber nomor — jangan improvisasi angka:
+54.6% = selection-first variant (bot picks 3/week), 2.5 yr, DD 21.5%;
SPY +45.6% DD 19.0%; live-engine run +32.2% DD 18.3%; judged-window regime
reads 31 RISK_ON / 8 NEUTRAL / 0 veto; 15.2B contracts 2025; retail 30–60%;
$29/$79 pricing.

---

## 0:00–0:04 · COVER — silent 3,5 dtk

**SCREEN:** `slide-1.png` — "Trades on rails. / AI on a **leash**." (leash emas)

## 0:04–0:29 · THE PROBLEM — slide-2 (55 kata)

> Retail options income should be boring: sell a cash-secured put, take
> profit at fifty percent, roll for credit, sell a covered call if assigned.
> In practice it's manual, emotional, error-prone, and the usual AI trading
> agent makes it worse: an LLM asked to pick trades hallucinates, drifts,
> and cannot be held to a risk mandate.

## 0:29–0:59 · THE IDEA — slide-3 (75 kata)

> So we inverted the design. This is OWL, the Option Wheel Agent. A
> deterministic engine does one hundred percent of the trading on hard-coded
> rails: the classic wheel. Above it, a Claude layer with exactly two powers:
> read the market regime, and veto a new entry. It can never place, size, or
> force a trade, and it can never block an exit. An AI on a leash is an AI
> you can actually trust on a broker.

## 0:59–1:22 · LIVE: COMMAND CENTER — sc-1 (54 kata)

**SCREEN:** hosted Command Center screenshot (URL bar terlihat).

> This is the live system, running unattended on Alpaca paper since day one.
> The Command Center shows the equity curve from the agent's own decision
> journal, premium collected, the wheel stage for every name, and both regime
> readers side by side: Claude's judgment and a deterministic SPY anchor.
> The tighter of the two always governs.

## 1:22–1:39 · LIVE: RISK LAB — sc-2 (43 kata)

> The Risk Lab is where safety is inspectable: every position with its
> collateral, the concentration caps, the hard-coded rails, and a live stress
> test. Drag the market down five percent, and watch what the book does
> before it happens for real.

## 1:39–1:59 · LIVE: AI BRAIN — sc-3 (46 kata)

> The AI Brain tab shows Claude's actual words, every cycle: each regime
> read with its stated reason, and the veto path. In the judged window:
> thirty-one risk-on reads, eight neutral, zero vetoes. Every refusal would
> be journaled verbatim.

## 1:59–2:40 · THE EVIDENCE — sc-4 About (97 kata) — scene terpanjang, jangan dipotong lagi

**SCREEN:** hosted About tab: kartu +54.6%, chart equity vs SPY, bar premium.

> The evidence, and let's be clear which engine is which. The agent you saw
> trading live runs the five-name engine: its own two-and-a-half-year number
> is plus thirty-two-point-two percent. This chart is the pre-committed
> selection-first variant: the bot picks three stocks a week, every premium
> a real traded bar. Plus fifty-four-point-six versus SPY's forty-five-point-
> six, with a deeper drawdown: the honest price of concentration. Why this
> mode? One stock a week won year one but lost the full window, so we
> rejected it. Three stocks a week won both. The full paper trail is public,
> failures included.

## 2:40–3:08 · BUSINESS CASE — slide-9 (55 kata)

> Who pays? US options printed fifteen-point-two billion contracts, the
> sixth straight record, with retail at thirty to sixty percent of flow.
> Every competitor automates execution; none sells an AI risk governor with
> provable alignment. A layer that cannot trade cannot churn your account.
> Twenty-nine dollars a month; seventy-nine for multi-account and
> defined-risk spreads.

## 3:08–3:33 · WHAT'S NEXT + TRUST — slide-10 (49 kata)

> Next: a defined-risk spreads sleeve, walk-forward re-validation of every
> gate, and selection-first behind an opt-in with tighter drawdown limits.
> Everything you've seen is public: the repo, the decision journal, every
> backtest artifact, failures included. The FAQ even answers, can it lose
> money? Honestly: yes.

## 3:33–3:43 · CLOSE — sc-1 lagi (23 kata)

> OWL Agent. The AI doesn't pick the trades, it makes sure you survive
> them. Try it yourself, at alpaca-wheel-agent dot streamlit dot app.

---

## Checklist build (bukan rekaman manual — TTS over stills)

- [x] Slide PNG dari `docs/slides/` (slide-1 = cover rails/leash, regen 2 Sep)
- [x] Screenshot hosted dari `docs/video-assets/` (5 PNG, tangkap 1 Sep)
- [x] `python build.py` → TTS per scene → render → concat → `docs/demo-video.mp4`
- [x] QA: durasi 3:43 (≤4:00), 10,7 MB (≤50 MB), frame t=2s & t=120s tajam,
      stream H.264 1080p30 + AAC stereo
- [x] Approve suara pemilik — **APPROVED 3 Sep ~00:05 WIB** (play via Firefox,
      voice en-US-AndrewMultilingualNeural rate −6% dipertahankan)
