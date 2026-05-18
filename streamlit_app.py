import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

# --- 1. SYSTEM INITIALIZATION & LOOP ---
if "run_count" not in st.session_state:
    st.session_state.run_count = 0
st.session_state.run_count += 1

st.set_page_config(page_title="AI Quant Live", layout="centered", initial_sidebar_state="collapsed")

# --- 2. TIME & COUNTDOWN LOGIC (IST) ---
ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
current_time_str = ist_now.strftime("%H:%M:%S")

market_open = ist_now.replace(hour=9, minute=15, second=0, microsecond=0)
market_close = ist_now.replace(hour=15, minute=30, second=0, microsecond=0)

if ist_now < market_open:
    status_label = "🔴 MARKET OPENS IN"
    diff = market_open - ist_now
elif ist_now > market_close:
    status_label = "🔴 MARKET CLOSED"
    diff = timedelta(seconds=0) 
else:
    status_label = "🟢 MARKET CLOSES IN"
    diff = market_close - ist_now

hours, remainder = divmod(diff.seconds, 3600)
minutes, seconds = divmod(remainder, 60)
countdown_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
if ist_now > market_close:
    countdown_str = "--h --m --s"

# --- 3. PREMIUM UI CSS (Bulletproof String Format) ---
css = (
    '<style>'
    '.block-container { padding-top: 1rem; padding-bottom: 0rem; max-width: 800px; }'
    '.header-panel { display: flex; justify-content: space-between; background: linear-gradient(145deg, #1c2128, #0d1117); border: 1px solid #444c56; border-radius: 8px; padding: 18px 24px; margin-bottom: 20px; box-shadow: 0 6px 16px rgba(0,0,0,0.5); }'
    '.time-box { text-align: left; }'
    '.countdown-box { text-align: right; }'
    '.header-label { font-size: 0.85rem; color: #c9d1d9 !important; text-transform: uppercase; font-weight: 700; letter-spacing: 1px;}'
    '.header-value { font-size: 1.6rem; font-weight: 800; color: #ffffff !important; font-family: monospace; margin-top: 4px; text-shadow: 0px 2px 4px rgba(0,0,0,0.8);}'
    '@keyframes snapIn { 0% { opacity: 0; transform: scale(0.95); filter: blur(4px); } 100% { opacity: 1; transform: scale(1); filter: blur(0); } }'
    '.sq-card { background-color: #0d1117; border-top: 4px solid #00ffcc; border-radius: 8px; padding: 18px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.4); animation: snapIn 0.3s ease-out forwards; height: 100%; display: flex; flex-direction: column; justify-content: space-between; }'
    '.sq-card-short { border-top-color: #ff3366; }'
    '.sq-card-long { border-top-color: #a155ff; }'
    '.sq-title-row { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;}'
    '.sq-ticker { font-size: 1rem; font-weight: 700; color: #8b949e; margin: 0; text-transform: uppercase;}'
    '.sq-price { font-size: 1.7rem; font-weight: 800; color: #ffffff; margin: 2px 0 6px 0; font-family: monospace;}'
    '.sq-margin { font-size: 1.05rem; font-weight: 800; background: #161b22; padding: 4px 10px; border-radius: 4px; border: 1px solid #30363d;}'
    '.sq-data-row { display: flex; justify-content: space-between; border-bottom: 1px solid #21262d; padding: 8px 0; align-items: center;}'
    '.sq-data-row:last-child { border-bottom: none; }'
    '.sq-label { font-size: 0.8rem; color: #8b949e; width: 35%;}'
    '.sq-val { font-size: 0.9rem; font-weight: 700; color: #c9d1d9; text-align: right; width: 65%;}'
    '.val-target { color: #00ffcc; font-size: 1rem;}'
    '.val-sl { color: #ff3366; font-size: 1rem;}'
    '</style>'
)
st.markdown(css, unsafe_allow_html=True)

# --- 4. HEADER RENDER ---
header_html = (
    '<div class="header-panel">'
    '<div class="time-box">'
    '<div class="header-label">Live Clock (IST)</div>'
    f'<div class="header-value">{current_time_str}</div>'
    '</div>'
    '<div class="countdown-box">'
    f'<div class="header-label">{status_label}</div>'
    f'<div class="header-value" style="color: #00ffcc !important;">{countdown_str}</div>'
    '</div>'
    '</div>'
)
st.markdown(header_html, unsafe_allow_html=True)

category = st.radio("Mode:", ["⚡ INTRADAY", "📦 F&O", "⏳ LONG TERM"], horizontal=True, label_visibility="collapsed")
st.markdown("<br>", unsafe_allow_html=True)

# --- 5. DATA SIMULATION ---
@st.cache_data(ttl=2)
def fetch_market_stream():
    stocks = ["TECHM", "INFY", "TATASTEEL", "SBIN", "RELIANCE", "HDFCBANK"]
    base_prices = {"TECHM": 1428.00, "INFY": 1129.70, "TATASTEEL": 205.20, "SBIN": 832.00, "RELIANCE": 2462.00, "HDFCBANK": 1430.50}
    atrs = {"TECHM": 26.0, "INFY": 19.0, "TATASTEEL": 5.1, "SBIN": 13.0, "RELIANCE": 38.0, "HDFCBANK": 22.0}
    
    matrix = []
    for s in stocks:
        tick = np.random.uniform(-0.004, 0.005) * base_prices[s]
        cmp = round(base_prices[s] + tick, 2)
        margin = round((atrs[s] * 1.5) / cmp * 100, 2)
        matrix.append({"Ticker": s, "CMP": cmp, "ATR": atrs[s], "Margin": margin})
    return pd.DataFrame(matrix)

live_data = fetch_market_stream()

# --- 6. RENDER 2-COLUMN GRID CARDS ---
if category == "⚡ INTRADAY":
    sorted_data = live_data.sort_values(by="Margin", ascending=False).head(4)
    col1, col2 = st.columns(2)
    
    for index, row in sorted_data.reset_index().iterrows():
        is_short = row["Ticker"] in ["TATASTEEL", "RELIANCE"]
        card_class = "sq-card sq-card-short" if is_short else "sq-card"
        action = "🔴 SHORT" if is_short else "🟢 LONG"
        m_color = "#ff3366" if is_short else "#00ffcc"
        
        tgt = round(row['CMP'] - (row['ATR'] * 1.5), 2) if is_short else round(row['CMP'] + (row['ATR'] * 1.5), 2)
        sl = round(row['CMP'] + (row['ATR'] * 1.0), 2) if is_short else round(row['CMP'] - (row['ATR'] * 1.0), 2)

        card_html = (
            f'<div class="{card_class}">'
            f'<div class="sq-title-row">'
            f'<div><p class="sq-ticker">{row["Ticker"]}</p><p class="sq-price">₹{row["CMP"]}</p></div>'
            f'<p class="sq-margin" style="color: {m_color};">+{row["Margin"]}%</p>'
            f'</div>'
            f'<div class="sq-data-row"><span class="sq-label">Action</span><span class="sq-val">{action}</span></div>'
            f'<div class="sq-data-row"><span class="sq-label">Target</span><span class="sq-val val-target">₹{tgt}</span></div>'
            f'<div class="sq-data-row"><span class="sq-label">Stop</span><span class="sq-val val-sl">₹{sl}</span></div>'
            f'</div>'
        )
        
        if index % 2 == 0:
            with col1: st.markdown(card_html, unsafe_allow_html=True)
        else:
            with col2: st.markdown(card_html, unsafe_allow_html=True)

elif category == "📦 F&O":
    sorted_data = live_data.sort_values(by="CMP", ascending=True).head(4)
    col1, col2 = st.columns(2)
    
    for index, row in sorted_data.reset_index().iterrows():
        fo_margin = round(row['Margin'] * 4.6, 1)
        is_bearish = index % 2 != 0  
        
        if is_bearish:
            card_class = "sq-card sq-card-short"
            m_color = "#ff3366"
            strategy = "Bear Call Spread"
            setup = f"Sell {int(row['CMP'] + row['ATR'])} CE <br> Buy {int(row['CMP'] + (row['ATR']*2))} CE"
            sl = round(row['CMP'] + row['ATR'], 2)
        else:
            card_class = "sq-card"
            m_color = "#00ffcc"
            strategy = "Bull Put Spread"
            setup = f"Sell {int(row['CMP'] - row['ATR'])} PE <br> Buy {int(row['CMP'] - (row['ATR']*2))} PE"
            sl = round(row['CMP'] - row['ATR'], 2)

        card_html = (
            f'<div class="{card_class}">'
            f'<div class="sq-title-row">'
            f'<div><p class="sq-ticker">{row["Ticker"]} F&O</p><p class="sq-price">₹{row["CMP"]}</p></div>'
            f'<p class="sq-margin" style="color: {m_color};">+{fo_margin}%</p>'
            f'</div>'
            f'<div class="sq-data-row"><span class="sq-label">Strategy</span><span class="sq-val">{strategy}</span></div>'
            f'<div class="sq-data-row"><span class="sq-label">Legs</span><span class="sq-val" style="font-size:0.75rem;">{setup}</span></div>'
            f'<div class="sq-data-row"><span class="sq-label">Floor</span><span class="sq-val val-sl">₹{sl}</span></div>'
            f'</div>'
        )
        
        if index % 2 == 0:
            with col1: st.markdown(card_html, unsafe_allow_html=True)
        else:
            with col2: st.markdown(card_html, unsafe_allow_html=True)

elif category == "⏳ LONG TERM":
    lt_targets = {"TECHM": 23.5, "INFY": 18.0, "TATASTEEL": 14.2, "SBIN": 19.4, "RELIANCE": 12.5, "HDFCBANK": 16.5}
    sorted_data = live_data.sort_values(by="Ticker", ascending=True).head(4)
    col1, col2 = st.columns(2)
    
    for index, row in sorted_data.reset_index().iterrows():
        t_margin = lt_targets.get(row['Ticker'], 15.0)
        card_class = "sq-card sq-card-long"
        m_color = "#a155ff" 
        
        buy_zone = f"₹{round(row['CMP']*0.97, 2)} - ₹{row['CMP']}"
        tgt = round(row['CMP'] * (1 + t_margin/100), 2)
        
        card_html = (
            f'<div class="{card_class}">'
            f'<div class="sq-title-row">'
            f'<div><p class="sq-ticker">{row["Ticker"]} Core</p><p class="sq-price">₹{row["CMP"]}</p></div>'
            f'<p class="sq-margin" style="color: {m_color};">+{t_margin}%</p>'
            f'</div>'
            f'<div class="sq-data-row"><span class="sq-label">Horizon</span><span class="sq-val">6-12 Months</span></div>'
            f'<div class="sq-data-row"><span class="sq-label">Buy Zone</span><span class="sq-val" style="font-size:0.75rem; color:#00ffcc;">{buy_zone}</span></div>'
            f'<div class="sq-data-row"><span class="sq-label">Target</span><span class="sq-val val-target">₹{tgt}</span></div>'
            f'</div>'
        )
        
        if index % 2 == 0:
            with col1: st.markdown(card_html, unsafe_allow_html=True)
        else:
            with col2: st.markdown(card_html, unsafe_allow_html=True)

# --- 7. AUTO-REFRESH LOOP ---
time.sleep(1) 
st.rerun()
