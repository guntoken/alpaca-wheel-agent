#!/usr/bin/env python3
"""Varian C (weekly champion, 1 thn) vs SPY vs baseline-wheel window sama.
Jalan dari agent/: uv run python runs/bt-2026-08-29_weekly-champion/compare_c.py
"""
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "bt-2026-08-29_wheel-csp-cc_1Day"

vc = json.loads((HERE / "summary.json").read_text())


def load(p):
    return [(r["date"], float(r["equity"])) for r in csv.DictReader(open(p))]


def seg(series, a, b):
    """base = titik terakhir SEBELUM a (biar return murni window), akhir <= b."""
    base = next((v for d, v in reversed(series) if d < a), series[0][1])
    return [v for d, v in series if a <= d <= b], base


def mdd(vals):
    peak, m = vals[0], 0.0
    for v in vals:
        peak = max(peak, v)
        m = max(m, (peak - v) / peak)
    return m * 100


A, B = "2025-08-01", "2026-07-31"
c_eq, c_base = seg(load(HERE / "equity.csv"), A, B)
spy_all = [(r["date"], float(r["spy_equity"]))
           for r in csv.DictReader(open(HERE / "benchmark_equity.csv"))]
s_eq, s_base = seg(spy_all, A, B)
b_eq, b_base = seg(load(BASE / "equity.csv"), A, B)

print("=" * 66)
print("WINDOW 1 TAHUN  %s -> %s" % (A, B))
for nama, vals, base in (("VARIANT C (champion)", c_eq, c_base),
                         ("BASELINE wheel", b_eq, b_base),
                         ("SPY buy-hold", s_eq, s_base)):
    ret = (vals[-1] / base - 1) * 100
    print("  %-22s %+7.2f%%   maxDD %5.2f%%   akhir $%s"
          % (nama, ret, mdd(vals), format(vals[-1], ",.0f")))

print("\nDARI summary.json varian C:")
print(" ", vc["strategy"])
print("  SPY:", vc["benchmark_spy"])
print("  aktivitas:", {k: v for k, v in vc["activity"].items() if v})
print("  gates:", {k: v for k, v in vc["gate_activity"].items() if v})

champs = vc.get("champions_picked", [])
cnt = Counter(c["name"] for c in champs)
print("\nCHAMPION AUDIT — %d pilihan dalam ~52 minggu:" % len(champs))
for nama, n in cnt.most_common():
    print("  %-6s %2dx" % (nama, n))
uniq = sorted(cnt)
print("  nama unik: %d dari 24 universe" % len(uniq))

# minggu aktif vs dry powder: CSP terjual
print("  CSP terjual %d => ~%d minggu aktif dari ~52 (sisanya pegang saham/CC atau dry)"
      % (vc["activity"]["csp_sold"], vc["activity"]["csp_sold"]))

print("\nPERINGATAN INTERPRETASI:")
print("  - 1 tahun = 1 sampel; bisa skill, bisa konsentrasi-beta, bisa luck.")
print("  - Bandingkan juga return nama-nama champion di window ini (skor seleksi")
print("    mengejar momentum; di tahun bull momentum-menang itu lumrah).")
