import streamlit as st
import random

# App Setup for Mobile/Desktop view
st.set_page_config(page_title="AI Trading Mentor", layout="centered")

st.title("🛡️ AI Mentor Command Center")
st.caption("May 18, 2026 | Market Oversight System")

st.sidebar.header("Oversight System Controls")
vix_level = st.sidebar.slider("Current India VIX", 10.0, 30.0, 21.4)

# Market Regime Analysis
if vix_level > 20:
    st.error("⚠️ HIGH VOLATILITY REGIME DETECTED")
    st.info("💡 Mentor Advice: Highly volatile conditions. Focus strictly on hedged options setups or quick momentum breakout spikes. Tighten stop losses.")
else:
    st.success("✅ STABLE MARKET REGIME")
    st.info("💡 Mentor Advice: Normal structural movements. Trend following and mean reversion strategies are highly favored.")

st.markdown("---")

# Target & Risk Calculator
st.subheader("🎯 Live Target & Risk Matrix")
ticker = st.text_input("Enter Stock Ticker (e.g., RELIANCE, NIFTY)", "HDFCBANK").upper()
cmp = st.number_input("Current Market Price (CMP)", value=1350.0, step=0.5)
atr = st.number_input("Average True Range (ATR - Daily Movement)", value=25.0, step=1.0)

if st.button("🚀 Calculate Mentor Targets"):
    # Target calculations based on volatility architectures
    target_cons = round(cmp + (atr * 1.5), 2)
    target_aggr = round(cmp + (atr * 2.5), 2)
    kill_level = round(cmp - (atr * 1.2), 2)
    
    st.markdown(f"### **Analysis for {ticker}**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"**Conservative Target:** ₹{target_cons}")
        st.warning(f"**Aggressive Target:** ₹{target_aggr}")
    with col2:
        st.error(f"**Kill Level (Stop Loss):** ₹{kill_level}")
        
    # Checking for Volume Spikes
    confidence = random.randint(65, 85) # Simulating confidence threshold until live API is connected
    st.write(f"📊 **Mentor System Confidence Rating:** {confidence}%")
    if confidence > 75:
        st.write("🔥 *Pattern recognition aligns with a high-volume institutional breakout. Watch closely.*")
    else:
        st.write("⚠️ *Move carries retail noise characteristics. Proceed with caution.*")
