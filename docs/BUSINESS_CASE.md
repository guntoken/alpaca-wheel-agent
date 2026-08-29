# Business Case — who pays for an AI-governed wheel agent

Material for the video (2:30–4:00) and the "market/revenue" slide. All market
numbers carry their source; Fermi estimates are labeled as such.

## The problem (one line)

Retail options-income traders must run a disciplined, boring, repeatable
process — and can't, because it is manual, emotional, and error-prone.

## Market size

**The market is at an all-time high, again.**
- US listed options volume hit **15.2 billion contracts in 2025**, +26% over
  2024 — the sixth consecutive annual record (Cboe, *State of the Options
  Industry 2025*).
- Retail is a major driver: estimates put retail at **30–37% of daily volume**
  (MEMX) to **45–60% of the options market** (Devexperts) — far above retail's
  ~20% share of equity volume.
- 0DTE alone is 24.1% of volume (Cboe) — the market is getting *more* retail,
  *more* short-dated, and *more* in need of discipline, not less.

**TAM/SAM/SOM (Fermi, stated honestly).**
- **TAM — English-speaking self-directed options-income traders.** Anchors:
  Schwab alone reports ~37.8M brokerage accounts (2025); industry estimates put
  active US options traders in the **~10–15M** range (no single authoritative
  count exists — stated as estimate). At a $30–100/mo automation subscription,
  TAM ≈ **$4–18B/yr**.
- **SAM — traders who want *systematic premium selling* (wheel/CSP style) and
  will connect a broker API.** Realistically 5–10% of the above → **$200M–1.8B/yr**.
- **SOM (3-yr, solo → small team)** — 5–20k subscribers at $25–50/mo →
  **$1.5–12M ARR**. Comparable platforms prove the price points (below).

## Competitive landscape (verified pricing, Aug 2026)

| Platform | Price | What it is | Gap we fill |
|---|---|---|---|
| **Option Alpha** | $99–149/mo (free w/ TradeStation/Tradier) | No-code bot builder; user writes the rules | No market judgment; bots execute whatever you tell them |
| **Composer** | $32–40/mo | No-code stock-algo platform | Equities-focused; options support thin |
| **Option Samurai** | $39–49/mo | Options scanner | Finds trades, doesn't manage them |
| **tastytrade** | $0 sub, $1/contract | Broker + education | Education is manual; execution is yours |

**Positioning:** every competitor automates *execution*. None of them sells
**an AI risk governor that can only refuse** — a layer whose incentive
alignment is provable (it cannot trade, so it cannot churn your account for
engagement). Our wedge: bring-your-own-broker (Alpaca first), wheel-only
determinism, AI veto, and a public decision journal as the trust artifact.

## Revenue model

1. **Core sub** $29/mo (annual $290): one broker connection, full wheel engine,
   AI risk governor, dashboard + journal.
2. **Pro** $79/mo: multi-account, spreads sleeve (defined-risk), custom risk
   mandates, longer journal history, API access.
3. ** introducing later, not at launch** — no payment-for-order-flow, no
   strategy marketplace cut. Alignment: we are paid to keep users *safe and
   compounding*, not to maximize volume. (An AI that can only say NO is also a
   pricing story: we can't monetize churn.)

## Why now

Broker APIs with options (Alpaca, Tradier, TradeStation) reached commodity
quality in 2024–25; LLM reasoning became cheap enough to run per-cycle as a
*supervisor* rather than a once-a-day analyst; and options volume just printed
its sixth straight record with retail as the marginal participant. The
infrastructure got cheap, the model got reliable enough for a narrow,
veto-only mandate, and the audience has never been larger.

## Sources

- Cboe — [The State of the Options Industry: 2025](https://www.cboe.com/insights/posts/the-state-of-the-options-industry-2025/)
- Cboe — [US Options Market Statistics](https://www.cboe.com/en/markets/us/options/market-statistics/)
- MEMX — [Retail Trading Insights](https://memx.com/insights/retail-trading-insights) (retail 30–37% of daily volume)
- Devexperts blog (retail 45–60% of options market)
- Pricing pages: [Option Alpha](https://optionalpha.com/pricing), [Composer](https://www.composer.trade/pricing), [Option Samurai](https://optionsamurai.com/), [tastytrade](https://tastytrade.com/pricing/)
