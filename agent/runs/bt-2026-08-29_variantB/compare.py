#!/usr/bin/env python3
"""Perbandingan: varian B vs baseline terbitan vs SPY buy-hold.
Jalan dari folder run varian: uv run python runs/bt-2026-08-29_variantB/compare.py
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "bt-2026-08-29_wheel-csp-cc_1Day"

vb = json.loads((HERE / "summary.json").read_text())
bl = json.loads((BASE / "summary.json").read_text())


def dd(seg):
    peak, mdd = seg[0], 0.0
    for v in seg:
        peak = max(peak, v)
        mdd = max(mdd, (peak - v) / peak)
    return mdd * 100


def load(p):
    return [(r["date"], float(r["equity"])) for r in csv.DictReader(open(p))]


veq, beq = load(HERE / "equity.csv"), load(BASE / "equity.csv")
vbe = [(r["date"], float(r["spy_equity"]))
       for r in csv.DictReader(open(HERE / "benchmark_equity.csv"))]
vmap = dict(veq)
bmap = dict(beq)

SPLIT = "2025-06-30"
print("=" * 74)
print("FULL WINDOW  %s -> %s" % (vb["window"]["start"], vb["window"]["end"]))
print("%-26s %12s %12s %12s" % ("", "VARIANT B", "BASELINE", "SPY"))
for label, key in (("total return %", "total_return"), ("CAGR %", "cagr"),
                   ("max drawdown %", "max_drawdown"), ("sharpe", "sharpe")):
    print("%-26s %12s %12s %12s" % (label, vb["strategy"][key], bl["strategy"][key],
                                    vb["benchmark_spy"][key]))

for nama, seg_v, seg_b in (("IS  (->2025-06)", veq, beq), ("OOS (2025-07->)", veq, beq)):
    sv = [v for d, v in seg_v if d <= SPLIT] if nama.startswith("IS") else \
         [v for d, v in seg_v if d >= SPLIT]
    sb = [v for d, v in seg_b if d <= SPLIT] if nama.startswith("IS") else \
         [v for d, v in seg_b if d >= SPLIT]
    print("\n%s  variant %+.1f%% (DD %.1f%%)  |  baseline %+.1f%% (DD %.1f%%)"
          % (nama, (sv[-1]/sv[0]-1)*100, dd(sv), (sb[-1]/sb[0]-1)*100, dd(sb)))

print("\nWALK-FORWARD (dari summary.json varian):")
for k, seg in vb["walk_forward"]["segments"].items():
    print("  %-4s strategy %+7.2f%% DD %5.2f%% sharpe %5.2f | SPY %+7.2f%% DD %5.2f%%"
          % (k, seg["strategy"]["total_return"], seg["strategy"]["max_drawdown"],
             seg["strategy"]["sharpe"], seg["benchmark_spy"]["total_return"],
             seg["benchmark_spy"]["max_drawdown"]))

print("\nAKTIVITAS (variant vs baseline):")
for k in ("csp_sold", "cc_sold", "assignments", "called_away", "expired_worthless"):
    print("  %-16s %4d vs %4d" % (k, vb["activity"][k], bl["activity"][k]))
print("  premium kotor    $%s vs $%s" % (format(vb["premiums_collected_gross"], ",.0f"),
                                          format(bl["premiums_collected_gross"], ",.0f")))
print("  bunga kas        $%s" % format(vb["cash_interest_accrued"], ",.0f"))
print("  gate quality     %dx (SMA200 blokir)" % vb["gate_activity"].get("quality", 0))

print("\nEPISODE STRES (DD varian | baseline | SPY):")
for a, b, lbl in (("2024-07-01", "2024-09-30", "VIX spike Agu-2024"),
                  ("2025-02-01", "2025-05-31", "Tarif crash Apr-2025"),
                  ("2026-01-01", "2026-04-30", "Tekanan awal 2026")):
    vseg = [v for d, v in veq if a <= d <= b]
    bseg = [v for d, v in beq if a <= d <= b]
    sseg = [v for d, v in vbe if a <= d <= b]
    print("  %-22s %5.1f%% | %5.1f%% | %5.1f%%" % (lbl, dd(vseg), dd(bseg), dd(sseg)))
