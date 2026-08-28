"""Thin wrapper over alpaca-py: trading + options/stock data + order helpers."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional

from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import (OptionChainRequest, StockBarsRequest,
                                  StockLatestTradeRequest)
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (GetOptionContractsRequest,
                                     GetOrdersRequest, LimitOrderRequest,
                                     QueryOrderStatus)

from . import config


def parse_occ(sym: str) -> tuple[str, date, str, float]:
    """'SPY260904C00500000' -> ('SPY', date(2026,9,4), 'C', 505.0)"""
    i = next(idx for idx, ch in enumerate(sym) if ch.isdigit())
    root = sym[:i]
    d = datetime.strptime(sym[i:i + 6], "%y%m%d").date()
    right = sym[i + 6].upper()
    strike = int(sym[i + 7:]) / 1000.0
    return root, d, right, strike


def _num(x) -> Optional[float]:
    try:
        v = float(x)
        return v if v == v else None  # NaN guard
    except (TypeError, ValueError):
        return None


def _quote_pair(q) -> tuple[Optional[float], Optional[float]]:
    """SDK model names differ across versions; try both spellings."""
    bid = _num(getattr(q, "bid_price", None)) or _num(getattr(q, "bp", None))
    ask = _num(getattr(q, "ask_price", None)) or _num(getattr(q, "ap", None))
    return bid, ask


class Candidate:
    """A tradable option contract with live quote + greeks attached."""

    def __init__(self, symbol, strike, expiry, right, delta, iv, bid, ask, oi):
        self.symbol = symbol
        self.strike = strike
        self.expiry = expiry
        self.right = right
        self.delta = delta
        self.iv = iv
        self.bid = bid
        self.ask = ask
        self.oi = oi

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2

    @property
    def dte(self) -> int:
        return (self.expiry - date.today()).days

    @property
    def premium_pct(self) -> float:
        """Premium (at bid) / collateral for a cash-secured short."""
        return self.bid / self.strike

    def as_dict(self) -> dict:
        return {"symbol": self.symbol, "strike": self.strike, "expiry": self.expiry.isoformat(),
                "right": self.right, "delta": round(self.delta, 3), "iv": round(self.iv, 3),
                "bid": self.bid, "ask": self.ask, "oi": self.oi, "dte": self.dte}


class Api:
    def __init__(self):
        if not config.PAPER:
            raise RuntimeError("config.PAPER is False — this project is paper-only by design")
        if not config.KEY_ID or not config.SECRET_KEY:
            raise RuntimeError("missing APCA_API_KEY_ID / APCA_API_SECRET_KEY (agent/.env)")
        self.trade = TradingClient(config.KEY_ID, config.SECRET_KEY, paper=True)
        self.opts = OptionHistoricalDataClient(config.KEY_ID, config.SECRET_KEY)
        self.stocks = StockHistoricalDataClient(config.KEY_ID, config.SECRET_KEY)

    # ---- account & state ----
    def clock(self):
        return self.trade.get_clock()

    def account(self):
        return self.trade.get_account()

    def positions(self):
        return list(self.trade.get_all_positions() or [])

    def open_orders(self) -> list:
        return list(self.trade.get_orders(GetOrdersRequest(status=QueryOrderStatus.OPEN)) or [])

    def order_by_coid(self, coid: str):
        try:
            return self.trade.get_order_by_client_id(coid)
        except Exception:
            return None  # not found -> safe to (re)consider; submit path is guarded by coid

    # ---- stock data ----
    def last_trade(self, symbol: str) -> Optional[float]:
        try:
            r = self.stocks.get_stock_latest_trade(
                StockLatestTradeRequest(symbol_or_symbols=symbol, feed="iex"))
            return _num(getattr(r[symbol], "price", None))
        except Exception:
            return None

    def daily_closes(self, symbol: str, days: int = 120) -> list[float]:
        try:
            r = self.stocks.get_stock_bars(StockBarsRequest(
                symbol_or_symbols=symbol, timeframe=TimeFrame.Day,
                start=datetime.utcnow() - timedelta(days=days),
                feed="iex"))
            # This SDK version returns BarSet with .data -> {symbol: [Bar]},
            # Bar fields use full names (b.close, not wire-format b.c).
            data = getattr(r, "data", None)
            if isinstance(data, dict):
                bars = data.get(symbol) or []
            elif isinstance(r, dict):
                bs = r.get(symbol)
                bars = list(getattr(bs, "bars", []) or [])
            else:
                bars = list(getattr(r, "bars", []) or [])
            closes = []
            for b in bars:
                c = getattr(b, "close", None)
                if c is None and isinstance(b, dict):
                    c = b.get("close")
                if c:
                    closes.append(float(c))
            return closes
        except Exception:
            return []

    # ---- options data ----
    def chain_snapshots(self, underlying: str) -> dict:
        try:
            return self.opts.get_option_chain(
                OptionChainRequest(underlying_symbol=underlying)) or {}
        except Exception:
            return {}

    def candidates(self, underlying: str, right: str,
                   dte_min: int, dte_max: int,
                   strike_max: Optional[float] = None,
                   strike_min: Optional[float] = None) -> list[Candidate]:
        today = date.today()
        resp = self.trade.get_option_contracts(GetOptionContractsRequest(
            underlying_symbols=[underlying], status="active",
            expiration_date_gte=(today + timedelta(days=dte_min)).isoformat(),
            expiration_date_lte=(today + timedelta(days=dte_max)).isoformat(),
            type=("call" if right == "C" else "put"), limit=1000))
        snaps = self.chain_snapshots(underlying)
        out: list[Candidate] = []
        for c in (resp.option_contracts or []):
            if not getattr(c, "tradable", False):
                continue
            oi = _num(getattr(c, "open_interest", 0)) or 0
            if oi < config.MIN_OPEN_INTEREST:
                continue
            s = snaps.get(c.symbol)
            if s is None or getattr(s, "greeks", None) is None:
                continue
            delta = _num(getattr(s.greeks, "delta", None))
            if delta is None:
                continue
            delta = abs(delta)
            bid, ask = _quote_pair(s.latest_quote) if getattr(s, "latest_quote", None) else (None, None)
            if not bid or not ask or bid <= 0 or ask <= 0:
                continue
            mid = (bid + ask) / 2
            if (ask - bid) / mid > config.MAX_QUOTE_SPREAD_PCT:
                continue
            strike = float(c.strike_price)
            if strike_max and strike > strike_max:
                continue
            if strike_min and strike < strike_min:
                continue
            out.append(Candidate(c.symbol, strike, parse_occ(c.symbol)[1], right,
                                 delta, _num(getattr(s, "implied_volatility", 0)) or 0.0,
                                 bid, ask, int(oi)))
        return out

    # ---- orders ----
    def submit_option_limit(self, occ: str, qty: int, side: str, price: float,
                            coid: str) -> dict:
        """Submit a simple day limit order for an option contract."""
        req = LimitOrderRequest(
            symbol=occ, qty=qty, side=side, type="limit", time_in_force="day",
            order_class="simple", limit_price=round(price, 2),
            extended_hours=False, client_order_id=coid)
        o = self.trade.submit_order(req)
        return {"id": getattr(o, "id", None), "coid": coid, "symbol": occ,
                "side": side, "qty": qty, "limit": round(price, 2),
                "status": getattr(o, "status", None)}

    def cancel_order(self, order_id: str) -> bool:
        try:
            self.trade.cancel_order_by_id(order_id)
            return True
        except Exception:
            return False
