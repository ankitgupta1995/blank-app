import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# --- 1. SYSTEM INITIALIZATION & LOOP ---
if "run_count" not in st.session_state:
    st.session_state.run_count = 0
st.session_state.run_count += 1

# Hides the default Streamlit sidebar and centers the app for mobile
st.set_page_config(page_title="AI Quant Live", layout="centered", initial_sidebar_state="collapsed")

# --- 2. PREMIUM UI & ANIMATION CSS ---
st.markdown("""
    <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
        
        /* Thanos Snap / Materialize Animation */
        @keyframes snapIn {
            0% { opacity: 0; transform: scale(0.95) translateY(10px); filter: blur(4px); }
            100% { opacity: 1; transform: scale(1) translateY(0); filter: blur(0); }
        }
        
        .signal-card {
            background-color: #0d1117;
            border-left: 4px solid #00ffcc;
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            animation: snapIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
        }
        .signal-card-short {
            background-color: #0d1117;
            border-left: 4px solid #ff3366;
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            animation: snapIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
        }
        
        .profit-badge {
            background: linear-gradient(135deg, #00ffcc 0%, #0099ff 100%);
            color: #000;
            padding: 4px 12px;
            font-weight: 800;
            font-size: 1.1rem;
            border-radius: 4px;
            float: right;
        }
        .profit-badge-short {
            background: linear-gradient(135deg, #ff3366 0%, #ff0033 100%);
            color: #fff;
            padding: 4px 12px;
            font-weight: 800;
            font-size: 1.1rem;
            border-radius: 4px;
            float: right;
        }
        
        .time-container {
            display: flex;
            justify-content: space-between;
            background-color: #161b22;
            padding: 8px;
            border-radius: 6px;
            margin: 12px 0;
            border: 1px solid #30363d;
        }
        .time-block { text-align: center; width: 33%; }
        .time-label { font-size: 0.65rem; color: #8b949e; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }
        .time-value { font-size: 0.9rem; font-weight: 700; color: #c9d1d9; margin-top: 2px; }
        
        .price-table { width: 100%; border-collapse: collapse; margin-top: 8px; }
        .price-table td { padding: 8px 0px; border-bottom: 1px solid #21262d; font-size: 0.9rem; color: #8b949e; }
        .price-target { font-weight: 800; color: #00ffcc; font-size: 1.1rem; }
        .price-sl { font-weight: 800; color: #ff3366; font-size: 1.1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Institutional Command")
st.caption(f"Status: LIVE | Compliance: <10 OPS | Cycle: #{st.session_state.run_count}")

# --- 3. LIVE TAPE (CHART) ---
if "price_history" not in st.session_state:
    st.session_state.price_history = [23470, 23370, 23340, 23410, 23490, 23590, 23620, 23640, 23609]

next_tick = round(st.session_state.price_history[-1] + np.random.uniform(-4.5, 5.5), 2)
st.session_state.price_history.append(next_tick)
if len(st.session_state.price_history) > 15:
    st.session_state.price_history.pop(0)

fig = go.Figure()
fig.add_trace(go.Scatter(y=st.session_state.price_history, mode='lines+markers', line=dict(color='#00ffcc', width=2), marker=dict(size=6, color='#fff')))
fig.update_layout(
    margin=dict(l=0, r=0, t=5, b=5), 
    height=120, 
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=False, showticklabels=False, zeroline=False), 
    yaxis=dict(showgrid=True, gridcolor="#21262d", zeroline=False)
)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- 4. ENGINE CATEGORY TOGGLE ---
category = st.radio("Mode:", ["⚡ INTRADAY", "📦 F&O", "⏳ LONG TERM"], horizontal=True, label_visibility="collapsed")
st.markdown("<br>", unsafe_allow_html=True)

# --- 5. DATA SIMULATION (REPLACE WITH BROKER API LATER) ---
@st.cache_data(ttl=2)
def fetch_market_stream():
    stocks = ["TECHM", "INFY", "TATASTEEL", "SBIN", "RELIANCE"]
    base_prices = {"TECHM": 1428.00, "INFY": 1129.70, "TATASTEEL": 205.20, "SBIN": 832.00, "RELIANCE": 2462.00}
    atrs = {"TECHM": 26.0, "INFY": 19.0, "TATASTEEL": 5.1, "SBIN": 13.0, "RELIANCE": 38.0}
    
    times = {
        "TECHM": {"entry": "14:25", "exit": "15:10"},
        "INFY": {"entry": "14:35", "exit": "15:15"},
        "TATASTEEL": {"entry": "14:40", "exit": "15:15"},
        "SBIN": {"entry": "14:45", "exit": "15:20"},
        "RELIANCE": {"entry": "14:50", "exit": "15:25"}
    }
    
    matrix = []
    for s in stocks:
        tick = np.random.uniform(-0.004, 0.005) * base_prices[s]
        cmp = round(base_prices[s] + tick, 2)
        margin = round((atrs[s] * 1.5) / cmp * 100, 2)
        
        matrix.append({
            "Ticker": s, "CMP": cmp, "ATR": atrs[s], "Margin": margin,
            "EntryTime": times[s]["entry"], "ExitTime": times[s]["exit"]
        })
    return pd.DataFrame(matrix)

live_data = fetch_market_stream()

# --- 6. RENDER CARDS ---
if category == "⚡ INTRADAY":
    sorted_data = live_data.sort_values(by="Margin", ascending=False)
    for _, row in sorted_data.head(3).iterrows():
        is_short = row["Ticker"] == "TATASTEEL"
        b_style = "profit-badge-short" if is_short else "profit-badge"
        c_style = "signal-card-short" if is_short else "signal-card"
        action = "🔴 PUT (SHORT)" if is_short else "🟢 CALL (LONG)"
        
        tgt = round(row['CMP'] - (row['ATR'] * 1.5), 2) if is_short else round(row['CMP'] + (row['ATR'] * 1.5), 2)
        sl = round(row['CMP'] + (row['ATR'] * 1.0), 2) if is_short else round(row['CMP'] - (row['ATR'] * 1.0), 2)

        st.markdown(f"""
            <div class="{c_style}">
                <div class="{b_style}">+{row['Margin']}%</div>
                <h3 style='margin:0; color:#fff;'>{row['Ticker']}</h3>
                
                <div class="time-container">
                    <div class="time-block"><div class="time-label">Status</div><div class="time-value" style="color:#00ffcc;">ACTIVE</div></div>
                    <div class="time-block" style="border-left: 1px solid #30363d; border-right: 1px solid #30363d;">
                        <div class="time-label">Entry</div><div class="time-value">{row['EntryTime']}</div>
                    </div>
                    <div class="time-block"><div class="time-label">Cutoff</div><div class="time-value" style="color:#ff3366;">{row['ExitTime']}</div></div>
                </div>
                
                <table class="price-table">
                    <tr><td>Direction</td><td style="font-weight:700; text-align:right; color:#c9d1d9;">{action}</td></tr>
                    <tr><td>Trigger Price</td><td style="font-weight:700; text-align:right; color:#c9d1d9;">₹{row['CMP']}</td></tr>
                    <tr><td>Target Level</td><td class="price-target" style="text-align:right;">₹{tgt}</td></tr>
                    <tr><td>Hard Stop</td><td class="price-sl" style="text-align:right;">₹{sl}</td></tr>
                </table>
            </div>
        """, unsafe_allow_html=True)

elif category == "📦 F&O":
    sorted_data = live_data.sort_values(by="CMP", ascending=True)
    for _, row in sorted_data.head(2).iterrows():
        fo_margin = round(row['Margin'] * 4.6, 1)
        st.markdown(f"""
            <div class="signal-card">
                <div class="profit-badge">+{fo_margin}%</div>
                <h3 style='margin:0; color:#fff;'>{row['Ticker']} Spread</h3>
                
                <div class="time-container">
                    <div class="time-block"><div class="time-label">Entry</div><div class="time-value">14:30 Today</div></div>
                    <div class="time-block" style="border-left: 1px solid #30363d; border-right: 1px solid #30363d;">
                        <div class="time-label">Type</div><div class="time-value" style="color:#00ffcc;">Credit</div>
                    </div>
                    <div class="time-block"><div class="time-label">Expiry</div><div class="time-value" style="color:#ff3366;">Thursday</div></div>
                </div>
                
                <table class="price-table">
                    <tr><td>Setup</td><td style="font-weight:700; text-align:right; color:#00ffcc;">Sell ₹{int(row['CMP'] - row['ATR'])} PE / Buy ₹{int(row['CMP'] - (row['ATR']*2))} PE</td></tr>
                    <tr><td>Invalidation</td><td class="price-sl" style="text-align:right;">₹{round(row['CMP'] - row['ATR'], 2)}</td></tr>
                </table>
            </div>
        """, unsafe_allow_html=True)

elif category == "⏳ LONG TERM":
    st.info("Accumulation Matrix Offline During Intraday Volatility Spike.")

# --- 7. AUTO-REFRESH LOOP ---
time.sleep(4)
st.rerun()
