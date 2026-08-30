# OWL Agent — per-slide speaker notes (informal English, read-aloud)

Untuk video pendekatan "baca tiap slide". Total ±730 kata ≈ 4:50–5:00 di
kecepatan santai (~145 kata/menit). Semua angka sudah ditulis **sebagaimana
diucapkan** — tinggal dibaca. Kalimat pendek-pendek, dibuat untuk napas
natural. Rekaman: buka `docs/slides.pdf` mode fullscreen/presentasi, wajah
pojok (Loom/OBS), baca note sambil mata sesekali ke slide.

---

## Slide 1 · Cover — ±28 detik

> Hi everyone. This is OWL Agent — short for Option-WheeL. It's an
> autonomous options trading agent with one big twist: the AI can only say
> NO. It never picks a trade. It can only refuse one. And the numbers you
> see here are real — our backtest beat SPY, it's been running live on
> Alpaca paper since day one, and everything is public. Let me show you
> how it works.

*Cue: senyum, tatap kamera. Tunjuk tile "+54.6%" sekali.*

## Slide 2 · The problem — ±30 detik

> So here's the problem. Selling options for income should be boring —
> but real people can't stay boring. They panic-buy back losing puts, they
> oversize one winner, they pick the wrong strike. And the popular answer
> — hey, let an AI pick the trades — actually makes it worse. LLMs
> hallucinate. You can't hold a chatbot to a risk mandate. And the market
> is huge: fifteen point two billion contracts last year, with retail
> driving up to sixty percent of the flow.

*Cue: gesture ke tiga kartu satu-per-satu saat menyebutnya.*

## Slide 3 · The solution — ±33 detik

> So we flipped the design. A deterministic engine does all the trading —
> the classic wheel, on hard-coded rails. Delta around zero point three,
> take profit at fifty percent, roll only for credit. And above it sits
> Claude, with exactly two powers: read the market regime, and veto a new
> entry. That's it. It can't place, size, or force a trade — and it can
> never block an exit. An AI that can only say no... is an AI you can
> actually trust on a broker.

*Cue: jeda setengah detik sebelum kalimat terakhir — itu tagline.*

## Slide 4 · One cycle, six steps — ±30 detik

> Every cycle runs six steps. Observe — the broker is the source of
> truth. Gate — kill switch, drawdown stop, and two regime readers:
> Claude's judgment plus a hard-coded SPY anchor. The tighter one always
> wins. Decide — the wheel logic, per name. Then the AI veto — one
> refusal kills the entry. Execute with limit orders, exits first. And
> everything lands in a public journal. That journal caught two real bugs
> on night one — both fixed live, in the open.

*Cue: hitung enam kotak dengan kursor mengikuti urutan; berhenti di kotak 4 (gold).*

## Slide 5 · Risk gates — ±28 detik

> Safety here isn't vibes — it's arithmetic. Max five names, two per
> sector, eighteen percent per name. Seventy-two percent of equity as
> collateral when the tape is strong — half of that when it's neutral.
> No new entries after a three percent down day, or a four percent SPY
> drop. Earnings blackouts. And a kill switch — one file, and the agent
> stops submitting anything. De-risking is never blocked. Only new risk
> can be vetoed.

*Cue: nada cepat-confident; ini slide "boring by design" — biar terdengar begitu.*

## Slide 6 · Live run — ±28 detik

> And this is not a mockup. It's been running unattended on Alpaca paper
> since day one of the hackathon. Twenty-five live cycles, four fills,
> seventeen hundred fifty-three dollars in premium. Thirty-one risk-on
> reads, eight neutral, zero vetoes so far — the veto path itself is
> tested in dry runs. The dashboard behind me is the real one — six tabs,
> and the equity curve is built straight from the agent's own journal.

*Cue: kalau video menampilkan dashboard sesaat, alt-tab singkat lalu kembali.*

## Slide 7 · The backtest — ±33 detik

> Now the evidence. Two and a half years, backtested on real Alpaca
> option trades — every single premium is a real traded bar, nothing
> synthetic. The mode on screen: each Monday the bot scores twenty-four
> names and picks the top three. The result — plus fifty-four point six
> percent, versus SPY's forty-five point six. And right next to it, the
> deeper drawdown: twenty-one and a half percent. We show it, because
> that's the honest price of concentration.

*Cue: kursor ikuti garis emas di chart pelan, lalu tunjuk angka DD.*

## Slide 8 · Why top-3 — ±33 detik — *slide terpenting*

> And here's how we picked that mode — this one matters. We ran a series
> of backtests to beat buy-and-hold. One stock a week beat SPY in its
> first year — but lost over the full two and a half years. So we
> rejected it. Two picks and five picks lost outright. Three picks beat
> SPY in both windows — the one year, and the two and a half. That's why
> top-three is our headline. And yes — even the failures are published.

*Cue: tunjuk baris champion (merah) saat "we rejected it", baris top-3 saat "both windows".*

## Slide 9 · Business — ±28 detik

> So, who pays for this? US options just printed its sixth straight
> record — fifteen point two billion contracts. Every competitor on this
> slide automates execution. Nobody sells what we have: an AI risk
> governor whose alignment is provable — it literally cannot churn your
> account. Twenty-nine a month for the engine and the governor.
> Seventy-nine for multi-account and defined-risk spreads. We're paid to
> keep users safe — not to grow their volume.

*Cue: tangan membuka saat "Nobody sells what we have".*

## Slide 10 · Close — ±28 detik

> Everything runs on all three Alpaca surfaces — the SDK, the CLI, and
> the MCP server, live inside the AI session itself. Next up: a
> defined-risk spreads sleeve, walk-forward validation of every gate, and
> the selection-first mode behind an opt-in. The repo, the journal, every
> backtest — all public, failures included. OWL Agent: the AI doesn't
> pick your trades. It makes sure you survive them. Try it — the link is
> right there. Thanks for watching.

*Cue: kembali tatap kamera di dua kalimat terakhir, senyum, diam 1 detik sebelum stop.*

---

## Checklist rekam versi slide-reading

- [ ] PDF mode fullscreen (Ctrl+L di kebanyakan viewer) — pindah slide dengan panah
- [ ] Wajah pojok kanan bawah; cahaya dari depan; mic dekat mulut
- [ ] Test 20 detik dulu (slide 1) — cek volume + posisi wajah
- [ ] Jangan buru-buru di slide 8 (kisah seleksi) — itu momen paling kuat
- [ ] Ekspor MP4, cek ≤5:00 dan ≤100 MB
