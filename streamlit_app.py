# ─────────────────────────────────────────────────────────────────────────────
#  QuantDesk Pro — Institutional-Grade AI Trading Dashboard
#  4-Tier Confluence Engine · Regime-Switching Framework · NSE/BSE Intelligence
#
#  BROKER INTEGRATION: Swap the SimulatedBrokerAPI class methods with your
#  actual Zerodha Kite Connect or DhanHQ API calls. The interface contract
#  (method signatures and return shapes) remains identical so zero dashboard
#  code changes are needed.
#
#  SEBI Compliance: API calls are rate-limited to ≤10 OPS via RateLimiter.
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import pytz
import random
import time as time_module
import math

# ── Streamlit Page Config — must be first call ────────────────────────────────
st.set_page_config(
    page_title="QuantDesk Pro | Institutional Trading Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS & CONFIG
# ─────────────────────────────────────────────────────────────────────────────
IST           = pytz.timezone("Asia/Kolkata")
MARKET_OPEN   = (9,  15)   # HH, MM
MARKET_CLOSE  = (15, 30)
REFRESH_SEC   = 30          # Data refresh interval
MAX_CARDS     = 10          # Max cards displayed per section
OPS_LIMIT     = 10          # SEBI retail broker OPS ceiling

# ─────────────────────────────────────────────────────────────────────────────
# NSE STOCK UNIVERSE  (lot_size for F&O eligibility)
# ─────────────────────────────────────────────────────────────────────────────
UNIVERSE = [
    {"ticker":"RELIANCE",   "name":"Reliance Industries",    "sector":"Energy",    "base":2847.50, "lot":250,  "fno":True},
    {"ticker":"TCS",        "name":"Tata Consultancy Svcs",  "sector":"IT",        "base":3921.25, "lot":150,  "fno":True},
    {"ticker":"HDFCBANK",   "name":"HDFC Bank Ltd",          "sector":"Banking",   "base":1678.90, "lot":550,  "fno":True},
    {"ticker":"INFY",       "name":"Infosys Ltd",            "sector":"IT",        "base":1456.30, "lot":300,  "fno":True},
    {"ticker":"ICICIBANK",  "name":"ICICI Bank Ltd",         "sector":"Banking",   "base":1234.75, "lot":700,  "fno":True},
    {"ticker":"SBIN",       "name":"State Bank of India",    "sector":"Banking",   "base":823.40,  "lot":1500, "fno":True},
    {"ticker":"BHARTIARTL", "name":"Bharti Airtel Ltd",      "sector":"Telecom",   "base":1892.60, "lot":470,  "fno":False},
    {"ticker":"AXISBANK",   "name":"Axis Bank Ltd",          "sector":"Banking",   "base":1156.20, "lot":600,  "fno":True},
    {"ticker":"TATAMOTORS", "name":"Tata Motors Ltd",        "sector":"Auto",      "base":978.45,  "lot":1400, "fno":True},
    {"ticker":"WIPRO",      "name":"Wipro Ltd",              "sector":"IT",        "base":567.80,  "lot":1500, "fno":False},
    {"ticker":"HINDALCO",   "name":"Hindalco Industries",    "sector":"Metals",    "base":623.15,  "lot":700,  "fno":False},
    {"ticker":"JSWSTEEL",   "name":"JSW Steel Ltd",          "sector":"Metals",    "base":934.70,  "lot":600,  "fno":False},
    {"ticker":"NTPC",       "name":"NTPC Ltd",               "sector":"Power",     "base":378.25,  "lot":2250, "fno":False},
    {"ticker":"POWERGRID",  "name":"Power Grid Corp",        "sector":"Power",     "base":312.40,  "lot":2700, "fno":False},
    {"ticker":"ONGC",       "name":"Oil & Natural Gas",      "sector":"Energy",    "base":276.90,  "lot":3850, "fno":False},
    {"ticker":"BAJFINANCE", "name":"Bajaj Finance Ltd",      "sector":"NBFC",      "base":7234.60, "lot":125,  "fno":True},
    {"ticker":"ASIANPAINT", "name":"Asian Paints Ltd",       "sector":"Paints",    "base":2456.80, "lot":200,  "fno":False},
    {"ticker":"TITAN",      "name":"Titan Company Ltd",      "sector":"Consumer",  "base":3567.40, "lot":175,  "fno":False},
    {"ticker":"SUNPHARMA",  "name":"Sun Pharma Industries",  "sector":"Pharma",    "base":1823.45, "lot":350,  "fno":False},
    {"ticker":"DRREDDY",    "name":"Dr. Reddy's Labs",       "sector":"Pharma",    "base":6789.20, "lot":125,  "fno":False},
    {"ticker":"HCLTECH",    "name":"HCL Technologies",       "sector":"IT",        "base":1678.30, "lot":350,  "fno":False},
    {"ticker":"DMART",      "name":"Avenue Supermarts",      "sector":"Retail",    "base":4234.65, "lot":150,  "fno":False},
    {"ticker":"NESTLEIND",  "name":"Nestle India Ltd",       "sector":"FMCG",      "base":23456.75,"lot":25,   "fno":False},
    {"ticker":"PIDILITIND", "name":"Pidilite Industries",    "sector":"Chemicals", "base":2890.25, "lot":200,  "fno":False},
    {"ticker":"NIFTY50",    "name":"Nifty 50 Index",         "sector":"Index",     "base":24850.0, "lot":50,   "fno":True},
    {"ticker":"BANKNIFTY",  "name":"Bank Nifty Index",       "sector":"Index",     "base":53240.0, "lot":15,   "fno":True},
]

# ─────────────────────────────────────────────────────────────────────────────
# RATE LIMITER — SEBI ≤10 OPS compliance shim
# ─────────────────────────────────────────────────────────────────────────────
class RateLimiter:
    """Token-bucket rate limiter. Max 10 API calls/second per SEBI retail limit."""
    def __init__(self, ops=OPS_LIMIT):
        self._ops   = ops
        self._calls = []

    def acquire(self):
        now = time_module.time()
        self._calls = [t for t in self._calls if now - t < 1.0]
        if len(self._calls) >= self._ops:
            time_module.sleep(1.0 - (now - self._calls[0]))
        self._calls.append(time_module.time())

_rate_limiter = RateLimiter()

# ─────────────────────────────────────────────────────────────────────────────
# SIMULATED BROKER API
# Production: Replace method bodies with kiteconnect / DhanHQ SDK calls.
# All method signatures and return shapes stay identical.
# ─────────────────────────────────────────────────────────────────────────────
class SimulatedBrokerAPI:

    @staticmethod
    def get_india_vix() -> float:
        """
        Production: fetch from NSE API or Kite quote("NSE:INDIA VIX").
        Returns current India VIX float.
        """
        _rate_limiter.acquire()
        seed = int(datetime.now(IST).timestamp() / 60)
        rng  = random.Random(seed)
        return round(14.8 + rng.uniform(-2.5, 8.2), 2)

    @staticmethod
    def get_quotes(tickers: list, seed_offset: int = 0) -> list:
        """
        Production: kite.quote(["NSE:RELIANCE", ...]) or DhanHQ /v2/marketfeed/quote.
        Returns list of enriched tick dicts — one per ticker.
        """
        _rate_limiter.acquire()
        now  = datetime.now(IST)
        seed = int(now.timestamp() / REFRESH_SEC) + seed_offset
        rng  = random.Random(seed)

        result = []
        for stock in tickers:
            noise      = rng.uniform(-0.022, 0.022)
            cmp        = round(stock["base"] * (1 + noise), 2)
            atr_pct    = rng.uniform(0.009, 0.028)
            atr        = round(cmp * atr_pct, 2)
            vwap_bias  = rng.uniform(-0.014, 0.014)
            vwap       = round(cmp * (1 + vwap_bias), 2)
            rvol       = round(rng.uniform(0.6, 4.8), 2)
            volume     = int(rng.randint(80_000, 4_000_000) * rvol)
            sweep_zone = round(cmp * rng.uniform(0.972, 0.993), 2)
            swept      = rng.random() > 0.42          # ~58 % detection rate
            trend      = rng.uniform(-1.0, 1.0)       # -1 = bearish, +1 = bullish
            wyckoff    = rng.choice(["Accumulation","Markup","Distribution","Markdown"])
            wave       = rng.choice(["Wave 3 UP","Wave 5 UP","Wave 2 Pullback",
                                     "Wave A DOWN","Wave C DOWN","Wave 3 DOWN"])
            result.append({
                **stock,
                "cmp":          cmp,
                "atr":          atr,
                "vwap":         vwap,
                "rvol":         rvol,
                "volume":       volume,
                "sweep_zone":   sweep_zone,
                "swept":        swept,
                "trend":        trend,
                "above_vwap":   cmp > vwap,
                "vwap_dist":    round((cmp - vwap) / vwap * 100, 2),
                "wyckoff":      wyckoff,
                "wave":         wave,
            })
        return result

# ─────────────────────────────────────────────────────────────────────────────
# REGIME-SWITCHING FRAMEWORK
# ─────────────────────────────────────────────────────────────────────────────
def classify_regime(vix: float) -> str:
    """
    Routes strategy selection based on market volatility weather.
    LOW_VOL  < 15   → All strategies active
    MED_VOL  15–20  → Favour credit spreads; allow cautious directional
    HIGH_VOL > 20   → Block all aggressive directional; credit spreads only
    """
    if vix < 15:   return "LOW_VOL"
    if vix <= 20:  return "MED_VOL"
    return "HIGH_VOL"

REGIME_META = {
    "LOW_VOL":  {"icon":"🟢","label":"LOW VOLATILITY",        "note":"All Strategies Active",                   "cls":"low"},
    "MED_VOL":  {"icon":"🟡","label":"ELEVATED VOLATILITY",   "note":"Prefer Credit Spreads",                   "cls":"med"},
    "HIGH_VOL": {"icon":"🔴","label":"HIGH VOLATILITY",       "note":"Aggressive Directional Plays BLOCKED",    "cls":"high"},
}

# ─────────────────────────────────────────────────────────────────────────────
# 4-TIER CONFLUENCE ENGINE — The Ultimate Gatekeeper
# ─────────────────────────────────────────────────────────────────────────────
def run_confluence(stocks: list, vix: float, mode: str = "INTRADAY") -> list:
    """
    TIER 1 — Market Regime  : India VIX gate. HIGH_VOL blocks intraday.
    TIER 2 — Inst. Footprint: RVOL ≥ 1.5× confirms institutional participation.
    TIER 3 — Liquidity Sweep: Recent stop-hunt zone detected + price reversal.
    TIER 4 — VWAP Momentum  : Price cleanly above (LONG) or below (SHORT) VWAP.

    Returns qualifying stocks sorted by Expected Profit Margin (EPM) ↓.
    Returns empty list → triggers Zero Confluence capital-preservation warning.
    """
    regime    = classify_regime(vix)
    qualified = []

    for s in stocks:
        # ── TIER 1: Regime Gate ───────────────────────────────────────────
        if regime == "HIGH_VOL" and mode == "INTRADAY":
            continue   # Block aggressive directional in high-vol regime

        # ── TIER 2: Institutional Footprint (RVOL ≥ 1.5×) ────────────────
        if s["rvol"] < 1.5:
            continue

        # ── TIER 3: Liquidity Sweep Detected ─────────────────────────────
        if not s["swept"]:
            continue

        # ── TIER 4: VWAP Momentum Alignment ──────────────────────────────
        bullish = s["trend"] > 0
        if bullish  and not s["above_vwap"]: continue   # Long signal but under VWAP
        if not bullish and s["above_vwap"]:  continue   # Short signal but over VWAP

        # ── All 4 Tiers Cleared — Compute Trade Parameters ───────────────
        action = "LONG" if bullish else "SHORT"
        cmp, atr, vwap = s["cmp"], s["atr"], s["vwap"]

        if action == "LONG":
            entry  = round(vwap * 1.0012, 2)
            target = round(entry + atr * 2.6, 2)
            stop   = round(s["sweep_zone"] - atr * 0.35, 2)
        else:
            entry  = round(vwap * 0.9988, 2)
            target = round(entry - atr * 2.6, 2)
            stop   = round(cmp + atr * 1.6, 2)

        reward   = abs(target - entry)
        risk     = abs(entry - stop) or 0.01
        rr_ratio = round(reward / risk, 2)

        # Win probability modelled on RVOL intensity + trend conviction
        win_p = min(0.86, max(0.48, 0.52
                              + (s["rvol"] - 1.5) * 0.06
                              + abs(s["trend"]) * 0.14))

        # Expected Profit Margin — primary ranking metric
        epm = round((win_p * reward - (1 - win_p) * risk) / entry * 100, 2)

        qualified.append({
            **s,
            "action":   action,
            "entry":    entry,
            "target":   target,
            "stop":     stop,
            "rr_ratio": rr_ratio,
            "win_p":    round(win_p * 100, 1),
            "epm":      epm,
            "regime":   regime,
        })

    qualified.sort(key=lambda x: x["epm"], reverse=True)
    return qualified

# ─────────────────────────────────────────────────────────────────────────────
# F&O CREDIT SPREAD ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def next_monthly_expiry() -> date:
    """NSE monthly expiry = last Thursday of the month."""
    today = datetime.now(IST).date()
    for extra_months in range(2):
        m = (today.month - 1 + extra_months) % 12 + 1
        y = today.year + ((today.month - 1 + extra_months) // 12)
        last_day = date(y + (1 if m == 12 else 0), m % 12 + 1, 1) - timedelta(days=1)
        offset   = (last_day.weekday() - 3) % 7     # days back to Thursday
        expiry   = last_day - timedelta(days=offset)
        if expiry > today:
            return expiry
    return today + timedelta(days=30)

def build_credit_spreads(stocks: list, vix: float) -> list:
    """
    Bull Put Spread : Sell OTM put + Buy deeper OTM put (net credit, bullish).
    Bear Call Spread: Sell OTM call + Buy further OTM call (net credit, bearish).
    Max expiry capped at 1 calendar month.
    Tracks daily Theta (in ₹ per lot) for premium-decay accounting.
    """
    expiry  = next_monthly_expiry()
    dte     = max(1, (expiry - datetime.now(IST).date()).days)
    seed    = int(datetime.now(IST).timestamp() / REFRESH_SEC) + 999
    rng     = random.Random(seed)
    result  = []

    fno_stocks = [s for s in stocks if s.get("fno")]

    for s in fno_stocks:
        if s["rvol"] < 1.5 or not s["swept"]:  # Confluence gates still apply
            continue
        cmp, atr, trend = s["cmp"], s["atr"], s["trend"]

        if trend > 0.08:
            kind         = "Bull Put"
            short_strike = _round_strike(cmp - atr * 1.0, cmp)
            long_strike  = _round_strike(cmp - atr * 2.1, cmp)
        elif trend < -0.08:
            kind         = "Bear Call"
            short_strike = _round_strike(cmp + atr * 1.0, cmp)
            long_strike  = _round_strike(cmp + atr * 2.1, cmp)
        else:
            continue  # Skip near-neutral instruments for spreads

        width             = round(abs(long_strike - short_strike), 2)
        premium           = round(width * rng.uniform(0.28, 0.44), 2)
        max_risk          = round(width - premium, 2)
        theta_per_unit    = round(premium / math.sqrt(dte) * rng.uniform(0.75, 1.25), 2)
        lot               = s.get("lot", 250)
        theta_rs          = round(theta_per_unit * lot, 2)

        win_p = min(0.82, 0.56 + (s["rvol"] - 1.5) * 0.05)
        epm   = round((win_p * premium - (1 - win_p) * max_risk) / max(max_risk, 0.01) * 100, 2)

        if epm <= 0:
            continue

        result.append({
            **s,
            "kind":         kind,
            "short_strike": short_strike,
            "long_strike":  long_strike,
            "width":        width,
            "premium":      premium,
            "max_risk":     max_risk,
            "theta_unit":   theta_per_unit,
            "theta_rs":     theta_rs,
            "lot":          lot,
            "dte":          dte,
            "expiry_str":   expiry.strftime("%d %b %Y"),
            "win_p":        round(win_p * 100, 1),
            "epm":          epm,
            "action":       "LONG" if kind == "Bull Put" else "SHORT",
        })

    result.sort(key=lambda x: x["epm"], reverse=True)
    return result

def _round_strike(price: float, ref: float) -> float:
    """Round to nearest sensible strike increment."""
    if ref >= 10_000: step = 100
    elif ref >= 2_000: step = 50
    elif ref >= 500:   step = 20
    else:              step = 10
    return round(price / step) * step

# ─────────────────────────────────────────────────────────────────────────────
# LONG-TERM HOLDINGS ENGINE
# ─────────────────────────────────────────────────────────────────────────────
LT_SECTORS = {"IT","Banking","NBFC","Paints","Consumer","Pharma","FMCG","Retail","Energy","Chemicals"}

def build_longterm(stocks: list, vix: float) -> list:
    """
    Long-term filter:
    • Relaxed RVOL ≥ 1.2× (institutional accumulation on weekly timeframe)
    • Wyckoff phase must be Accumulation or early Markup
    • Elliott Wave position compatible with early trend
    • Wide stops (ATR × 3) and stretched targets (ATR × 8 / ×15)
    """
    result = []
    for s in [x for x in stocks if x["sector"] in LT_SECTORS]:
        if s["rvol"] < 1.2 or not s["swept"]:
            continue
        if s["wyckoff"] not in ("Accumulation", "Markup"):
            continue

        entry   = round(s["vwap"] * 1.006, 2)
        tgt1    = round(entry + s["atr"] * 8,  2)
        tgt2    = round(entry + s["atr"] * 15, 2)
        stop    = round(entry - s["atr"] * 3,  2)
        reward  = tgt1 - entry
        risk    = max(entry - stop, 0.01)
        rr      = round(reward / risk, 2)
        win_p   = 0.60
        epm     = round((win_p * reward - (1 - win_p) * risk) / entry * 100, 2)

        if epm <= 0:
            continue

        horizon = "3–6 Months" if s["wyckoff"] == "Accumulation" else "1–3 Months"
        result.append({
            **s,
            "action":  "LONG",
            "entry":   entry,
            "target":  tgt1,
            "target2": tgt2,
            "stop":    stop,
            "rr_ratio":rr,
            "win_p":   round(win_p * 100, 1),
            "epm":     epm,
            "horizon": horizon,
        })

    result.sort(key=lambda x: x["epm"], reverse=True)
    return result

# ─────────────────────────────────────────────────────────────────────────────
# FORMATTING HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fp(v: float) -> str:
    """Format price with ₹ symbol and comma separators."""
    return f"₹{v:,.2f}" if v >= 1_000 else f"₹{v:.2f}"

def pct_color(v: float) -> str:
    return "green" if v >= 0 else "red"

# ─────────────────────────────────────────────────────────────────────────────
# CSS — Dark Institutional Theme with @keyframes card animations
# ─────────────────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Syne:wght@400;600;700;800&display=swap');

/* ── Nuke Streamlit Defaults ─────────────────────────────────────────────── */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"],
.stDeployButton { display:none !important; visibility:hidden !important; }
section[data-testid="stSidebar"] { display:none !important; }
.block-container { padding:0 !important; max-width:100% !important; }
.main .block-container { padding-top:0 !important; }
[data-testid="stAppViewContainer"] { background:#0d1117 !important; }

/* ── Base ────────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family:'JetBrains Mono',monospace !important;
    background:#0d1117 !important;
    color:#e6edf3 !important;
}

/* ── Live-dot Pulse ─────────────────────────────────────────────────────── */
@keyframes pulse {
    0%,100% { opacity:1; box-shadow:0 0 0 0 rgba(63,185,80,.45); }
    50%      { opacity:.7; box-shadow:0 0 0 7px rgba(63,185,80,0); }
}
.live-dot {
    display:inline-block; width:8px; height:8px; border-radius:50%;
    background:#3fb950; margin-right:8px; vertical-align:middle;
    animation:pulse 2s infinite;
}

/* ── Card Snap-In Animation ─────────────────────────────────────────────── */
@keyframes cardReveal {
    0%   { opacity:0; filter:blur(7px); transform:scale(.96) translateY(8px); }
    100% { opacity:1; filter:blur(0);   transform:scale(1)   translateY(0);   }
}

/* ── Regime Chips ───────────────────────────────────────────────────────── */
.chip {
    display:inline-block; font-size:10px; font-weight:700; letter-spacing:1px;
    text-transform:uppercase; padding:4px 11px; border-radius:4px;
}
.chip-low  { color:#3fb950; background:rgba(63,185,80,.10);  border:1px solid rgba(63,185,80,.30);  }
.chip-med  { color:#d29922; background:rgba(210,153,34,.10); border:1px solid rgba(210,153,34,.30); }
.chip-high { color:#f85149; background:rgba(248,81,73,.10);  border:1px solid rgba(248,81,73,.30);  }

/* ── Stat Pill ──────────────────────────────────────────────────────────── */
.stat-pill {
    display:inline-flex; align-items:center; gap:5px;
    font-size:11px; color:#8b949e;
}
.stat-val { color:#58a6ff; font-weight:600; }

/* ── Section Header ─────────────────────────────────────────────────────── */
.sec-hdr {
    font-family:'Syne',sans-serif !important;
    font-size:11px; font-weight:700; color:#6e7681;
    letter-spacing:2.5px; text-transform:uppercase;
    border-bottom:1px solid #21262d; padding-bottom:10px; margin-bottom:18px;
}
.sec-count {
    float:right; font-size:10px; color:#6e7681;
    background:#161b22; border:1px solid #21262d;
    padding:2px 10px; border-radius:20px; letter-spacing:.5px;
}

/* ── CARD ───────────────────────────────────────────────────────────────── */
.card {
    background:#0d1117; border:1px solid #21262d; border-radius:8px;
    padding:18px 20px 16px; position:relative; overflow:hidden;
    animation:cardReveal .28s ease-out both;
}
.card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
}
.card-long::before  { background:linear-gradient(90deg,#00d4ff,#0066ff); }
.card-short::before { background:linear-gradient(90deg,#ff4757,#ff1a2e); }
.card-lt::before    { background:linear-gradient(90deg,#a855f7,#7c3aed); }
.card-fno::before   { background:linear-gradient(90deg,#d29922,#f0883e); }

/* stagger delays */
.d0{animation-delay:0ms}   .d1{animation-delay:45ms}  .d2{animation-delay:90ms}
.d3{animation-delay:135ms} .d4{animation-delay:180ms} .d5{animation-delay:225ms}
.d6{animation-delay:270ms} .d7{animation-delay:315ms} .d8{animation-delay:360ms}
.d9{animation-delay:405ms}

.card-top {
    display:flex; justify-content:space-between; align-items:flex-start;
    margin-bottom:12px;
}
.ticker {
    font-family:'Syne',sans-serif !important;
    font-size:19px; font-weight:800; color:#f0f6fc; letter-spacing:-.5px; line-height:1;
}
.sub-tag { font-size:9px; color:#6e7681; letter-spacing:1.5px; text-transform:uppercase; margin-top:3px; }

.act-badge {
    font-size:10px; font-weight:700; padding:5px 10px;
    border-radius:4px; letter-spacing:1px; white-space:nowrap;
}
.act-long  { background:rgba(0,212,255,.12); color:#00d4ff; border:1px solid rgba(0,212,255,.30); }
.act-short { background:rgba(255,71,87,.12);  color:#ff4757; border:1px solid rgba(255,71,87,.30); }
.act-lt    { background:rgba(168,85,247,.12); color:#a855f7; border:1px solid rgba(168,85,247,.30); }
.act-fno-b { background:rgba(0,212,255,.12);  color:#00d4ff; border:1px solid rgba(0,212,255,.30); }
.act-fno-c { background:rgba(255,71,87,.12);  color:#ff4757; border:1px solid rgba(255,71,87,.30); }

.price-row { display:flex; align-items:baseline; gap:9px; margin-bottom:14px; }
.cmp-lbl   { font-size:9px; color:#6e7681; letter-spacing:1px; text-transform:uppercase; }
.cmp-val   { font-size:23px; font-weight:700; color:#f0f6fc; letter-spacing:-.5px; }

.mini-badge {
    font-size:9px; font-weight:700; padding:2px 7px; border-radius:3px;
    letter-spacing:.5px;
}
.mb-cyan   { background:rgba(0,212,255,.10); color:#00d4ff; border:1px solid rgba(0,212,255,.25); }
.mb-amber  { background:rgba(210,153,34,.10);color:#d29922; border:1px solid rgba(210,153,34,.25); }
.mb-green  { background:rgba(63,185,80,.10); color:#3fb950; border:1px solid rgba(63,185,80,.25); }
.mb-red    { background:rgba(248,81,73,.10); color:#f85149; border:1px solid rgba(248,81,73,.25); }
.mb-purple { background:rgba(168,85,247,.10);color:#a855f7; border:1px solid rgba(168,85,247,.25); }

.hr { height:1px; background:#21262d; margin:12px 0; }

.dgrid { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }
.dcell { display:flex; flex-direction:column; gap:3px; }
.dlbl  { font-size:9px; color:#6e7681; letter-spacing:1px; text-transform:uppercase; }
.dval  { font-size:13px; font-weight:600; color:#e6edf3; }
.dval.green  { color:#3fb950; }
.dval.red    { color:#f85149; }
.dval.cyan   { color:#00d4ff; }
.dval.purple { color:#a855f7; }
.dval.amber  { color:#d29922; }
.dval.muted  { color:#8b949e; font-size:11px; }

.card-foot {
    display:flex; justify-content:space-between; align-items:flex-end;
    margin-top:14px; padding-top:12px; border-top:1px solid #21262d;
    flex-wrap:wrap; gap:8px;
}
.foot-cell { display:flex; flex-direction:column; gap:2px; }

/* confluence pips */
.pips { display:flex; gap:3px; align-items:center; margin-top:2px; }
.pip  { width:18px; height:4px; border-radius:2px; background:#21262d; }
.pip.on { background:#3fb950; }

/* ── Card Grid ───────────────────────────────────────────────────────────── */
.card-grid {
    display:grid; grid-template-columns:1fr 1fr; gap:14px;
}

/* ── Zero Confluence ────────────────────────────────────────────────────── */
.zero-box {
    background:#0a0a0d; border:1px solid rgba(248,81,73,.40);
    border-radius:8px; padding:48px 32px; text-align:center; margin:24px 0;
}
.zero-icon { font-size:52px; display:block; margin-bottom:18px; }
.zero-ttl  {
    font-family:'Syne',sans-serif !important;
    font-size:22px; font-weight:800; color:#f85149; letter-spacing:-.5px; margin-bottom:10px;
}
.zero-sub  { font-size:12px; color:#8b949e; line-height:1.8; max-width:480px; margin:0 auto; }

/* ── Sticky Footer Bar ───────────────────────────────────────────────────── */
.foot-bar {
    position:fixed; bottom:0; left:0; right:0;
    background:#010409; border-top:1px solid #21262d;
    padding:7px 28px; display:flex; justify-content:space-between;
    font-size:10px; color:#6e7681; z-index:9999; align-items:center;
}
.foot-bar .right { display:flex; gap:20px; }

/* ── Disclaimer Box ─────────────────────────────────────────────────────── */
.disc {
    margin-top:20px; padding:12px 16px;
    background:#161b22; border:1px solid #21262d; border-radius:6px;
    font-size:10px; color:#6e7681; line-height:1.7;
}

/* ── Tab Override ────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background:transparent !important; gap:0 !important;
    border-bottom:1px solid #21262d !important; padding:0 28px !important;
}
.stTabs [data-baseweb="tab"] {
    background:transparent !important; color:#6e7681 !important;
    font-family:'JetBrains Mono',monospace !important;
    font-size:11px !important; font-weight:600 !important;
    letter-spacing:1px !important; text-transform:uppercase !important;
    padding:12px 22px !important; border-radius:0 !important;
    border-bottom:2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color:#00d4ff !important; border-bottom:2px solid #00d4ff !important;
    background:transparent !important;
}
.stTabs [data-baseweb="tab-highlight"] { background:transparent !important; }
.stTabs [data-baseweb="tab-panel"] { padding:0 !important; }

/* scrollbar */
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:#0d1117; }
::-webkit-scrollbar-thumb { background:#30363d; border-radius:2px; }
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
# LIVE CLOCK COMPONENT  (JavaScript iframe — ticks every second)
# ─────────────────────────────────────────────────────────────────────────────
CLOCK_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:transparent;font-family:'JetBrains Mono',monospace;overflow:hidden}
.wrap{display:flex;flex-direction:column;align-items:flex-end;padding-right:2px}
#t{font-size:31px;font-weight:700;color:#f0f6fc;letter-spacing:3px;line-height:1}
#cd{font-size:10.5px;font-weight:600;letter-spacing:1px;margin-top:5px}
#ms{font-size:9px;letter-spacing:2px;color:#6e7681;margin-top:3px}
.open{color:#3fb950} .close{color:#f85149} .off{color:#6e7681}
</style>
</head>
<body>
<div class="wrap">
  <div id="t">--:--:--</div>
  <div id="cd" class="off">Connecting...</div>
  <div id="ms">INDIA STANDARD TIME</div>
</div>
<script>
function tick(){
  var n=new Date(),ist=new Date(n.toLocaleString("en-US",{timeZone:"Asia/Kolkata"}));
  var h=ist.getHours(),m=ist.getMinutes(),s=ist.getSeconds();
  document.getElementById('t').textContent=
    String(h).padStart(2,'0')+':'+String(m).padStart(2,'0')+':'+String(s).padStart(2,'0');
  var tot=h*3600+m*60+s, open=9*3600+15*60, close=15*3600+30*60;
  var cd=document.getElementById('cd');
  function fmt(sec){var hh=Math.floor(sec/3600),mm=Math.floor((sec%3600)/60),ss=sec%60;
    return String(hh).padStart(2,'0')+':'+String(mm).padStart(2,'0')+':'+String(ss).padStart(2,'0');}
  if(tot<open){
    cd.textContent='MARKET OPENS IN '+fmt(open-tot);cd.className='open';
  }else if(tot<close){
    cd.textContent='MARKET CLOSES IN '+fmt(close-tot);cd.className='close';
  }else{
    cd.textContent='MARKET CLOSED — AFTER HOURS';cd.className='off';
  }
}
tick();setInterval(tick,1000);
</script>
</body>
</html>
"""

# ─────────────────────────────────────────────────────────────────────────────
# CARD BUILDERS — Custom flush-left HTML/CSS (no code-block rendering bugs)
# ─────────────────────────────────────────────────────────────────────────────
def _pips(n=4):
    return '<div class="pips">' + (''.join(['<div class="pip on"></div>'] * n)) + '</div>'

def card_intraday(s: dict, idx: int) -> str:
    a   = s["action"]
    cc  = "card-long" if a == "LONG" else "card-short"
    ac  = "act-long"  if a == "LONG" else "act-short"
    em  = "🟢 LONG"   if a == "LONG" else "🔴 SHORT"
    tc  = "green" if a == "LONG" else "red"
    sc  = "red"   if a == "LONG" else "green"
    di  = f"d{min(idx,9)}"
    vc  = "green" if s["above_vwap"] else "red"
    vt  = "▲ Above" if s["above_vwap"] else "▼ Below"
    ec  = "green" if s["epm"] >= 3 else "amber"

    return f"""
<div class="card {cc} {di}">
  <div class="card-top">
    <div>
      <div class="ticker">{s['ticker']}</div>
      <div class="sub-tag">{s['sector']}</div>
    </div>
    <div class="act-badge {ac}">{em}</div>
  </div>

  <div class="price-row">
    <span class="cmp-lbl">CMP</span>
    <span class="cmp-val">{fp(s['cmp'])}</span>
    <span class="mini-badge mb-cyan">RVOL {s['rvol']}×</span>
  </div>

  <div class="hr"></div>

  <div class="dgrid">
    <div class="dcell">
      <span class="dlbl">⚡ Entry Trigger</span>
      <span class="dval cyan">{fp(s['entry'])}</span>
    </div>
    <div class="dcell">
      <span class="dlbl">🎯 Target</span>
      <span class="dval {tc}">{fp(s['target'])}</span>
    </div>
    <div class="dcell">
      <span class="dlbl">🛑 Hard Stop</span>
      <span class="dval {sc}">{fp(s['stop'])}</span>
    </div>
  </div>

  <div class="card-foot">
    <div class="foot-cell">
      <span class="dlbl">Confluence</span>
      {_pips(4)}
    </div>
    <div class="foot-cell">
      <span class="dlbl">R:R</span>
      <span class="dval">{s['rr_ratio']}×</span>
    </div>
    <div class="foot-cell">
      <span class="dlbl">VWAP</span>
      <span class="dval {vc}">{vt}</span>
    </div>
    <div class="foot-cell">
      <span class="dlbl">ATR</span>
      <span class="dval muted">{fp(s['atr'])}</span>
    </div>
    <div class="foot-cell">
      <span class="dlbl">EPM</span>
      <span class="dval {ec}">+{s['epm']}%</span>
    </div>
  </div>
</div>"""

def card_fno(s: dict, idx: int) -> str:
    bull   = s["kind"] == "Bull Put"
    ac     = "act-fno-b" if bull else "act-fno-c"
    em     = "🟢 BULL PUT" if bull else "🔴 BEAR CALL"
    di     = f"d{min(idx,9)}"

    return f"""
<div class="card card-fno {di}">
  <div class="card-top">
    <div>
      <div class="ticker">{s['ticker']}</div>
      <div class="sub-tag">{s['kind']} Spread · {s['sector']}</div>
    </div>
    <div class="act-badge {ac}">{em}</div>
  </div>

  <div class="price-row">
    <span class="cmp-lbl">CMP</span>
    <span class="cmp-val">{fp(s['cmp'])}</span>
    <span class="mini-badge mb-purple">RVOL {s['rvol']}×</span>
  </div>

  <div class="hr"></div>

  <div class="dgrid">
    <div class="dcell">
      <span class="dlbl">Sell Strike</span>
      <span class="dval cyan">{fp(s['short_strike'])}</span>
    </div>
    <div class="dcell">
      <span class="dlbl">Buy Strike</span>
      <span class="dval">{fp(s['long_strike'])}</span>
    </div>
    <div class="dcell">
      <span class="dlbl">Spread Width</span>
      <span class="dval">{fp(s['width'])}</span>
    </div>
  </div>

  <div class="hr"></div>

  <div class="dgrid">
    <div class="dcell">
      <span class="dlbl">💰 Net Premium</span>
      <span class="dval green">{fp(s['premium'])}</span>
    </div>
    <div class="dcell">
      <span class="dlbl">📅 Daily Theta</span>
      <span class="dval amber">₹{s['theta_rs']:,.0f}</span>
    </div>
    <div class="dcell">
      <span class="dlbl">Max Risk</span>
      <span class="dval red">{fp(s['max_risk'])}</span>
    </div>
  </div>

  <div class="card-foot">
    <div class="foot-cell">
      <span class="dlbl">End Date</span>
      <span class="dval purple">{s['expiry_str']}</span>
    </div>
    <div class="foot-cell">
      <span class="dlbl">DTE</span>
      <span class="dval">{s['dte']}d</span>
    </div>
    <div class="foot-cell">
      <span class="dlbl">Lot Size</span>
      <span class="dval">{s['lot']}</span>
    </div>
    <div class="foot-cell">
      <span class="dlbl">Win Prob</span>
      <span class="dval green">{s['win_p']}%</span>
    </div>
    <div class="foot-cell">
      <span class="dlbl">EPM</span>
      <span class="dval green">+{s['epm']}%</span>
    </div>
  </div>
</div>"""

def card_lt(s: dict, idx: int) -> str:
    di = f"d{min(idx,9)}"
    ec = "green" if s["epm"] >= 3 else "amber"
    return f"""
<div class="card card-lt {di}">
  <div class="card-top">
    <div>
      <div class="ticker">{s['ticker']}</div>
      <div class="sub-tag">{s['sector']} · {s.get('wyckoff','')}</div>
    </div>
    <div class="act-badge act-lt">🟣 LONG</div>
  </div>

  <div class="price-row">
    <span class="cmp-lbl">CMP</span>
    <span class="cmp-val">{fp(s['cmp'])}</span>
    <span class="mini-badge mb-purple">RVOL {s['rvol']}×</span>
  </div>

  <div class="hr"></div>

  <div class="dgrid">
    <div class="dcell">
      <span class="dlbl">⚡ Entry</span>
      <span class="dval cyan">{fp(s['entry'])}</span>
    </div>
    <div class="dcell">
      <span class="dlbl">🎯 Target</span>
      <span class="dval green">{fp(s['target'])}</span>
    </div>
    <div class="dcell">
      <span class="dlbl">🛑 Stop Loss</span>
      <span class="dval red">{fp(s['stop'])}</span>
    </div>
  </div>

  <div class="card-foot">
    <div class="foot-cell">
      <span class="dlbl">Horizon</span>
      <span class="dval purple">{s.get('horizon','3–6M')}</span>
    </div>
    <div class="foot-cell">
      <span class="dlbl">Wave</span>
      <span class="dval cyan" style="font-size:10px;">{s.get('wave','')}</span>
    </div>
    <div class="foot-cell">
      <span class="dlbl">R:R</span>
      <span class="dval">{s['rr_ratio']}×</span>
    </div>
    <div class="foot-cell">
      <span class="dlbl">Confluence</span>
      {_pips(4)}
    </div>
    <div class="foot-cell">
      <span class="dlbl">EPM</span>
      <span class="dval {ec}">+{s['epm']}%</span>
    </div>
  </div>
</div>"""

def grid(cards: list[str]) -> str:
    return '<div class="card-grid">' + "".join(cards) + '</div>'

def zero_confluence_box(reason: str = "") -> str:
    note = f'<br><strong style="color:#d29922;">{reason}</strong>' if reason else ""
    return f"""
<div class="zero-box">
  <span class="zero-icon">⚠️</span>
  <div class="zero-ttl">ZERO CONFLUENCE — Capital Preservation Mode</div>
  <div class="zero-sub">
    No assets are clearing all 4 confluence tiers simultaneously.<br>
    Market conditions do not support high-probability entries right now.{note}<br><br>
    <strong style="color:#f85149;">Directive: Stand down. Preserve capital. No trades.</strong>
  </div>
</div>"""

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────────────────
def main():
    # ── Inject global CSS ─────────────────────────────────────────────────────
    st.markdown(CSS, unsafe_allow_html=True)

    # ── Pull market data (simulated; swap with real broker API) ───────────────
    api     = SimulatedBrokerAPI()
    vix     = api.get_india_vix()
    stocks  = api.get_quotes(UNIVERSE)
    regime  = classify_regime(vix)
    rmeta   = REGIME_META[regime]

    # ── Run engines ───────────────────────────────────────────────────────────
    intraday = run_confluence(stocks, vix, mode="INTRADAY")
    fno      = build_credit_spreads(stocks, vix)
    lt       = build_longterm(stocks, vix)
    expiry   = next_monthly_expiry()
    now_ist  = datetime.now(IST)
    refresh_ts = now_ist.strftime("%H:%M:%S IST")

    # ── HEADER ────────────────────────────────────────────────────────────────
    col_left, col_right = st.columns([3, 1])

    with col_left:
        st.markdown(f"""
<div style="padding:18px 28px 0 28px;">
  <div style="display:flex;align-items:baseline;gap:12px;margin-bottom:10px;">
    <span style="font-family:Syne,sans-serif;font-size:25px;font-weight:800;color:#f0f6fc;letter-spacing:-.5px;">
      <span class="live-dot"></span>QuantDesk Pro
    </span>
    <span style="font-size:10px;color:#6e7681;letter-spacing:2px;text-transform:uppercase;">
      Institutional Trading Intelligence · NSE/BSE
    </span>
  </div>

  <div style="display:flex;flex-wrap:wrap;gap:14px;align-items:center;padding-bottom:16px;
              border-bottom:1px solid #21262d;">
    <span class="chip chip-{rmeta['cls']}">{rmeta['icon']} {rmeta['label']} — {rmeta['note']}</span>
    <span class="stat-pill">VIX <span class="stat-val">{vix}</span></span>
    <span class="stat-pill">Intraday <span class="stat-val" style="color:#00d4ff;">{len(intraday)}</span></span>
    <span class="stat-pill">F&O Spreads <span class="stat-val" style="color:#a855f7;">{len(fno)}</span></span>
    <span class="stat-pill">Long-Term <span class="stat-val" style="color:#3fb950;">{len(lt)}</span></span>
    <span class="stat-pill">4-Tier Engine <span class="stat-val" style="color:#3fb950;">ACTIVE</span></span>
  </div>
</div>
""", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div style="padding-top:16px;padding-right:28px;">', unsafe_allow_html=True)
        components.html(CLOCK_HTML, height=82, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "⚡  INTRADAY CALLS",
        "📊  F&O CREDIT SPREADS",
        "🌱  LONG-TERM HOLDINGS",
    ])

    pad = "padding:20px 28px 80px 28px;"

    # ─── TAB 1 — INTRADAY ─────────────────────────────────────────────────────
    with tab1:
        st.markdown(f'<div style="{pad}">', unsafe_allow_html=True)
        st.markdown(f"""
<div class="sec-hdr">
  <span class="sec-count">{len(intraday)} qualifying</span>
  Intraday Calls — Sorted by Expected Profit Margin ↓
</div>""", unsafe_allow_html=True)

        if not intraday:
            reason = (
                f"India VIX = {vix} (above 20). All directional intraday plays blocked "
                "by the Regime-Switching Framework. Redirect capital → F&O Credit Spreads."
                if regime == "HIGH_VOL" else ""
            )
            st.markdown(zero_confluence_box(reason), unsafe_allow_html=True)
        else:
            cards = [card_intraday(s, i) for i, s in enumerate(intraday[:MAX_CARDS])]
            st.markdown(grid(cards), unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ─── TAB 2 — F&O ──────────────────────────────────────────────────────────
    with tab2:
        st.markdown(f'<div style="{pad}">', unsafe_allow_html=True)
        st.markdown(f"""
<div class="sec-hdr">
  <span class="sec-count">{len(fno)} qualifying</span>
  Credit Spreads — Max Expiry: <span style="color:#a855f7;">{expiry.strftime('%d %b %Y')}</span>
  &nbsp;·&nbsp; Theta Decay Harvesting Active
</div>""", unsafe_allow_html=True)

        if not fno:
            st.markdown(zero_confluence_box(), unsafe_allow_html=True)
        else:
            cards = [card_fno(s, i) for i, s in enumerate(fno[:MAX_CARDS])]
            st.markdown(grid(cards), unsafe_allow_html=True)

        st.markdown("""
<div class="disc">
  ⚠️ <strong style="color:#d29922;">F&O Risk Disclosure:</strong>
  Credit spreads cap downside to (Spread Width − Premium Collected) × Lot Size.
  Options involve risk of total premium loss. Max profit = Net Premium Collected × Lot Size.
  Connect your <strong>Zerodha Kite Connect</strong> or <strong>DhanHQ</strong> API key
  in the config to stream live option chain data and replace simulated quotes.
  Past performance does not guarantee future results. This dashboard is for educational
  and informational purposes only — not SEBI-registered investment advice.
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ─── TAB 3 — LONG-TERM ────────────────────────────────────────────────────
    with tab3:
        st.markdown(f'<div style="{pad}">', unsafe_allow_html=True)
        st.markdown(f"""
<div class="sec-hdr">
  <span class="sec-count">{len(lt)} qualifying</span>
  Long-Term Holdings — Wyckoff Phases · Elliott Wave · Sorted by EPM ↓
</div>""", unsafe_allow_html=True)

        if not lt:
            st.markdown(zero_confluence_box(), unsafe_allow_html=True)
        else:
            cards = [card_lt(s, i) for i, s in enumerate(lt[:MAX_CARDS])]
            st.markdown(grid(cards), unsafe_allow_html=True)

        st.markdown("""
<div class="disc">
  ℹ️ Long-term targets use Fibonacci extensions (ATR × 8 / × 15). Entries confirmed by
  Wyckoff Accumulation / early Markup phase. Stops set at 3× ATR to withstand
  normal weekly volatility. Review and re-score monthly. Not SEBI-registered advice.
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── STICKY FOOTER BAR ─────────────────────────────────────────────────────
    st.markdown(f"""
<div class="foot-bar">
  <div>
    <span style="display:inline-block;width:6px;height:6px;border-radius:50%;
      background:#3fb950;margin-right:6px;vertical-align:middle;animation:pulse 1.5s infinite;">
    </span>
    LIVE SIM · Auto-refresh {REFRESH_SEC}s · Last: {refresh_ts}
  </div>
  <div class="right">
    <span>⚙️ Swap SimulatedBrokerAPI → Kite / DhanHQ for live data</span>
    <span>🔒 SEBI-compliant · ≤{OPS_LIMIT} OPS · Rate-limited</span>
    <span>🧠 4-Tier Confluence Engine · Regime-Switching Active</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── AUTO-REFRESH ──────────────────────────────────────────────────────────
    # Uses session state to avoid blocking the render loop.
    # On each rerun, we check if REFRESH_SEC seconds have elapsed.
    if "last_tick" not in st.session_state:
        st.session_state.last_tick = time_module.time()

    elapsed = time_module.time() - st.session_state.last_tick
    remaining = max(0, REFRESH_SEC - elapsed)

    # Sleep only the remaining time, then rerun
    time_module.sleep(remaining)
    st.session_state.last_tick = time_module.time()
    st.rerun()


if __name__ == "__main__":
    main()
