import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# 1. EMULATE AUTO-REFRESH EVERY 5 SECONDS
if "run_count" not in st.session_state:
    st.session_state.run_count = 0
st.session_state.run_count += 1

st.set_page_config(page_title="AI Quant Live", layout="centered")

# Custom CSS for Premium Block UI Cards and Thanos-like snappy transitions
st.markdown("""
    <style>
        /* Base App Container Tweaks */
        .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
        
        /* Premium Card Layout */
        .signal-card {
            background-color: #111622;
            border-left: 5px solid #00ffcc;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            transition: all 0.4s ease-in-out;
        }
        .signal-card-short {
            background-color: #111622;
            border-left: 5px solid #ff3366;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            transition: all 0.4s ease-in-out;
        }
        
        /* High-Visibility Profit Highlight */
        .profit-badge {
            background: linear-gradient(135deg, #00ffcc 0%, #0099ff 100%);
            color: #000000;
            padding: 6px 14px;
            font-weight: 800;
            font-size: 1.25rem;
            border-radius: 6px;
            float: right;
            margin-top: -5px;
        }
        .profit-badge-short {
            background: linear-gradient(135deg, #ff3366 0%, #ff0033 100%);
            color: #ffffff;
            padding: 6px 14px;
            font-weight: 800;
            font-size: 1.25rem;
            border-radius: 6px;
            float: right;
            margin-top: -5px;
        }
        
        /* Timing Block Labels */
        .time-container {
            display: flex;
            justify-content: space-between;
            background-color: #0b0e14;
            padding: 10px;
            border-radius: 6px;
            margin-top: 12px;
            margin-bottom: 12px;
            border: 1px solid #222;
        }
        .time-block { text-align: center; width: 33%; }
        .time-label { font-size: 0.75rem; color: #888; text-transform: uppercase; font-weight: 600; }
        .time-value { font-size: 0.95rem; font-weight: 700; color: #fff; margin-top: 2px; }
        
        /* Clean Tables */
        .price-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .price-table td { padding: 6px 0px; border-bottom: 1px solid #222; font-size: 0.9rem; }
        .price-target { font-weight: 700; color: #00ffcc; font-size: 1.05rem; }
        .price-sl { font-weight: 700; color: #ff3366; font-size: 1.05rem; }
    </style>
""", unsafe_with_html_safe=True)

st.title("🛡️ Direct Execution Command Center")
st.caption(f"Live Feed Active | Cycle: #{st.session_state.run_count} | Auto-Sorting Engine")

# 2. CONTINUOUS INTRADAY TAPE (NIFTY 50 GRAPH)
if "price_history" not in st.session_state:
    st.session_state.price_history = [23470, 23370, 23340, 23410, 23490, 23590, 23620, 23640, 23609]

next_tick = round(st.session_state.price_history[-1] + np.random.uniform(-4, 5.5), 2)
st.session_state.price_history.append(next_tick)
if len(st.session_state.price_history) > 15:
    st.session_state.price_history.pop(0)

fig = go.Figure()
fig.add_trace(go.Scatter(y=st.session_state.price_history, mode='lines+markers', name='Nifty Spot', line=dict(color='#00ffcc', width=3)))
fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=140, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                  xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=True, gridcolor="#222"))
st.plotly_chart(fig, use_container_width=True)

# SELECTION HUB
category = st.radio("Select View:", ["⚡ INTRADAY CALLS", "📦 FUTURE & OPTIONS (F&O)", "⏳ LONG TERM HOLDINGS"], label_visibility="collapsed")
st.markdown("<br>", unsafe_with_html_safe=True)

# 3. LIVE MATHEMATICAL EXCHANGE SIMULATION ENGINE
@st.cache_data(ttl=2)
def fetch_live_market_stream():
    stocks = ["TECHM", "INFY", "TATASTEEL", "SBIN", "RELIANCE"]
    base_prices = {"TECHM": 1428.00, "INFY": 1129.70, "TATASTEEL": 205.20, "SBIN": 832.00, "RELIANCE": 2462.00}
    atrs = {"TECHM": 26.0, "INFY": 19.0, "TATASTEEL": 5.1, "SBIN": 13.0, "RELIANCE": 38.0}
    
    # Pre-assigned structured times to keep interface pristine
    times = {
        "TECHM": {"entry": "14:25", "exit": "15:10"},
        "INFY": {"entry": "14:35", "exit": "15:15"},
        "TATASTEEL": {"entry": "14:40", "exit": "15:15"},
        "SBIN": {"entry": "14:45", "exit": "15:20"},
        "RELIANCE": {"entry": "14:50", "exit": "15:25"}
    }
    
    matrix = []
    for s in stocks:
        tick_fluctuation = np.random.uniform(-0.003, 0.004) * base_prices[s]
        cmp = round(base_prices[s] + tick_fluctuation, 2)
        margin = round((atrs[s] * 1.5) / cmp * 100, 2)
        
        matrix.append({
            "Ticker": s, "CMP": cmp, "ATR": atrs[s], "Margin": margin,
            "EntryTime": times[s]["entry"], "ExitTime": times[s]["exit"]
        })
    return pd.DataFrame(matrix)

live_data = fetch_live_market_stream()

# --- ENGINE VIEW CATEGORIES ---
if category == "⚡ INTRADAY CALLS":
    # CRITICAL SORTING: Highest profit always climbs to the top card block
    sorted_data = live_data.sort_values(by="Margin", ascending=False)
    
    for _, row in sorted_data.head(3).iterrows():
        is_short = row["Ticker"] == "TATASTEEL"
        badge_style = "profit-badge-short" if is_short else "profit-badge"
        card_style = "signal-card-short" if is_short else "signal-card"
        action_label = "🔴 PUT" if is_short else "🟢 CALL"
        
        target = round(row['CMP'] - (row['ATR'] * 1.5), 2) if is_short else round(row['CMP'] + (row['ATR'] * 1.5), 2)
        sl = round(row['CMP'] + (row['ATR'] * 1.0), 2) if is_short else round(row['CMP'] - (row['ATR'] * 1.0), 2)

        # HTML Block UI Generation Loop
        st.markdown(f"""
            <div class="{card_style}">
                <div class="{badge_style}">GAINS: +{row['Margin']}%</div>
                <h2 style='margin:0; color:#fff; font-size:1.5rem;'>{row['Ticker']}</h2>
                <div style='color:#888; font-size:0.9rem; margin-top:2px;'>Live Price: ₹{row['CMP']}</div>
                
                <div class="time-container">
                    <div class="time-block"><div class="time-label">Scan Match</div><div class="time-value">LIVE</div></div>
                    <div class="time-block" style="border-left: 1px solid #222; border-right: 1px solid #222;"><div class="time-label">Entry Window</div><div class="time-value" style="color:#00ffcc;">{row['EntryTime']}</div></div>
                    <div class="time-block"><div class="time-label">Hard Cutoff</div><div class="time-value" style="color:#ff3366;">{row['ExitTime']}</div></div>
                </div>
                
                <table class="price-table">
                    <tr><td>Action Direction:</td><td style="font-weight:700; text-align:right;">{action_label}</td></tr>
                    <tr><td>Execution Trigger:</td><td style="font-weight:700; text-align:right;">₹{row['CMP']}</td></tr>
                    <tr><td>Target Goal Level:</td><td class="price-target" style="text-align:right;">₹{target}</td></tr>
                    <tr><td>Invalidation Floor:</td><td class="price-sl" style="text-align:right;">₹{sl}</td></tr>
                </table>
            </div>
        """, unsafe_with_html_safe=True)

elif category == "📦 FUTURE & OPTIONS (F&O)":
    sorted_data = live_data.sort_values(by="CMP", ascending=True)
    for _, row in sorted_data.head(2).iterrows():
        fo_margin = round(row['Margin'] * 4.6, 1)
        st.markdown(f"""
            <div class="signal-card">
                <div class="profit-badge">EXPIRY GAINS: +{fo_margin}%</div>
                <h2 style='margin:0; color:#fff; font-size:1.5rem;'>{row['Ticker']} Options Spread</h2>
                
                <div class="time-container">
                    <div class="time-block"><div class="time-label">Entry Action</div><div class="time-value">14:30 Today</div></div>
                    <div class="time-block" style="border-left: 1px solid #222; border-right: 1px solid #222;"><div class="time-label">Strategy Setup</div><div class="time-value" style="color:#00ffcc;">Credit Spread</div></div>
                    <div class="time-block"><div class="time-label">Settlement</div><div class="time-value" style="color:#ff3366;">Thu Expiry</div></div>
                </div>
                
                <table class="price-table">
                    <tr><td>Option Setup:</td><td style="font-weight:700; text-align:right; color:#00ffcc;">Sell ₹{int(row['CMP'] - row['ATR'])} PE / Buy ₹{int(row['CMP'] - (row['ATR']*2))} PE</td></tr>
                    <tr><td>Safety Invalidation Boundary:</td><td class="price-sl" style="text-align:right;">₹{round(row['CMP'] - row['ATR'], 2)}</td></tr>
                </table>
            </div>
        """, unsafe_with_html_safe=True)

elif category == "⏳ LONG TERM HOLDINGS":
    # Multipliers representing long-horizon yield structures
    lt_targets = {"TECHM": 23.5, "INFY": 18.0, "TATASTEEL": 14.2, "SBIN": 19.4, "RELIANCE": 12.5}
    sorted_data = live_data.sort_values(by="Ticker", ascending=True)
    
    for _, row in sorted_data.head(2).iterrows():
        st.markdown(f"""
            <div class="signal-card">
                <div class="profit-badge" style="background: linear-gradient(135deg, #00ffcc 0%, #a155ff 100%);">TARGET: +{lt_targets[row['Ticker']]}%</div>
                <h2 style='margin:0; color:#fff; font-size:1.5rem;'>{row['Ticker']} Core Block</h2>
                
                <div class="time-container">
                    <div class="time-block"><div class="time-label">Entry Horizon</div><div class="time-value" style="color:#00ffcc;">Panic Dips Week</div></div>
                    <div class="time-block" style="border-left: 1px solid #222; border-right: 1px solid #222;"><div class="time-label">Hold Timeline</div><div class="time-value">6-12 Months</div></div>
                    <div class="time-block"><div class="time-label">Allocation Risk</div><div class="time-value" style="color:#00ffcc;">Conservative</div></div>
                </div>
                
                <table class="price-table">
                    <tr><td>Accumulation Buy Window:</td><td style="font-weight:700; text-align:right; color:#00ffcc;">₹{round(row['CMP']*0.97, 2)} - ₹{row['CMP']}</td></tr>
                    <tr><td>Structural Sale Target:</td><td class="price-target" style="text-align:right;">₹{round(row['CMP'] * (1 + lt_targets[row['Ticker']]/100), 2)}</td></tr>
                </table>
            </div>
        """, unsafe_with_html_safe=True)

# 4. LOOP CONTROL RE-RUNNER
time.sleep(5)
st.rerun()
