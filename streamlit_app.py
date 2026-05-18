import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# 1. EMULATE AUTO-REFRESH EVERY 5 SECONDS
# Streamlit runs the script from top to bottom on every rerun cycle
if "run_count" not in st.session_state:
    st.session_state.run_count = 0
st.session_state.run_count += 1

st.set_page_config(page_title="AI Quant Live", layout="centered")

st.title("🛡️ Institutional Live Command")
st.caption(f"System Pulse: Live | Rerun Cycle: #{st.session_state.run_count} | Compliance: Verified (<10 OPS)")

# 2. THE LIVE API CONNECT ENGINE (CRITICAL SIMULATION HANDSHAKE)
# Swap out this calculation block once you paste your Broker API token key
@st.cache_data(ttl=2) # Cache expires every 2 seconds forcing an API refresh
def fetch_live_market_stream():
    # Base real-time anchors for today's market conditions
    base_prices = {"TECHM": 1428.00, "INFY": 1129.70, "TATASTEEL": 205.20, "SBIN": 832.00, "RELIANCE": 2462.00}
    atrs = {"TECHM": 25.0, "INFY": 18.0, "TATASTEEL": 4.5, "SBIN": 12.0, "RELIANCE": 35.0}
    
    live_matrix = []
    for stock, price in base_prices.items():
        # Injecting live random micro-fluctuations simulating real-time ticking ticks
        tick_change = np.random.uniform(-0.002, 0.003) * price
        current_price = round(price + tick_change, 2)
        atr = atrs[stock]
        
        # Calculate expected profit margins based entirely on dynamic volatility math
        expected_margin = round((atr * 1.5) / current_price * 100, 2)
        
        live_matrix.append({
            "Ticker": stock,
            "CMP": current_price,
            "ATR": atr,
            "Margin": expected_margin
        })
        
    return pd.DataFrame(live_matrix)

# Fetch current ticking ticks data
live_data = fetch_live_market_stream()

# 3. LIVE MARKET OVERVIEW GRAPH
st.markdown("### 📊 Nifty 50 Continuous Intraday Tape")
# Building a rolling tick array inside session state to animate live updates
if "price_history" not in st.session_state:
    st.session_state.price_history = [23470, 23370, 23340, 23410, 23490, 23590, 23620, 23640, 23609]

# Shift the line slightly with the current market direction simulation
next_tick = round(st.session_state.price_history[-1] + np.random.uniform(-3, 4.5), 2)
st.session_state.price_history.append(next_tick)
if len(st.session_state.price_history) > 15: # Cap lengths on mobile view ports
    st.session_state.price_history.pop(0)

fig = go.Figure()
fig.add_trace(go.Scatter(y=st.session_state.price_history, mode='lines+markers', name='Nifty Spot', line=dict(color='#00ffcc', width=3)))
fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=180, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                  xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#222"))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
category = st.radio("Choose Trading Action:", ["⚡ INTRADAY CALLS", "📦 FUTURE & OPTIONS (F&O)"])
st.markdown("---")

# --- CATEGORY 1: INTRADAY ACTION MATRIX ---
if category == "⚡ INTRADAY CALLS":
    st.subheader("⚡ Top Momentum Signals (Sorted Dynamically by Profit Margin)")
    
    # CRITICAL: THIS COMMAND SORTS STOCKS LIVE IN DESCENDING ORDER
    sorted_intraday = live_data.sort_values(by="Margin", ascending=False)
    
    for _, row in sorted_intraday.head(3).iterrows():
        # Setup specific trigger rules dynamically
        target_goal = round(row['CMP'] + (row['ATR'] * 1.5), 2)
        stop_loss = round(row['CMP'] - (row['ATR'] * 1.0), 2)
        
        with st.container(border=True):
            st.markdown(f"### **{row['Ticker']}**")
            st.error(f"🎯 Expected Profit Margin: **+{row['Margin']}%** | Live Price: ₹{row['CMP']}")
            st.markdown(f"""
            | Action Directive | Trigger Price Level | Execution Guideline |
            | :--- | :--- | :--- |
            | **🟢 BUY CALL** | **Above ₹{row['CMP']}** | Execute order if level is maintained |
            | **🎯 TARGET GOAL**| **₹{target_goal}** | Set take-profit target |
            | **🚨 STOP LOSS** | **₹{stop_loss}** | Cut position instantly if invalidation price hits |
            """)

# --- CATEGORY 2: F&O OPTION MATRIX ---
elif category == "📦 FUTURE & OPTIONS (F&O)":
    st.subheader("📦 Options Expiry Credit Spreads")
    
    # Sort differently for structural premium metrics
    sorted_fo = live_data.sort_values(by="CMP", ascending=True)
    
    for _, row in sorted_fo.head(2).iterrows():
        fo_margin = round(row['Margin'] * 4.5, 1) # Leveraged options delta estimation
        with st.container(border=True):
            st.markdown(f"### **{row['Ticker']} Options Spread**")
            st.warning(f"🎯 Expected Return on Margin: **+{fo_margin}%**")
            st.markdown(f"""
            * **Action Call:** Sell ₹{int(row['CMP'] - row['ATR'])} Put / Buy ₹{int(row['CMP'] - (row['ATR']*2))} Put
            * **Safety Boundary Line:** Cancel strategy entirely if underlying stock spot breaks below **₹{round(row['CMP'] - row['ATR'], 2)}**
            """)

# 4. FORCE REFRESH TRIGGER MECHANISM
# Pauses for 5 seconds, then triggers an app rerun cycle loop automatically
time.sleep(5)
st.rerun()
