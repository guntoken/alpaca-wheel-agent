# Research Notes — sources studied and what we adopted

Every source below was analyzed against the engine and a deliberate adopt/reject
decision recorded. Date: 28–29 Aug 2026 (hackathon days 1–2).

## 1. Alpaca official options-wheel tutorial (alpaca.markets/learn)
**Confirmed our parameters**: CSP delta band 0.18–0.42, TP at 50% of credit,
roll at 2× initial delta (=0.60), DTE 7–35.
**Adopted**: CC strike must clear SMA20+2σ upper Bollinger Band; OI threshold 200;
CC sizing on `qty_available` (net of committed shares).
**Rejected (we're stricter)**: market orders (we use marketable limits);
self-computed Black-Scholes greeks (we use exchange OPRA greeks); first-match
contract pick (we pick best-in-band); single underlying (we run a capped portfolio).

## 2. Rustamov et al. 2024, "A New Approach to Build a Successful Straddle
Strategy: The Analytical Option Navigator", Risks 12(11):1131
Percentile-ranks dollar-volatility bars (35-day OHP vs 250-day history); buys
straddles at LOW percentiles (compressed vol = cheap options).
**Adopted (inverted for premium selling)**: `vol_dollar_percentile()` gate — new
CSPs are skipped when the underlying's vol-in-currency percentile is below the
40th percentile of its own history. Existing positions unaffected.
**Rejected**: the straddle side itself (we committed to wheel-only for the event);
95% CI envelope (complexity not worth it for a one-week run).

## 3. Practitioner threads (r/ActiveOptionTraders "The Wheel Explained" by
ScottishTrader; r/Optionswheel "wheel for a living" & "leverage with the wheel")
**Adopted**:
- **Roll-for-credit discipline**: a challenged put is only bought back when a
  fresh CSP's bid covers the closing ask (net credit). No credit roll available
  -> hold to assignment and work it off with covered calls. (Their line: "if you
  can't roll for a credit, let the CSP play out — closing early causes a major loss.")
- **Vol awareness for the regime read**: SPY dollar-vol percentile is now part of
  the market summary fed to the AI ("always know what vol is doing").
**Affirmed (already our design)**: diversification caps; earnings blackout;
"goal is premium, not assignment"; boring-but-repeatable beats sexy-but-fragile.
**Rejected**:
- **Leverage** (2:1–4:1 margin): thread consensus is that diversification and
  early-exit "both jam shut in the same moment" in a crash. We stay unleveraged;
  the broker's options buying power is a hard wall we clamp to.
- 5%-per-stock sizing: tuned for living-income accounts; too conservative for a
  one-week judged run on $100k (our 18%/name, 5 names, 72% ceiling, halved in
  NEUTRAL, zero in RISK_OFF).

## 4. Medium: "Wheel strategy is the ultimate trading cheat code" (2020)
Cites CBOE and Dorean (FSU, 1996–2006) studies that put-selling beat other
option strategies. **Adopted as write-up citation only.** (The "80% expire
worthless" stat is pop shorthand — we cite the studies, not the meme.)

## 5. Medium: Project Theta — wheel profitability, sub-$10 lists, spreads 101
- *Profitability piece*: wheel is short-vol; avoid catalysts and explosive small
  caps; flat markets are the sweet spot. **Already enforced** (earnings blackout,
  liquidity/OI filters, large-liquid universe).
- *Sub-$10 stock list (Sep 2020)*: **rejected outright** — six years stale;
  several names fundamentally changed (GE split, MVIS dilution). Stale ticker
  lists are a trap; our engine sizes off live prices instead.
- *Debit spreads / put credit spreads primers*: solid mechanics, **not adopted** —
  different strategy family than the wheel we committed to. Parked in the
  roadmap as a possible defined-risk sleeve (level-3 account permits it).

## 6. github.com/LaurentiuGabriel/greek-alpaca ("GreekFlow")
React/TS dashboard: portfolio value, equity curve, per-position Greeks, sector
exposure, algorithmic hedging recommendations, runtime credentials.
**Adopted as design reference** for our dashboard (panel layout ideas: equity
curve, positions with P&L, Greeks, exposure). **Code not reused** — the repo
carries no open-source license ("private"), so ideas only, per our no-unlicensed-copy
rule. Our dashboard stays Python/Streamlit, journal-fed, zero credentials.

## Net effect on the engine (all live from the day-2 loop restart)
1. CC strikes clear max(cost basis, SMA20+2σ) — official guidance
2. OI floor 200; CC sizing on qty_available
3. New-CSP vol-percentile gate ≥ 40th pct (research-derived)
4. Roll-for-credit-only management (practitioner discipline)
5. AI regime sees SPY vol percentile alongside SMA context
