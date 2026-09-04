"""autoexport — jaga dashboard hosted tetap segar selama window skor resmi.

Tiap ~25 menit sepanjang sesi pasar (20:30-03:00 WIB) malam Sel/Rab/Kam
(plus sisa sesi Senin), jalankan `python -m agent.export` lalu commit+push
data.json/journal/state. Tick penutup 02:57 tiap malam menangkap kondisi
jelang close. Berhenti sendiri setelah Sab 5 Sep 03:05 WIB (malam pasca-window).

Jalankan:  setsid nohup ~/.local/bin/uv run python autoexport.py \
             >> autoexport.log 2>&1 < /dev/null & echo $! > autoexport.pid
Hentikan:  kill $(cat autoexport.pid)
"""
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

AGENT = Path(__file__).resolve().parent
WIB = timezone(timedelta(hours=7))
END = datetime(2026, 9, 5, 3, 5, tzinfo=WIB)          # malam Jum 4 Sep (pasca-window) selesai
FILES = ["dashboard/data.json", "journal.jsonl", "state.json"]


def log(msg):
    print(f"{datetime.now(WIB):%m-%d %H:%M:%S} {msg}", flush=True)


def in_session(now):
    """Sesi = 20:25-03:02 WIB; antar-malam (03:02-20:25) dilewati."""
    h = now.hour + now.minute / 60
    return h >= 20.42 or h < 3.03


def next_tick(now):
    """Tick berikutnya: +25 menit, atau tepat 02:57 sebagai penutup malam."""
    t = now.replace(second=0, microsecond=0) + timedelta(minutes=25)
    if now.hour < 3 and t.hour >= 3 and (t.hour, t.minute) > (3, 0):
        t = t.replace(hour=2, minute=57)
    return t


def export_and_push():
    r = subprocess.run([sys.executable, "-m", "agent.export"],
                       cwd=AGENT, capture_output=True, text=True)
    if r.returncode != 0:
        log(f"ERROR export: {r.stderr.strip()[:200]}")
        return
    add = subprocess.run(["git", "add", *FILES], cwd=AGENT)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=AGENT)
    if diff.returncode == 0:
        log("skip — tidak ada perubahan")
        return
    for args in (["git", "commit", "-m",
                  "Auto-export sesi live",
                  "-m", "Co-Authored-By: Claude Code <noreply@anthropic.com>"],
                 ["git", "pull", "--rebase", "--autostash"],
                 ["git", "push"]):
        r = subprocess.run(args, cwd=AGENT, capture_output=True, text=True)
        if r.returncode != 0:
            log(f"ERROR git {' '.join(args[:2])}: {r.stderr.strip()[:200]}")
            return
    log(f"pushed: {r.stdout.strip().splitlines()[-1][:80] if r.stdout.strip() else 'ok'}")


def main():
    log("autoexport start (tick 25 mnt, sesi 20:30-03:00 WIB, s.d. Jum 03:05)")
    while True:
        now = datetime.now(WIB)
        if now >= END:
            log("window selesai — autoexport berhenti")
            return
        if in_session(now):
            export_and_push()
            t = next_tick(now)
        else:
            t = (now + timedelta(minutes=10)).replace(second=0, microsecond=0)
        time.sleep(max(30, (t - datetime.now(WIB)).total_seconds()))


if __name__ == "__main__":
    if "--once" in sys.argv:
        export_and_push()
    else:
        main()
