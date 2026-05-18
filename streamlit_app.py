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
# Calculate current IST time
ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
current_time_str = ist_now.strftime("%H:%M:%S")

# Calculate Market Open (09:15) and Close (15:30)
market_open = ist_now.replace(hour=9, minute=15, second=0, microsecond=0)
market_close = ist_now.replace(hour=15, minute=30, second=0, microsecond=0)

if ist_now < market_open:
    status_label = "🔴 MARKET OPENS IN"
    diff = market_open - ist_now
elif ist_now > market_close:
    status_label = "🔴 MARKET CLOSED"
    diff = timedelta(seconds=0) # Reset or calculate tomorrow's open
else:
    status_label = "🟢 MARKET CLOSES IN"
    diff = market_close - ist_now

# Format countdown timer
hours, remainder = divmod(diff.seconds, 3600)
minutes, seconds = divmod(remainder, 60)
countdown_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
if ist_now > market_close:
    countdown_str = "--h --m --s"

# --- 3. PREMIUM COMPACT UI CSS ---
st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 0rem; max-width: 800px; }
        
        /* Top Clock & Countdown Header */
        .header-panel {
            display: flex;
            justify-content: space-between;
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 15px 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }
        .time-box { text-align: left; }
        .countdown-box { text-align: right; }
        .header-label { font-size: 0.7rem; color: #8b949e; text-transform: uppercase; font-weight: 700; letter-spacing: 1px;}
        .header-value { font-size: 1.4rem; font-weight: 800; color: #fff; font-family: monospace; margin-top: 2px;}
        
        /* Square Card Layout */
        @keyframes snapIn {
            0% { opacity: 0; transform: scale(0.95); filter: blur(4px); }
            100% { opacity: 1; transform: scale(1); filter: blur(0); }
        }
        
        .sq-card {
            background-color: #0d1117;
            border-top: 4px solid #00ffcc;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: snapIn 0.3s ease-out forwards;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .sq-card-short {
            border-top-color: #ff3366;
        }
        
        .sq-title-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;}
        .sq-ticker { font-size: 1.2rem; font-weight: 800; color: #fff; margin: 0;}
        .sq-margin { font-size: 0.9rem; font-weight: 700; background: #161b22; padding: 3px 8px; border-radius: 4px; border: 1px solid #30363d;}
        
        .sq-data-row { display: flex; justify-content: space-between; border-bottom: 1px solid #21262d; padding: 6px 0;}
        .sq-data-row:last-child { border-bottom: none; }
        .sq-label { font-size: 0.75rem; color: #8b949e; }
        .sq-val { font-size: 0.85rem; font-weight: 700; color: #c9d1d9; }
        .val-target { color: #00ffcc; font-size: 0.95rem;}
        .val-sl { color: #ff3366; font-size: 0.95rem;}
    </style>
""", unsafe_allow_html=True)

# --- 4. HEADER RENDER ---
st.markdown(f"""
    <div class="header-panel">
        <div class="time-box">
            <div class="header-label">Live Clock (IST)</div>
            <div class="header-value">{current_time_str}</div>
        </div>
        <div class="countdown-box">
            <div class="header-label">{status_label}</div>
            <div class="header-value" style="color: #00ffcc;">{countdown_str}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

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
    sorted_data = live_data.sort_values(by="Margin", ascending=False).head(4) # Get top 4 for a 2x2 grid
    
    # Create the 2 columns
    col1, col2 = st.columns(2)
    
    for index, row in sorted_data.reset_index().iterrows():
        is_short = row["Ticker"] in ["TATASTEEL", "RELIANCE"] # Example split
        card_class = "sq-card sq-card-short" if is_short else "sq-card"
        action = "🔴 SHORT" if is_short else "🟢 LONG"
        m_color = "#ff3366" if is_short else "#00ffcc"
        
        tgt = round(row['CMP'] - (row['ATR'] * 1.5), 2) if is_short else round(row['CMP'] + (row['ATR'] * 1.5), 2)
        sl = round(row['CMP'] + (row['ATR'] * 1.0), 2) if is_short else round(row['CMP'] - (row['ATR'] * 1.0), 2)

        card_html = f"""
        <div class="{card_class}">
            <div class="sq-title-row">
                <p class="sq-ticker">{row['Ticker']}</p>
                <p class="sq-margin" style="color: {m_color};">+{row['Margin']}%</p>
            </div>
            <div class="sq-data-row"><span class="sq-label">Action</span><span class="sq-val">{action}</span></div>
            <div class="sq-data-row"><span class="sq-label">Entry</span><span class="sq-val">₹{row['CMP']}</span></div>
            <div class="sq-data-row"><span class="sq-label">Target</span><span class="sq-val val-target">₹{tgt}</span></div>
            <div class="sq-data-row"><span class="sq-label">Stop</span><span class="sq-val val-sl">₹{sl}</span></div>
        </div>
        """
        
        # Distribute cards evenly between the two columns
        if index % 2 == 0:
            with col1: st.markdown(card_html, unsafe_allow_html=True)
        else:
            with col2: st.markdown(card_html, unsafe_allow_html=True)

elif category == "📦 F&O":
    st.info("F&O Logic Offline.")
elif category == "⏳ LONG TERM":
    st.info("Accumulation Matrix Offline.")

# --- 7. AUTO-REFRESH LOOP ---
time.sleep(1) # Faster refresh for the live clock
st.rerun()
