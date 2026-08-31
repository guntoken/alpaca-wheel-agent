# Social post #2 — dashboard + live numbers (post Senin 31 Agu; dashboard sudah live)

Angka diverifikasi 31 Agu pagi via fills asli Alpaca: 4 fill, premium kotor
$1.753 (13×$0,22 F + 2×$2,96 INTC + 2×$3,40 INTC + 1×$1,95 INTC), semuanya
malam Jumat 28 Agu — akhir pekan pasar tutup, jadi ini masih angka terkini.
Tag: @lablabai @AlpacaHQ · maks 5 link · posting pakai akun pemilik.

## X (thread, 280 chars/post)

**1/**
Day 4 of the Alpaca AI Trading Agents hackathon. Our options-wheel agent ran
25 live cycles unattended on @AlpacaHQ paper: 4 fills, $1,753 premium
collected, equity $99.7k/$100k. The twist? The AI can't place a single trade. 🦉
@lablabai

**2/**
Claude's only powers: read the market regime (RISK_ON / NEUTRAL / RISK_OFF)
and VETO a new entry. A deterministic engine does 100% of the trading on
hard rails — delta bands, vol-percentile gates, sector caps, drawdown stops.

**3/**
It can never force a trade and can never block an exit. De-risking is always
allowed. An LLM you can actually trust on a broker. alpaca-wheel-agent.streamlit.app

**4/**
Everything is journaled — every order with its reason, every regime read,
every bug it found in itself and fixed live on night 1. The dashboard shows
Claude's actual words each cycle. Paper only. guntoken/alpaca-wheel-agent

## X (single-post fallback, ≤280 chars)

An options-wheel agent whose AI can only say NO. 25 live cycles on Alpaca
paper: 4 fills, $1,753 premium. Deterministic engine trades; Claude reads the
regime and vetoes bad entries — never places, sizes, or forces a trade.
@lablabai @AlpacaHQ alpaca-wheel-agent.streamlit.app

## LinkedIn (~120 words)

Day 2 update from the Alpaca AI Trading Agents hackathon (lablab.ai × Alpaca):

Our autonomous options-wheel agent completed 25 live cycles on Alpaca's paper
trading — 4 fills, $1,753 premium collected, all without a human touching an
order.

The design decision I'm most proud of: the LLM (Claude) has no trade
execution power at all. It reads the market regime each cycle and it can veto
a new entry. That's it. A deterministic engine handles every trade on
hard-coded risk rails — delta bands, volatility-percentile gates, sector
concentration caps, a 3% daily drawdown stop, and a kill-switch file.

Every decision is journaled and public — including two bugs the agent's own
journal caught on night 1 and fixed the same night.

Dashboard (read-only, zero credentials): https://alpaca-wheel-agent.streamlit.app
Repo: github.com/guntoken/alpaca-wheel-agent

#AI #fintech #alpaca #hackathon @lablabai @AlpacaHQ
