"""AI layer: Claude (headless via Claude Code CLI) as regime reader + entry veto.

Design rule: the AI can only TIGHTEN (veto entries, downgrade regime), never force
a trade. If the AI call fails, we fall back to NEUTRAL and the deterministic risk
gates still apply. Buybacks (risk-reducing) are never sent to the AI.
"""
from __future__ import annotations

import json
import re
import subprocess
from typing import Optional

from . import config

REGIME_PROMPT = """You are the risk overlay of an options wheel trading agent (paper account).
Given the market summary below, classify the current regime for SELLING cash-secured puts
on liquid US large/mid caps over the next few sessions.

Market summary (JSON):
{summary}

Rules:
- RISK_OFF: falling knife / stressed tape (e.g. index well below both SMAs with momentum down)
- NEUTRAL: mixed or choppy
- RISK_ON: orderly uptrend or healthy pullback

Answer with STRICT JSON only, no prose: {{"regime":"RISK_ON|NEUTRAL|RISK_OFF","reason":"<max 20 words"}}"""

VETO_PROMPT = """You are the entry veto layer of an options wheel trading agent (paper account).
The deterministic engine proposes the NEW entries below. Each is a cash-secured short put or a
covered call with defined risk. Veto only entries with a concrete, stated flaw (e.g. symbol has
earnings very soon, distressed name, abnormal IV without cause, obviously illiquid).

Proposals (JSON):
{proposals}

Answer with STRICT JSON only, no prose:
{{"veto":[<list of coid strings to veto>],"reasons":{{"<coid>":"<max 15 words>"}}}}"""


def _ask(prompt: str) -> Optional[dict]:
    """Run `claude -p` headless; return parsed JSON from its reply, or None."""
    if not config.AI_ENABLED:
        return None
    try:
        p = subprocess.run(
            ["claude", "-p", "--output-format", "json"],
            input=prompt, capture_output=True, text=True,
            timeout=config.AI_TIMEOUT_S)
        if p.returncode != 0 or not p.stdout.strip():
            return None
        data = json.loads(p.stdout.strip().splitlines()[-1])
        result = str(data.get("result") or "")
        m = re.search(r"\{.*\}", result, re.S)
        return json.loads(m.group(0)) if m else None
    except Exception:
        return None


def read_regime(market_summary: dict) -> dict:
    out = _ask(REGIME_PROMPT.format(summary=json.dumps(market_summary, default=str)))
    if not isinstance(out, dict) or out.get("regime") not in ("RISK_ON", "NEUTRAL", "RISK_OFF"):
        return {"regime": "NEUTRAL", "reason": "AI unavailable/invalid -> conservative default", "ai": False}
    out["ai"] = True
    return out


def veto_entries(intents: list[dict]) -> dict:
    if not intents:
        return {"veto": [], "reasons": {}, "ai": False}
    out = _ask(VETO_PROMPT.format(proposals=json.dumps(intents, default=str)))
    if not isinstance(out, dict) or not isinstance(out.get("veto"), list):
        return {"veto": [], "reasons": {}, "ai": False}
    out.setdefault("reasons", {})
    out["ai"] = True
    return out
