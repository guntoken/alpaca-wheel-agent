# alpaca-wheel-agent — agent operating manual

Proyek hackathon **Alpaca AI Trading Agents 2026** (lablab.ai × Alpaca, 28 Agu–4 Sep 2026).
Agent: wheel options otonom (CSP → covered call) + lapisan AI Claude headless. **PAPER ONLY.**

## ▶️ RESUME — baca dulu (state per 29 Agu ~20:00 WIB)
**Hari-2 SELESAI** (semua item lama beres): bug posisi-enum + multi-posisi + cap
per-underlying ditambal; adaptasi agentic-trading-system (regime deterministik, cap sektor,
re-pricing); panel makro Alpaca-native (GLD/VIXY/BTC/news → regime AI); **dashboard 4-tab
selesai & interaktif** (tema kuning-navy "Alpaca daylight", chart equity SVG halus dengan
hover crosshair + tooltip + sumbu waktu UTC, stress test, AI Brain, stepper wheel).
Hasil malam-1: 4 fill, **$1.753 premium**, 25 cycle live. Posisi kini: 4 short put
(INTC×3, F×1), equity ±$99.7k. Market tutup sampai Senin 20:30 WIB.

**Menunggu pemilik (satu-satunya bloker): DEPLOY** — share.streamlit.io → login GitHub →
New app → repo `guntoken/alpaca-wheel-agent`, branch main, file `agent/dashboard/app.py`
→ Deploy (tanpa secrets) → tulis URL hasilnya ke README bagian Dashboard.

**Sisa agenda (SUBMISSION_PLAN.md punya versi lengkap):**
- [ ] Minggu 30 Agu: **write-up satu halaman** (docs/WRITEUP.md: AI logic, risk gates,
      infra SDK+CLI+MCP — bahan: RESEARCH_NOTES.md) + slide PDF ≤10 hlm + cover 16:9 +
      riset business case (TAM/SAM/kompetitor) + draft post sosial #2
- [ ] Senin 31 Agu 20:15 WIB: **restart loop live** (kode baru aktif):
      `cd agent && setsid nohup env PYTHONUNBUFFERED=1 timeout 19800 ~/.local/bin/uv run wheel-agent loop --live --interval 900 >> loop.log 2>&1 < /dev/null & echo $! > loop.pid`
      Cek dulu `ps -p $(cat agent/loop.pid)` — JANGAN dua loop. Rutin tiap sesi malam:
      `uv run python -m agent.export` lalu commit+push (dashboard hosted ikut segar).
- [ ] Selasa 1 Sep: rekam video ≤5 mnt (struktur di SUBMISSION_PLAN) + **buat akun paper
      BARU $100.000** + ganti keys di `agent/.env` (+ env MCP bila perlu)
- [ ] Rabu 2 Sep: dry-run submission → **SUBMIT** (hard stop Kamis 3 Sep)

Bahasa kerja: **Indonesia**.

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
**Rencana lengkap + jadwal 7 hari + checklist deliverable resmi lablab ada di
[docs/SUBMISSION_PLAN.md](./docs/SUBMISSION_PLAN.md) — BACA ITU DULU saat resume.
Deadline: submit Rabu 2 Sep (hard stop Kamis 3 Sep, jangan tunggu 4 Sep).**
- [x] First live cycle (28 Agu 20:42 WIB, $1.753 premium)
- [x] Dashboard Streamlit lokal (4 tab: Command Center / Risk Lab / AI Brain /
      Execution Desk; stress test live; hero screenshot `docs/dashboard-hero.png`)
- [ ] **Deploy Streamlit Cloud (aksi pemilik)**: share.streamlit.com → login GitHub →
      New app → repo `guntoken/alpaca-wheel-agent`, branch main, file
      `agent/dashboard/app.py` → Deploy (tanpa secrets) → tulis URL ke README
- [ ] Rutin tiap sesi malam: `uv run python -m agent.export` lalu commit+push
      (agar dashboard hosted ikut segar), lalu restart loop live jelang 20:30 WIB
- [ ] Cadence cycle selama lomba: loop live tiap malam saat pasar buka (20:30–03:00 WIB);
      **Senin 31 Agu 20:15 WIB restart loop** (kode baru: enum fix, multi-posisi,
      cap sektor, regime overlay, re-pricing, Bollinger CC, vol gate)
- [ ] One-page write-up: AI logic, risk gates, infrastruktur Alpaca (SDK+CLI+MCP)
- [ ] Video ≤5 menit + slide PDF + cover 16:9 + deskripsi (pola lengkap di SUBMISSION_PLAN)
- [ ] Akun submission BARU $100k (~2 Sep) + ganti keys di `agent/.env`
- [ ] Post sosial X/LinkedIn tag @lablabai @AlpacaHQ (maks 5 link, kumpulkan URL-nya)

## Konteks desain singkat
Wheel murni: CSP delta±0.30 DTE 7–35 → take-profit 50% / roll di delta 0.60 → assignment →
CC delta±0.25 strike≥cost. AI Claude (`claude -p` headless) hanya bisa MENGETAT (regime
RISK_OFF/NEUTRAL memangkas budget, veto entry) — tidak pernah memaksa trade; buyback tidak
pernah di-veto. Cap: 5 underlying, 72% ekuitas (NEUTRAL=36%), drawdown stop harian 3%,
blackout earnings (config kosong — INTC 22 Okt, MU 30 Sep, aman untuk window lomba).
Arsitektur & bug yang sudah diperbaiki: lihat README.md bagian "Status setup".
