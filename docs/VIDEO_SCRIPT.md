# OWL Agent — demo video script (≤5 minutes, English narration)

Target: lablab.ai × Alpaca judges. Tone: calm, confident, honest. Pace ≈ 140
words/min. Total narration ≈ 640 words. Record 1080p, browser FULLSCREEN on
**https://alpaca-wheel-agent.streamlit.app** (not localhost — show the real
URL). Slow mouse; hover charts 2–3 s before speaking about them; leave 1 s of
silence at each cut point.

Sumber nomor — jangan improvisasi angka di depan kamera:
+54.6% = selection-first variant (bot picks 3/week), 2.5 yr, DD 21.5%;
SPY +45.6% DD 19.0%; live-engine run +32.2% DD 18.3%; live paper: 25 cycles,
$1,753 premium; 15.2B contracts 2025; retail 30–60%; $29/$79 pricing.

---

## 0:00–0:30 · THE PROBLEM (~70 words)

**SCREEN:** PDF cover slide (or dashboard hero, slow zoom in). Then slide 2.

> Retail options income should be boring. Sell a cash-secured put, take
> profit at fifty percent, roll for credit, sell a covered call if you're
> assigned — repeat. In practice it's manual, emotional, and error-prone:
> the wrong delta, panic buy-backs, one oversized ticker. And the usual "AI
> trading agent" makes it worse — an LLM asked to pick trades hallucinates,
> drifts, and cannot be held to a risk mandate.

**CUT:** hard cut on "risk mandate."

## 0:30–1:10 · THE IDEA (~95 words)

**SCREEN:** slide 3 (two columns), slow pan left→right. Then dashboard
**About** tab, top note visible.

> So we inverted the design. This is OWL — the Option-WheeL Agent. A
> deterministic engine does one hundred percent of the trading on
> hard-coded rails: the classic wheel. Above it sits a Claude layer with
> exactly two powers: read the market regime, and veto a new entry. It can
> never place, size, or force a trade — and it can never block an exit.
> An AI that can only say NO is an AI you can actually trust on a broker.

**CUT:** to the hosted dashboard Command Center.

## 1:10–3:05 · LIVE DEMO (~300 words) — the core, do not rush

**SCREEN A (1:10–1:40) — Command Center.** Point (hover) at: equity chart →
premium card → regime ribbon → wheel stepper.

> This is the live system, running unattended on Alpaca paper since day one
> of the hackathon. The Command Center shows the equity curve built from the
> agent's own decision journal, premium collected, the wheel stage for every
> name — and the two regime readers side by side: Claude's judgment, and a
> deterministic SPY anchor. The tighter of the two always governs.

**SCREEN B (1:40–2:10) — Risk Lab.** Click tab; run the stress test slider
to −5%; let the number settle.

> The Risk Lab is where safety is inspectable. Every position with its
> collateral, the concentration caps, the full list of hard-coded rails —
> and a live stress test: drag the market down five percent and watch what
> the book does before it happens for real.

**SCREEN C (2:10–2:35) — AI Brain.** Click tab; scroll one regime read;
point at the veto column.

> The AI Brain tab shows Claude's actual words, every cycle — each regime
> read with its stated reason, and the veto path. In the judged window:
> thirty-one risk-on reads, eight neutral, zero vetoes — the veto path is
> exercised in dry-runs, and every refusal would be journaled verbatim.

**SCREEN D (2:35–3:15) — About tab.** Click tab; hover the equity chart
crosshair slowly left→right; point at +54.6% card, then 21.5% card.

> The evidence. A two-and-a-half-year backtest on real Alpaca option
> trades — every premium a real traded bar. The selection-first mode, where
> the bot picks three stocks a week, returned plus fifty-four-point-six
> percent versus SPY's forty-five-point-six — and right next to it, the
> deeper drawdown, because that's the honest price of concentration. How
> did we pick this mode? A series of backtests. One stock a week beat SPY
> in its first year — but lost over the full two-and-a-half-year window,
> so we rejected it. Three stocks a week beat SPY in BOTH windows — one
> year, and two-and-a-half years. That's the mode we selected, and its
> full paper trail is public, failures included.

**CUT:** to slide 8 (explorations table) for 2 seconds if timing allows.

## 3:15–3:55 · BUSINESS CASE (~100 words)

**SCREEN:** slide 9. Point at TAM tile, then competitor table.

> Who pays for this? US options just printed fifteen-point-two billion
> contracts — the sixth straight record — with retail at thirty to sixty
> percent of flow. Every competitor automates execution; none of them sells
> an AI risk governor whose incentive alignment is provable — a layer that
> cannot trade cannot churn your account. Twenty-nine dollars a month for
> the engine and the governor; seventy-nine for multi-account and
> defined-risk spreads.

**CUT:** to slide 10.

## 3:55–4:45 · WHAT'S NEXT + TRUST (~90 words)

**SCREEN:** slide 10; end on the hosted dashboard FAQ tab, "Can it lose
> money?" expander opened.

> Next: a defined-risk spreads sleeve, walk-forward re-validation of every
> gate, and the selection-first mode behind an opt-in with tighter drawdown
> limits. Everything you've seen is public: the repo, the decision journal
> with every order and reason, every backtest artifact — including the
> failures. The FAQ even answers "can it lose money?" honestly: yes.

## 4:45–5:00 · CLOSE (~35 words)

**SCREEN:** back to dashboard hero (OWL logo). Hold still.

> OWL Agent. The AI doesn't pick the trades — it makes sure you survive
> them. Try it yourself: alpaca-wheel-agent dot streamlit dot app.

---

## Recording checklist

- [ ] OBS (or any recorder) 1080p60, browser fullscreen, hide bookmarks bar
- [ ] Mic test; room quiet; narrate slightly slower than comfortable
- [ ] Use the HOSTED URL (the address bar is visible proof)
- [ ] Stress-test slider: one smooth move to −5%, hold 3 s
- [ ] Chart hover: slow sweep, let the tooltip track
- [ ] Export MP4 H.264; check ≤5:00 and ≤100 MB before uploading
- [ ] Simpan sebagai docs/demo-video.mp4 (jangan commit bila >50 MB —
      unggah ke platform submission dan cantumkan tautannya)
