# Submission deck — build pipeline

`docs/slides.pdf` (10 pages, 16:9 1280×720) is assembled from per-slide PNGs:

1. `slides.html` — source deck (1280×720 per `.slide`, brand tokens, 2–3 sentences/slide)
2. charts: `equity.svg` + `premium.svg` generated from the published baseline run
   (`agent/runs/bt-2026-08-29_wheel-csp-cc_1Day/` + `agent/dashboard/backtest.json`);
   palette validated with the dataviz skill validator (gold #C98A00 / navy #3D6BA8)
3. inline SVGs into `slides.print.html` (agent-browser `open file://…`)
4. **screenshots — CRITICAL, do it exactly this way** (learned the hard way):
   ```
   agent-browser set viewport 1280 720          # viewport MUST equal slide size
   for i in 1..10:
     agent-browser eval "var s=document.querySelectorAll('.slide');
       for(var k=0;k<s.length;k++) s[k].style.display = k==i-1?'block':'none';
       window.scrollTo(0,0);"
     agent-browser screenshot slide-i.png       # VIEWPORT shot, not selector shot
   ```
   The daemon's *element* screenshot clips relative to the viewport without
   captureBeyondViewport — anything not at page-y 0 renders as the gap
   background (uniform #3a3d42, ~4KB files). Hiding sibling slides puts the
   target at the top, making a plain viewport shot exact.
5. **verify every PNG before assembly** (std>8, >20KB, 1280×720) — a silent
   blank-slide regression otherwise ships to the PDF (it did once)
6. `uv run --with img2pdf` → `../slides.pdf` (MediaBox 960×540pt = exact 16:9;
   chromium print-to-PDF ignores @page size, hence the screenshot route)

Cover 16:9 = `slide-1.png` → `docs/cover-16x9.png`. QA: DOM overflow check
(all slides scrollHeight == 720) + chart node counts + per-PNG pixel check.
