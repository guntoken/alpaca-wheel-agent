# Social post #2 — judged run night 1 (post Senin 31 Agu malam; dashboard sudah live)

Angka diverifikasi 31 Agu ~22:45 WIB via fills asli API akun judged (PA3F0TJJ7C7W,
dibuat 31 Agu 12:04 WIB): INTC260904P 2@1,10 + PFE260904P 6@0,18 = **$328 premium
kotor**, SOFI 17P×5 re-priced & working, BABA tergeser cap kolateral 72%.
Semua CSP expiry tepat Jum 4 Sep (sprint window resmi, diungkap jujur).
Tag: @lablabai @AlpacaHQ · maks 5 link (dipakai 2: dashboard + repo) ·
posting pakai akun pemilik.

## X (thread, 280 chars/post)

**1/**
Day 4 of the Alpaca AI Trading Agents hackathon — the official P&L window just
opened. Our dev account didn't meet the rules, so today we opened a brand-new
$100k paper account. Night 1 of the judged run is live. 🦉 @lablabai @AlpacaHQ

**2/**
The engine sells cash-secured puts that expire exactly Fri Sep 4. The window
scores equity at Thursday's close, so we want premium that becomes cash inside
it. That choice is disclosed in the public journal — we play the window openly.

**3/**
Tonight: 4 puts across INTC, PFE, BABA, SOFI — all picked by the deterministic
engine. Two filled within minutes ($328 premium). Claude read the regime
(RISK_ON) and approved entries. It has no other trade power.

**4/**
Because the LLM can still only say NO. Veto-only by design; exits can never be
blocked. Every order + reason journaled: guntoken/alpaca-wheel-agent
Live: alpaca-wheel-agent.streamlit.app
3 nights to go.

## X (single-post fallback, ≤280 chars)

Night 1 of the judged run in the Alpaca AI hackathon: a brand-new $100k paper
account, 4 cash-secured puts expiring exactly Fri Sep 4, 2 filled fast — $328
premium. Claude's only power is veto; the deterministic engine trades.
@lablabai @AlpacaHQ alpaca-wheel-agent.streamlit.app

## LinkedIn (low-key, disegarkan Rabu 2 Sep malam — angka malam-3; versi lama malam-1 di bawah)

Progress note from the Alpaca AI Trading Agents hackathon (lablab.ai × Alpaca).

Night 3 of the judged run on a fresh $100k paper account: the deterministic
wheel engine has collected $872 gross premium on cash-secured puts and closed
its first position at +$72 realized. The Claude layer still cannot place a
trade — its only power is vetoing an entry.

Dashboard: https://alpaca-wheel-agent.streamlit.app
Repo: github.com/guntoken/alpaca-wheel-agent

@lablabai @AlpacaHQ

### Versi lama (malam-1, sudah basi — jangan dipakai)

Day 4 progress note from the Alpaca AI Trading Agents hackathon (lablab.ai × Alpaca).

Tonight the paper-trading options-wheel agent began its judged run on a fresh
$100k account: four cash-secured puts expiring Fri Sep 4, two filled so far
($328 premium). The LLM layer remains veto-only; a deterministic engine
handles all order decisions.

Dashboard (read-only): https://alpaca-wheel-agent.streamlit.app
Repo: github.com/guntoken/alpaca-wheel-agent

@lablabai @AlpacaHQ
