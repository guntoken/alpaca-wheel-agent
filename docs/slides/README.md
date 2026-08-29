# Submission deck — build pipeline

`docs/slides.pdf` (10 pages, 16:9 1280×720) is assembled from per-slide PNGs:

1. `slides.html` — source deck (1280×720 per `.slide`, brand tokens, 2–3 sentences/slide)
2. charts: `equity.svg` + `premium.svg` generated from the published baseline run
   (`agent/runs/bt-2026-08-29_wheel-csp-cc_1Day/` + `agent/dashboard/backtest.json`);
   palette validated with the dataviz skill validator (gold #C98A00 / navy #3D6BA8)
3. inline SVGs → `slides.print.html`, open in headless chromium (agent-browser)
4. screenshot each `body > div.slide:nth-of-type(N)` → `slide-N.png` (1280×720)
5. `uv run --with img2pdf` → `../slides.pdf` (MediaBox 960×540pt = exact 16:9;
   chromium print-to-PDF ignores @page size, hence the screenshot route)

Cover 16:9 = `slide-1.png` → `docs/cover-16x9.png`. QA: DOM overflow check
(all slides scrollHeight == 720, no clipped elements) + chart node counts.
