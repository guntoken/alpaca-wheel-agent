"""CLI: status | cycle | loop | cancel-orders.

Safety default: everything runs DRY (plans + journals, submits nothing) unless
--live is passed explicitly. The account is paper-only regardless.
"""
from __future__ import annotations

import argparse
import time

from . import config, journal
from .alpaca_client import Api
from .cycle import run_cycle


def cmd_status(_args) -> None:
    api = Api()
    clock = api.clock()
    acct = api.account()
    print(f"market_open : {clock.is_open}")
    print(f"equity      : ${float(acct.equity):,.2f}   buying power: ${float(acct.buying_power):,.2f}")
    print(f"options lv  : approved={acct.options_approved_level} effective={acct.options_trading_level}")
    print("positions   :")
    poss = api.positions()
    if not poss:
        print("  (none)")
    for p in poss:
        print(f"  {p.symbol:<22} {str(getattr(p, 'side', '')):<5} qty={p.qty:<8} "
              f"uPL={float(getattr(p, 'unrealized_pl', 0) or 0):+,.2f}")
    orders = api.open_orders()
    print(f"open orders : {len(orders)}")
    for o in orders:
        print(f"  {getattr(o, 'client_order_id', ''):<28} {getattr(o, 'symbol', ''):<22} "
              f"{getattr(o, 'side', ''):<4} {getattr(o, 'status', '')}")
    last = journal.tail(3)
    print(f"journal     : {config.JOURNAL_FILE} ({len(last)} recent shown)")
    for r in last:
        print(f"  {r.get('ts')} cycle#{r.get('cycle_no')} "
              f"dry={r.get('dry_run')} orders={len(r.get('orders', []))} "
              f"errs={len(r.get('errors', []))}")


def cmd_cycle(args) -> None:
    rec = run_cycle(dry_run=not args.live, force=args.force, no_ai=args.no_ai)
    _print_cycle(rec)


def cmd_loop(args) -> None:
    api = Api()
    interval = args.interval
    print(f"loop: interval={interval}s  live={args.live}  (Ctrl-C to stop)")
    while True:
        try:
            clock = api.clock()
            if clock.is_open:
                rec = run_cycle(dry_run=not args.live, force=False, no_ai=args.no_ai)
                _print_cycle(rec)
            else:
                print(f"[{time.strftime('%H:%M:%S')}] market closed, waiting...")
        except KeyboardInterrupt:
            print("loop stopped by user")
            return
        except Exception as e:
            print(f"cycle error (continuing): {e}")
        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            print("loop stopped by user")
            return


def cmd_cancel_orders(args) -> None:
    api = Api()
    orders = [o for o in api.open_orders()
              if str(getattr(o, "client_order_id", "")).startswith(config.ORDER_PREFIX)]
    if not orders:
        print("no wheel orders open")
        return
    for o in orders:
        oid = getattr(o, "id", None)
        if args.live:
            ok = api.cancel_order(oid)
            print(f"{'cancelled' if ok else 'FAILED'} {getattr(o, 'symbol', '')} ({oid})")
        else:
            print(f"[dry] would cancel {getattr(o, 'symbol', '')} ({oid})")


def _print_cycle(rec: dict) -> None:
    mode = "DRY-RUN" if rec.get("dry_run") else "LIVE"
    print(f"--- cycle #{rec.get('cycle_no')} [{mode}] equity=${rec.get('equity', 0):,.0f} "
          f"regime={rec.get('ai_regime', {}).get('regime', 'n/a')} "
          f"entries_allowed={rec.get('entries_allowed')}")
    for e in rec.get("errors", []):
        print(f"  ERR  {e}")
    for o in rec.get("orders", []):
        print(f"  {o.get('action', ''):<12} {o.get('kind', ''):<12} {o.get('occ', ''):<22} "
              f"qty={o.get('qty')} limit={o.get('limit')} :: {o.get('reason', '')[:80]}")
    for i in rec.get("intents", []):
        if i.get("kind") == "SKIP":
            print(f"  {'skip':<12} {i.get('underlying', ''):<6} {i.get('reason', '')[:90]}")


def main() -> None:
    ap = argparse.ArgumentParser(prog="wheel-agent",
                                 description="Options wheel agent (Alpaca hackathon, paper only)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status").set_defaults(func=cmd_status)

    p_cycle = sub.add_parser("cycle")
    p_cycle.add_argument("--live", action="store_true", help="actually submit orders (default: dry-run)")
    p_cycle.add_argument("--force", action="store_true", help="run even when market is closed")
    p_cycle.add_argument("--no-ai", action="store_true", help="skip Claude regime/veto calls")
    p_cycle.set_defaults(func=cmd_cycle)

    p_loop = sub.add_parser("loop")
    p_loop.add_argument("--live", action="store_true")
    p_loop.add_argument("--no-ai", action="store_true")
    p_loop.add_argument("--interval", type=int, default=300)
    p_loop.set_defaults(func=cmd_loop)

    p_cancel = sub.add_parser("cancel-orders")
    p_cancel.add_argument("--live", action="store_true")
    p_cancel.set_defaults(func=cmd_cancel_orders)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
