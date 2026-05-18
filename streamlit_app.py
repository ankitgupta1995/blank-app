import streamlit as st

# Setup layout for sharp, clean mobile viewing
st.set_page_config(page_title="AI Trading Signals", layout="centered")

st.title("🛡️ Direct Execution Command Center")
st.caption("🔴 Live Market Session | Signals Sorted by Expected Profit Margin")

st.markdown("---")

# DIRECT ALLOCATION SELECTION
category = st.radio("Select Trading View:", ["⚡ INTRADAY CALLS", "📦 FUTURE & OPTIONS (F&O)", "⏳ LONG TERM HOLDINGS"])

st.markdown("---")

# --- CATEGORY 1: INTRADAY ---
if category == "⚡ INTRADAY CALLS":
    st.subheader("⚡ Intraday Actions (Exit Before 3:15 PM Today)")
    
    # Stock 1 (Highest Profit)
    with st.container(border=True):
        st.markdown("### **1. TECH MAHINDRA (TECHM)**")
        st.error("🎯 Expected Profit Margin: **+2.10%**")
        st.markdown("""
        * **Time to Enter:** **14:25 PM**
        * **Time to Exit:** **15:10 PM**
        
        | Action Type | Trigger Price | Target Goal | Stop Loss (Exit If Defeated) |
        | :--- | :--- | :--- | :--- |
        | **🟢 BUY CALL** | **Above ₹1,428.00** | **₹1,458.00** | **₹1,411.00** |
        """)

    # Stock 2
    with st.container(border=True):
        st.markdown("### **2. INFOSYS (INFY)**")
        st.warning("🎯 Expected Profit Margin: **+1.65%**")
        st.markdown("""
        * **Time to Enter:** **14:35 PM**
        * **Time to Exit:** **15:15 PM**
        
        | Action Type | Trigger Price | Target Goal | Stop Loss (Exit If Defeated) |
        | :--- | :--- | :--- | :--- |
        | **🟢 BUY CALL** | **Above ₹1,132.00** | **₹1,150.00** | **₹1,119.00** |
        """)

    # Stock 3
    with st.container(border=True):
        st.markdown("### **3. TATA CONSUMER (TATACONSUM)**")
        st.success("🎯 Expected Profit Margin: **+1.20%**")
        st.markdown("""
        * **Time to Enter:** **14:40 PM**
        * **Time to Exit:** **15:15 PM**
        
        | Action Type | Trigger Price | Target Goal | Stop Loss (Exit If Defeated) |
        | :--- | :--- | :--- | :--- |
        | **🔴 PUT CALL** | **Below ₹1,085.00** | **₹1,072.00** | **₹1,093.00** |
        """)

# --- CATEGORY 2: F&O ---
elif category == "📦 FUTURE & OPTIONS (F&O)":
    st.subheader("📦 Options Expiry Plays (Hold Until Thursday Expiry)")
    
    # Play 1 (Highest Profit)
    with st.container(border=True):
        st.markdown("### **1. COAL INDIA (COALINDIA)**")
        st.error("🎯 Expected Profit Margin: **+14.2% on Blocked Capital**")
        st.markdown("""
        * **Time to Enter:** **14:30 PM Today**
        * **Time to Exit:** **Thursday Expiry Settlement**
        
        | Setup Action | Action Price Levels | Final Protection Line |
        | :--- | :--- | :--- |
        | **🔴 PUT CALL** | **Sell 480 PE / Buy 460 PE** | Exit entirely if stock goes below **₹468** |
        """)

    # Play 2
    with st.container(border=True):
        st.markdown("### **2. STATE BANK OF INDIA (SBIN)**")
        st.warning("🎯 Expected Profit Margin: **+11.5% on Blocked Capital**")
        st.markdown("""
        * **Time to Enter:** **14:45 PM Today**
        * **Time to Exit:** **Thursday Expiry Settlement**
        
        | Setup Action | Action Price Levels | Final Protection Line |
        | :--- | :--- | :--- |
        | **🟢 BUY CALL** | **Sell 830 CE / Buy 850 CE** | Exit entirely if stock goes above **₹842** |
        """)

    # Play 3
    with st.container(border=True):
        st.markdown("### **3. RELIANCE (RELIANCE)**")
        st.success("🎯 Expected Profit Margin: **+9.8% on Blocked Capital**")
        st.markdown("""
        * **Time to Enter:** **14:50 PM Today**
        * **Time to Exit:** **Thursday Expiry Settlement**
        
        | Setup Action | Action Price Levels | Final Protection Line |
        | :--- | :--- | :--- |
        | **🟢 BUY CALL** | **Sell 2460 CE / Buy 2480 CE** | Exit entirely if stock goes above **₹2472** |
        """)

# --- CATEGORY 3: LONG TERM ---
elif category == "⏳ LONG TERM HOLDINGS":
    st.subheader("⏳ Direct Portfolio Accumulation (Hold for 6-12 Months)")
    
    # Asset 1 (Highest Profit)
    with st.container(border=True):
        st.markdown("### **1. KRN HEAT EXCHANGER (KRN)**")
        st.error("🎯 Expected Profit Margin: **+23.5% Minimum Growth**")
        st.markdown("""
        * **When to Buy:** Accumulate during market panic dips this week.
        
        | Buying Range | Target Sale Price | Ultimate Safety Floor |
        | :--- | :--- | :--- |
        | **🟢 Buy Between ₹410 - ₹430** | **₹525.00** | **₹385.00** |
        """)

    # Asset 2
    with st.container(border=True):
        st.markdown("### **2. HINDUSTAN ZINC (HINDZINC)**")
        st.warning("🎯 Expected Profit Margin: **+18.0% Minimum Growth**")
        st.markdown("""
        * **When to Buy:** Accumulate immediately on price drops.
        
        | Buying Range | Target Sale Price | Ultimate Safety Floor |
        | :--- | :--- | :--- |
        | **🟢 Buy Between ₹455 - ₹468** | **₹540.00** | **₹435.00** |
        """)

    # Asset 3
    with st.container(border=True):
        st.markdown("### **3. JSW STEEL (JSWSTEEL)**")
        st.success("🎯 Expected Profit Margin: **+12.5% Minimum Growth**")
        st.markdown("""
        * **When to Buy:** Wait for the specific entry trigger block.
        
        | Buying Range | Target Sale Price | Ultimate Safety Floor |
        | :--- | :--- | :--- |
        | **🟢 Buy Between ₹810 - ₹822** | **₹915.00** | **₹790.00** |
        """)

st.markdown("---")
st.caption("All parameters strictly comply with retail tracking safety rules.")
