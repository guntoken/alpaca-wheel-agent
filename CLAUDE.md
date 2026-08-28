# alpaca-wheel-agent — agent operating manual

Proyek hackathon **Alpaca AI Trading Agents 2026** (lablab.ai × Alpaca, 28 Agu–4 Sep 2026).
Agent: wheel options otonom (CSP → covered call) + lapisan AI Claude headless. **PAPER ONLY.**

## ▶️ RESUME — baca dulu (state per 28 Agu ~21:00 WIB)
**Malam pertama SUDAH terjadi** (28 Agu): cycle live perdana jam 20:42 — AI regime RISK_ON,
3 order CSP terkirim (INTC $86/25Sep qty2, T $25/18Sep qty7, F $13.50/18Sep qty13; limit di
mid, status terakhir: open menunggu fill). Order ke-4 (KO) sempat ditolak broker (options
buying power habis) → **sudah dipatch**: cycle kini menjepit budget ke `options_buying_power`
aktual akun. Loop mandiri jalan sampai ±03:00 WIB lalu mati otomatis (timeout), market tutup.

**Saat resume pagi (market TUTUP sampai 20:30 WIB):**
1. Rekap semalam: `tail -50 agent/loop.log`, `cd agent && uv run wheel-agent status`,
   `tail -5 agent/journal.jsonl` → laporkan ke pemilik (Bahasa Indonesia): order terisi/tidak,
   premium masuk, posisi short put, P&L, peristiwa (TP/roll/assignment).
2. Commit+push jurnal semalam ke repo.
3. Penyempurnaan hari-2 (pasar tutup, waktu bagus): (a) **re-pricing order menganggur** —
   cancel/replace ke bid/ask bila entry belum terisi >3 cycle; (b) tulis **one-page write-up**
   (AI logic, risk gates, infra SDK+CLI+MCP) → `docs/WRITEUP.md`; (c) draft post sosial #2.
4. Menjelang 20:30 WIB: jalankan ulang loop live:
   `cd agent && setsid nohup env PYTHONUNBUFFERED=1 timeout 19800 ~/.local/bin/uv run wheel-agent loop --live --interval 900 >> loop.log 2>&1 < /dev/null & echo $! > loop.pid`
   (timeout 19800s ≈ mati jam 03:00 WIB). JANGAN jalankan dua loop sekaligus — cek
   `ps -p $(cat agent/loop.pid)` dulu.

Bahasa kerja: **Indonesia**. Pemilik istirahat malam 28 Agu, kembali pagi 29 Agu.

## Perintah (dari folder `agent/`)
| Perintah | Fungsi |
|---|---|
| `uv run wheel-agent status` | jam pasar, ekuitas, posisi, order terbuka |
| `uv run wheel-agent cycle --force` | satu cycle DRY-RUN (force saat pasar tutup) |
| `uv run wheel-agent cycle --live` | satu cycle LIVE (submit order paper) |
| `uv run wheel-agent loop --live --interval 300` | loop tiap 5 menit selama pasar buka |
| `uv run wheel-agent cancel-orders --live` | batalkan semua order wheel terbuka |

## Aturan (jangan dilanggar)
1. **PAPER ONLY** — `--live` = order paper sungguhan di akun paper DEV, bukan uang riil.
2. Default semua perintah adalah dry-run; hanya `--live` yang mensubmit.
3. **Jangan pernah commit `agent/.env`** atau keys apa pun (sudah di `.gitignore`, terverifikasi).
4. Repo publik untuk lablab: `git@github.com:guntoken/alpaca-wheel-agent.git` — push jurnal & progres tiap malam.
5. Akun submission (BARU, $100.000) dibuat menjelang 4 Sep — akun dev sekarang BUKAN akun submission.
6. Kill-switch: buat file `agent/KILL` → agent berhenti mensubmit apa pun.
7. `alpaca doctor` sebelum sesi trading via CLI; endpoint wajib `https://paper-api.alpaca.markets`.

## Infrastruktur yang SUDAH siap (jangan di-setup ulang)
- `uv` + venv di `agent/` (alpaca-py), keys paper di `agent/.env` (perm 600)
- Alpaca CLI 0.0.13 — login profile `paper` tersimpan di `~/.config/alpaca/`
- MCP server `alpaca` terpasang **user-scope** (aktif di sesi mana pun) — env keys asli, `ALPACA_PAPER_TRADE=true`
- 4 skill `alpaca-trading-*` terpasang **user-scope** di `~/.claude/skills/`
- ⚠️ **DNS pin**: `*.alpaca.markets` diblokir DNS ISP (Kominfo). `/etc/hosts` sudah dipin:
  `paper-api.alpaca.markets → 35.194.67.18`, `data.alpaca.markets → 34.86.145.125`.
  Kalau API mendadak gagal: resolve ulang via DoH (`curl -H 'accept: application/dns-json' 'https://1.1.1.1/dns-query?name=paper-api.alpaca.markets&type=A'`) lalu perbarui `/etc/hosts` (butuh sudo, minta pemilik).
- Jam pasar: 09:30–16:00 ET = **20:30–03:00 WIB** (Sen–Jum)

## Kerjaan tersisa (checklist submission)
- [ ] **First live cycle** + lapor + push jurnal ← LANGKAH BERIKUTNYA
- [ ] Cadence cycle selama lomba (29 Agu–4 Sep): tiap ~5 menit saat pasar buka
- [ ] One-page write-up: AI logic, risk gates, infrastruktur Alpaca (SDK+CLI+MCP)
- [ ] Akun submission BARU $100k (menjelang 4 Sep) + ganti keys di `agent/.env`
- [ ] Post sosial X/LinkedIn tag @lablabai @AlpacaHQ (maks 5 link, kumpulkan URL-nya)

## Konteks desain singkat
Wheel murni: CSP delta±0.30 DTE 7–35 → take-profit 50% / roll di delta 0.60 → assignment →
CC delta±0.25 strike≥cost. AI Claude (`claude -p` headless) hanya bisa MENGETAT (regime
RISK_OFF/NEUTRAL memangkas budget, veto entry) — tidak pernah memaksa trade; buyback tidak
pernah di-veto. Cap: 5 underlying, 72% ekuitas (NEUTRAL=36%), drawdown stop harian 3%,
blackout earnings (config kosong — INTC 22 Okt, MU 30 Sep, aman untuk window lomba).
Arsitektur & bug yang sudah diperbaiki: lihat README.md bagian "Status setup".
