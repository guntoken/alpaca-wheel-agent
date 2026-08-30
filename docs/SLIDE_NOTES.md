# OWL Agent — per-slide speaker notes (mengikuti teks PDF, EN informal)

Prinsip sesuai permintaan: **notes mengalir mengikuti teks slide dari atas ke
bawah** — seperti membaca PDF-nya, hanya diberi kata sambung/kata bantu agar
enak didengar. Semua angka ditulis **sesuai pelafalan**. Total ±770 kata ≈
5:00–5:10 di kecepatan santai; kalau terasa mepet, potong satu kalimat di
slide 3 atau 8 (sudah kutandai). Rekam: PDF fullscreen (Ctrl+L), pindah slide
dengan panah, wajah pojok kanan bawah.

---

## Slide 1 · Cover — ±30 detik

> Hi everyone — this is OWL Agent, short for Option-WheeL: an autonomous
> options wheel with an AI risk governor. The whole idea is in this one
> line: an AI that can only say NO. A deterministic engine does the
> trading, and Claude holds exactly two powers — read the regime, and
> veto a new entry. It never places, sizes, or forces a trade, and it
> never blocks an exit. Back here: plus fifty-four point six percent,
> live since day one, one hundred percent public. Let me show you.

## Slide 2 · The problem — ±30 detik

> So, the problem: options income is a discipline problem disguised as a
> trading problem. The wheel should be boring and repeatable — and real
> people can't do it. The wrong delta, panic buy-backs, one oversized
> ticker. And the popular fix — an AI that picks the trades — actually
> makes it worse: LLMs hallucinate, drift, and can't be held to a risk
> mandate. Meanwhile the market is huge: fifteen point two billion
> contracts in twenty twenty-five, with retail at thirty to sixty percent
> of the flow.

## Slide 3 · The solution — ±32 detik

> Our solution: invert the design — the AI governs, the engine trades.
> On the left, the deterministic engine that does everything: puts at
> delta zero point three, profit taken at fifty percent, rolls only for
> credit, covered calls above cost and the Bollinger band. On the right,
> the Claude governor, which may only refuse: it reads the regime every
> cycle, and it vetoes new entries — one refusal with a reason kills it.
> It can never place, size, or force a trade, and never block an exit.
> *(kalau mepet, hapus:)* Incentive alignment by construction.

## Slide 4 · How it works — ±33 detik

> How it works: one cycle, six steps — every five to fifteen minutes
> while the market is open. The broker is the source of truth, and
> everything is appended to a public journal. Observe — the account and
> market snapshot. Gate — kill switch, drawdown stop, dual regime
> readers. Decide — the wheel logic per name. Then the AI veto — Claude
> reviews each entry, one NO kills it. Execute — marketable limits,
> exits first. And journal — every order and reason, public. The regime
> also scales exposure: seventy-two percent collateral in risk-on,
> thirty-six in neutral, no new entries in risk-off — and the tighter
> reader always wins.

## Slide 5 · Safety — ±30 detik

> Safety is hard-coded, not vibes — every gate on this slide is a
> deterministic check that runs before any order. Five names max, two
> per sector, eighteen percent per name. Seventy-two percent of equity
> as total collateral — or thirty-six when the tape is weak. A minus
> three percent daily drawdown stops new entries. SPY down two percent
> halves the budget; down four percent, entries stop entirely. Earnings
> blackouts. And the kill switch — one file, and nothing gets submitted.
> Exits are never vetoed: de-risking is always allowed.

## Slide 6 · Live run — ±28 detik

> And this is real — live and unattended on Alpaca paper since day one.
> Engine, governor, gates, journal: the whole system, running on its
> own. Four fills, seventeen hundred fifty-three dollars in premium.
> Twenty-five live cycles out of thirty-nine. Thirty-one risk-on reads,
> eight neutral, zero vetoes — the veto path is exercised in dry-runs.
> Behind me, the six-tab dashboard — and the equity curve is built
> straight from that journal.

## Slide 7 · The backtest — ±33 detik

> Now the evidence: backtested two and a half years on real option
> trades — and it beats SPY in its own bull window. The mode on this
> chart: every Monday the bot scores twenty-four names and sells puts
> on the top three only. Every premium is a real traded option bar, and
> no parameter was fitted to this window. The result: plus fifty-four
> point six percent, versus SPY's forty-five point six. Calmar one point
> three nine versus one point three four. And the deeper drawdown —
> twenty-one and a half percent — is shown, not hidden.

## Slide 8 · Why top-3 — ±33 detik — *slide terpenting*

> How we picked that mode: four configurations, one window, every result
> published. The live engine's own rules: plus thirty-two point two —
> trading upside for drawdown control. Add the defensive levers:
> thirty-four point two, smallest drawdown, best Calmar. One pick a
> week — the champion — beat SPY in year one, but didn't survive the
> full window... so we rejected it. Two picks and five picks lost
> outright. And three picks beat SPY in both windows — that's the
> headline, and that's why it's selected.

## Slide 9 · Business — ±30 detik

> The business: a paid governor in a market that has never been larger.
> Fifteen point two billion contracts — the sixth straight record —
> retail at thirty to sixty percent. Our TAM is four to eighteen billion
> a year; a realistic SAM, two hundred million to one point eight
> billion. Everyone on this table automates execution — none of them
> sells an AI risk governor with provable alignment. Pricing is simple:
> twenty-nine a month core, seventy-nine pro. No payment for order flow
> — we're paid to keep users safe, not to grow their volume.

## Slide 10 · Close — ±28 detik

> Finally: built on all three Alpaca surfaces — the SDK for the engine,
> the CLI for operations, and the MCP server, live inside the AI session
> itself. What's next: a defined-risk spreads sleeve, walk-forward
> validation of every gate, and the selection-first mode behind an
> opt-in. The repo, the journal, every backtest — all public, failures
> included. The AI doesn't pick your trades — it makes sure you survive
> them. Try it: the link is right there. Thanks for watching.

---

## Checklist rekam

- [ ] PDF fullscreen (Ctrl+L), pindah slide dengan panah — baca note, mata sesekali ke slide
- [ ] Wajah pojok kanan bawah, cahaya dari depan, mic dekat mulut
- [ ] Test 20 detik (slide 1) dulu — cek volume & posisi
- [ ] Slide 8 jangan diburu-buru — "so we rejected it" adalah momen terkuat
- [ ] Dua take; take kedua biasanya lebih santai
- [ ] Ekspor MP4, cek ≤5:00 dan ≤100 MB
