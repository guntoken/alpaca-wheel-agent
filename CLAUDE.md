# alpaca-wheel-agent — agent operating manual

Proyek hackathon **Alpaca AI Trading Agents 2026** (lablab.ai × Alpaca, 28 Agu–4 Sep 2026).
Agent: wheel options otonom (CSP → covered call) + lapisan AI Claude headless. **PAPER ONLY.**

## ▶️ RESUME — baca dulu (state per 28 Agu 18:42 WIB)
- **Loop LIVE mandiri sedang berjalan**, terlepas dari sesi Claude: PID di `agent/loop.pid`,
  log `agent/loop.log`, interval 15 menit, auto-mati ±03:12 WIB (setelah close). Cycle live
  pertama terjadi otomatis begitu market open (20:30 WIB) — TIDAK perlu dijalankan manual.
- Saat resume: **JANGAN jalankan loop/cycle kedua** (bisa tabrakan). Cukup periksa hasilnya:
  `tail -30 agent/loop.log`, `cd agent && uv run wheel-agent status`, `tail -3 agent/journal.jsonl`,
  lalu laporkan ke pemilik (Bahasa Indonesia): regime AI, posisi/order terkirim, P&L, error.
  Setelah itu commit+push jurnal ke repo.
- Hentikan loop: `kill $(cat agent/loop.pid)`.
- Pemilik kembali ~21:00+ WIB. Bahasa kerja: **Indonesia**.

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
