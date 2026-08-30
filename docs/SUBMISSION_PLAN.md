# Submission Plan — How We Win This

Working document built from (1) lablab.ai's official submission guide, (2) a
"how to win an AI hackathon" playbook, (3) patterns reverse-engineered from a
real lablab winner (evo.ninja). Updated 28 Aug 2026 night.

## Hard deadline & account rules
- **Submit EARLY: target Wed 2 Sep, hard stop Thu 3 Sep** — never ride into 4 Sep.
- ⚠️ **UPDATE 31 Agu — akun baru = SYARAT ELIGIBILITAS** (halaman event):
  "create a brand-new Alpaca paper trading account dedicated to this
  hackathon. Projects run on an existing or reused account will not be
  eligible for judging." Balance awal $100.000. Plus field wajib di form:
  **Alpaca account ID** (juri menilai P&L dari akun itu). Karena P&L adalah
  kriteria penilaian #1 → **flip akun Senin 31 Agu malam** (bukan Selasa):
  loop restart Senin 20:15 WIB langsung di akun judged → 3 malam trading
  (Sen/Sel/Rab) + Kamis sampai end-of-submissions, loop tetap jalan.
  Dev account berhenti dipakai saat flip (jangan dihapus — bukti).

### Runbook flip akun paper (diverifikasi 30 Agu — mekanisme Alpaca)
Dashboard app.alpaca.markets → paper section → **"Open New Paper Account"**
(satu login boleh punya sampai 3 akun paper, masing-masing API keys sendiri;
tidak perlu email baru). JANGAN hapus akun dev (tetap sebagai bukti/backup).
1. Buat akun paper baru, starting balance $100.000, generate key pair baru.
2. `alpaca doctor`-class sanity: pastikan endpoint tetap `https://paper-api.alpaca.markets`.
3. Update `agent/.env` (perm 600) + env MCP user-scope bila dipakai sesi malam itu.
4. Arsipkan jejak dev supaya data.json run penilaian bersih:
   `git mv agent/journal.jsonl agent/journal-dev.jsonl` (atau salin + kosongkan),
   pertimbangkan reset `agent/state.json`. Loop berikutnya mulai dari $100k flat.
5. `uv run wheel-agent status` → equity $100.000, 0 posisi → baru `cycle --live`.
6. Catat di README/judul run bahwa judged window mulai tanggal flip.

### Strategi form lablab (diverifikasi 30 Agu)
- lablab punya **draft**: buka draft submission lebih awal, paste semua field
  dari SUBMISSION_FORM.md kecuali URL video; draft belum dihitung submission.
- Submit final Rabu 2 Sep ≥6 jam sebelum deadline 4 Sep → bonus poin
  "Early Submission" +25 (poin leaderboard, bukan skor juri) dan buffer
  1 hari penuh sebelum hard-stop Kamis.

## Required deliverables (from the official guide)
| # | Deliverable | Status | Owner/notes |
|---|---|---|---|
| 1 | Project title (clear, descriptive) | ✅ final | "OWL Agent — an autonomous options wheel whose AI can only say NO" ([SUBMISSION_FORM](SUBMISSION_FORM.md)) |
| 2 | Short description ≤255 chars | ✅ final | 244 chars, paste-ready (SUBMISSION_FORM) |
| 3 | Long description ≥100 words (problem/solution/audience/unique) | ✅ final | 195 kata, paste-ready (SUBMISSION_FORM) |
| 4 | Technology & category tags | ✅ picked | AI Agents / Fintech / Trading / Python / API (SUBMISSION_FORM) |
| 5 | Cover image PNG/JPG 16:9 | ✅ done | `docs/cover-16x9.png` (headline K=3) |
| 6 | Video ≤5 min MP4 (intro → slides → demo) | ☐ rekam 1 Sep | script + shot list + checklist: `VIDEO_SCRIPT.md`; notes: `SLIDE_NOTES.md` |
| 7 | Slide deck PDF (≤10 pages, 2–3 sentences/slide) | ✅ done | `docs/slides.pdf` 10 hlm 16:9 EN |
| 8 | Public GitHub repo (real commits across event window) | ✅ live | guntoken/alpaca-wheel-agent — keep daily commits |
| 9 | **Application URL (interactive)** | ✅ live | **https://alpaca-wheel-agent.streamlit.app** (DOM-verified 6 tab) |

Note: "IBM Bob report" in the guide is template boilerplate from an IBM hackathon —
our equivalent is the agent-native paper trail: CLAUDE.md operating manual, commit
history, and the decision journal (`agent/journal.jsonl`).

## The gap we must close: demo URL (Streamlit dashboard)
Judges need something clickable. Plan (no credentials in the cloud):
1. Loop already logs every cycle to `agent/journal.jsonl` (equity, regime, orders, errors).
2. Add a small exporter: agent writes `dashboard/data.json` (equity curve, open
   positions, order history, latest AI regime + reasons, P&L) each cycle — committed
   to the repo by the nightly push.
3. Streamlit app (`dashboard/`) reads `data.json` — READ-ONLY, zero API keys.
4. Deploy free on **Streamlit Community Cloud** from this GitHub repo.
   Golden path: equity curve → current wheel positions → AI regime timeline →
   decision journal table. Fix only bugs on that path.

## Video script (5 min, per winning structure)
- 0:00–0:30 problem: retail options income is manual, emotional, error-prone
- 0:30–2:30 LIVE demo: dashboard + one cycle running (engine picks CSP, Claude
  reads regime/vetoes, order lands on Alpaca paper, journal records it)
- 2:30–4:00 business case: who pays, TAM/SAM, revenue model
- 4:00–5:00 solo builder + roadmap (spreads sleeve, multi-agent debate, live-ready rails)

## Judging rubric → our mapping (kriteria RESMI event, urutan asli — P&L no. 1)
| Criterion | What we show |
|---|---|
| **P&L Performance** | akun judged baru $100k berjalan otonom sejak Senin malam (maksimalkan malam trading sebelum 4 Sep); premium terkumpul + drawdown terkendali; backtest 2,5 th sebagai bukti aturan yang sama |
| **Technology Implementation** | **real** autonomous agent, live on Alpaca paper since day 1; SDK + CLI + MCP semua terpakai; AI meaningfully integrated (regime read + veto-only risk overlay — bukan chatbot wrapper) |
| **Creativity & Originality** | "an AI that can only say no" — LLM sebagai risk governor di atas rel deterministik; decision journal publik termasuk bug yang ditemukan & diperbaiki live |
| **Presentation & Execution** | dashboard-first README (hero screenshot sebelum install), video 5 mnt, slide PDF, write-up 1 halaman |

## README upgrade (copy evo.ninja patterns)
Hero screenshot first → one-line tagline → quick start split (demo URL vs source)
→ architecture diagram (numbered cycle loop) → use-case table → honest build log.
Installation LAST, not first.

## 7-day battle plan
| Day | Focus |
|---|---|
| 29 Aug (Sat) | order re-pricing fix; dashboard data exporter + Streamlit MVP locally; collect first equity curve |
| 30 Aug (Sun) | dashboard golden path polish; deploy Streamlit Cloud; README restructure |
| 31 Aug (Mon) | WRITEUP.md (one-pager: AI logic, risk gates, Alpaca infra); business-case research (TAM/SAM/competitors: Composer, Option Alpha, Tastytrade) |
| 1 Sep (Tue) | slides PDF + cover image + record video; social post #2 |
| 2 Sep (Wed) | **create fresh $100k account, flip keys, judged run starts**; submission dry-run (every field filled) |
| 3 Sep (Thu) | **SUBMIT** with buffer; prep judge Q&A; final social post w/ results |
| 4 Sep (Fri) | slack; watch for judge questions |

## Anti-patterns to avoid (from the playbook)
- Don't add features after video is recorded — polish the golden path only.
- Don't bury the demo in the video — first 30 s must state the value.
- Don't wait until 4 Sep to submit.
- Notebook must stay awake while the loop trades (Kominfo DNS pin note in CLAUDE.md).
