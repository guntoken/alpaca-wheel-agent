# Alpaca AI Trading Agents Hackathon 2026

Proyek submission untuk hackathon lablab.ai × Alpaca (28 Agu – 4 Sep 2026).

**PENTING — akun:**
- Development: pakai akun paper bebas.
- Submission: **wajib akun paper BARU, khusus hackathon, saldo awal $100.000** (dibuat menjelang submission, jangan dipakai dev).
- Semua yang di sini PAPER ONLY. Tidak ada live trading.

## Struktur
- `agent/` — kode submission (agent options otonom) — dibangun dari sini
  - `src/agent/`: `config` (knob + gates) · `alpaca_client` (wrapper alpaca-py) · `risk` (kill-switch, drawdown stop, blackout, cap) · `wheel` (state machine CSP→CC) · `ai` (Claude headless: regime + veto) · `journal` (JSONL + state) · `cycle` (orkestrator) · `main` (CLI)
  - CLI: `uv run wheel-agent status | cycle [--live --force --no-ai] | loop [--live] | cancel-orders`
  - **Default DRY-RUN** — order hanya betul-betul terkirim dengan `--live`
  - Jurnal keputusan: `agent/journal.jsonl` (tiap cycle: regime AI, intent, order, error)
- `repos/` — repo referensi (dipelajari, bukan untuk dimodifikasi):
  - `options-wheel/` — template RESMI Alpaca untuk strategi Wheel (CSP + covered calls), Apache-2.0 → basis strategi
  - `alpaca-skills/` — SKILL.md resmi Alpaca untuk AI agent (juga terpasang di `~/.claude/skills/`)
  - `alpaca-mcp-server/` — MCP server resmi Alpaca (syarat lomba: MCP atau CLI)
  - `GaussWorldTrader/` — referensi arsitektur multi-agent (MIT)
  - `cemarsh/agentic-trading-system` — TIDAK di-clone (tanpa lisensi); dipelajari idenya saja via GitHub

## Syarat inti lomba (checklist)
- [ ] Autonomous AI trading agent pakai Alpaca Trading API
- [ ] Memakai MCP server ATAU CLI Alpaca (target: keduanya)
- [ ] Strategi wajib melibatkan OPTIONS (rencana: Wheel + lapisan keputusan AI)
- [ ] Akun submission baru, $100.000
- [ ] One-page write-up: AI logic, risk gates, infrastruktur Alpaca
- [ ] (Ekstra) maks. 5 link post X/LinkedIn, tag @lablabai & @AlpacaHQ

## Kredensial
- JANGAN paste API key ke chat. Simpan di `agent/.env` (lihat `.env.example`).
- Paper keys saja. Live key tidak pernah dibagikan.
- Alpaca CLI pakai OAuth untuk paper — tanpa API key.

## Status setup (28 Agu 2026 — 17:15 WIB)
Sudah siap & TERVERIFIKASI:
- ✅ `uv` 0.12.7 + proyek `agent/` dengan `alpaca-py` + `python-dotenv`; keys paper di `agent/.env` (perm 600, ter-ignore git)
- ✅ Alpaca CLI 0.0.13 — **sudah login** profile `paper`; `alpaca doctor` semua lulus (Trading & Data connected, endpoint paper terkonfirmasi)
- ✅ MCP server `alpaca` user-scope dengan keys asli — Connected
- ✅ 4 skill Alpaca terpasang di `~/.claude/skills/`
- ✅ Akun: ACTIVE, equity $100.000, **options level 3** (level efektif — CSP, covered call, long options, DAN spreads semua boleh)
- ✅ Data options OK: contracts + chain (quote/greeks/trade) teruji
- ⚠️ **Blokir jaringan**: domain `*.alpaca.markets` di-DNS-poison ke laman blokir Kominfo oleh ISP. Solusinya pin IP di `/etc/hosts` (2 baris, mudah dibatalkan). Kalau API tiba-tiba gagal: IP mungkin berubah — resolve ulang via DoH `curl -H 'accept: application/dns-json' 'https://1.1.1.1/dns-query?name=paper-api.alpaca.markets&type=A'` lalu perbarui `/etc/hosts`. Endpoint LIVE (`api.alpaca.markets`) sengaja TIDAK dipin — tetap tidak tersambuh.
- 🕐 Pasar buka 09:30 ET (= 20:30 WIB)

Menunggu pemilik:
- ⏳ Menjelang submission: akun paper BARU khusus lomba, saldo $100.000
- ⏳ (Ekstra) post X/LinkedIn tag @lablabai & @AlpacaHQ

Perintah penting: `alpaca doctor` (wajib paper endpoint `https://paper-api.alpaca.markets` sebelum order apa pun), `alpaca clock`, `alpaca account get`. Aturan CLI: JANGAN pakai flag `-p/--profile`; gunakan env `ALPACA_PROFILE`.
