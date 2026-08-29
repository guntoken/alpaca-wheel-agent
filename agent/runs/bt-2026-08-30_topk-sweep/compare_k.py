#!/usr/bin/env python3
"""Sweep Top-K: K=1 (varian C) vs K=2/3/5 vs SPY vs baseline, window sama.
Jalan dari agent/: uv run python runs/bt-2026-08-30_topk-sweep/compare_k.py
"""
import csv
import json
from collections import Counter
from pathlib import Path

SWEEP = Path(__file__).resolve().parent
CHAMP = SWEEP.parent / "bt-2026-08-29_weekly-champion"
BASE = SWEEP.parent / "bt-2026-08-29_wheel-csp-cc_1Day"
A, B = "2025-08-01", "2026-07-31"

k1 = json.loads((CHAMP / "summary.json").read_text())
rows = [("K=1 (varian C)", k1)]
for k in (2, 3, 5):
    p = SWEEP / f"k{k}_summary.json"
    if p.exists():
        rows.append((f"K={k}", json.loads(p.read_text())))
    else:
        print("(k%d belum selesai)" % k)


def seg(series):
    base = next((v for d, v in reversed(series) if d < A), series[0][1])
    return [v for d, v in series if A <= d <= B], base


def mdd(vals):
    peak, m = vals[0], 0.0
    for v in vals:
        peak = max(peak, v)
        m = max(m, (peak - v) / peak)
    return m * 100


print("=" * 78)
print("WINDOW 1 TAHUN  %s -> %s   (equal-weight budget per K)" % (A, B))
print("%-18s %9s %8s %8s %8s  %s" % ("", "return", "maxDD", "sharpe", "calmar", "champions"))
for nama, s in rows:
    st = s["strategy"]
    cal = st["cagr"] / max(st["max_drawdown"], 0.01)
    cnt = Counter(c["name"] for c in s.get("champions_picked", []))
    uniq = len(cnt)
    tot = sum(cnt.values())
    print("%-18s %+8.2f%% %7.2f%% %8.2f %8.2f  %d pilihan, %d nama unik"
          % (nama, st["total_return"], st["max_drawdown"], st["sharpe"], cal, tot, uniq))

spy_all = [(r["date"], float(r["spy_equity"]))
           for r in csv.DictReader(open(CHAMP / "benchmark_equity.csv"))]
base_v = next((v for d, v in reversed(spy_all) if d < A), spy_all[0][1])
segv = [v for d, v in spy_all if A <= d <= B]
print("%-18s %+8.2f%% %7.2f%% %8s %8s" %
      ("SPY buy-hold", (segv[-1] / base_v - 1) * 100, mdd(segv), "1.51", ""))

b_all = [(r["date"], float(r["equity"]))
         for r in csv.DictReader(open(BASE / "equity.csv"))]
bbase = next((v for d, v in reversed(b_all) if d < A), b_all[0][1])
bseg = [v for d, v in b_all if A <= d <= B]
print("%-18s %+8.2f%% %7.2f%%" % ("BASELINE wheel", (bseg[-1] / bbase - 1) * 100, mdd(bseg)))

print("\nCHAMPION per K (5 teratas):")
for nama, s in rows:
    cnt = Counter(c["name"] for c in s.get("champions_picked", []))
    top = ", ".join(f"{u} {n}x" for u, n in cnt.most_common(5))
    print("  %-14s %s" % (nama, top))

print("\nKESIMPULAN OTOMATIS:")
if len(rows) > 1:
    best = max(rows, key=lambda x: x[1]["strategy"]["total_return"])
    print("  return terbaik : %s (%+.2f%%)" % (best[0], best[1]["strategy"]["total_return"]))
    lo_dd = min(rows, key=lambda x: x[1]["strategy"]["max_drawdown"])
    print("  drawdown terkecil: %s (%.2f%%)" % (lo_dd[0], lo_dd[1]["strategy"]["max_drawdown"]))
print("  interpretasi tetap: 1 sampel per K; seleksi momentum menang di rezim momentum.")
