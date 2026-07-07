import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="Advanced Live Metal Tracker", layout="wide")
st.title("📈 Advanced Real-Time Gold & Silver Analytics Dashboard")
st.write("This is an enterprise-grade live data streaming dashboard with dynamic KPIs and real-time trend graphs.")

# History maintain karne ke liye dataframes initialize karna
if 'gold_history' not in st.session_state:
    st.session_state.gold_history = []
if 'silver_history' not in st.session_state:
    st.session_state.silver_history = []
if 'time_history' not in st.session_state:
    st.session_state.time_history = []

def get_live_prices():
    gold = yf.Ticker("GC=F")
    silver = yf.Ticker("SI=F")
    gold_price = round(gold.history(period="1d")['Close'].iloc[-1], 2)
    silver_price = round(silver.history(period="1d")['Close'].iloc[-1], 2)
    return gold_price, silver_price

placeholder = st.empty()

# Live Data Stream Loop
while True:
    try:
        g_price, s_price = get_live_prices()
        current_time = pd.Timestamp.now().strftime('%H:%M:%S')
        
        # History mein data append karna real-time chart ke liye
        st.session_state.gold_history.append(g_price)
        st.session_state.silver_history.append(s_price)
        st.session_state.time_history.append(current_time)
        
        # Data limit tak rakhna (Sirf pichle 20 data points dikhane ke liye takki graph clean rahe)
        if len(st.session_state.gold_history) > 20:
            st.session_state.gold_history.pop(0)
            st.session_state.silver_history.pop(0)
            st.session_state.time_history.pop(0)
            
        # --- ADVANCED KPI CALCULATIONS ---
        # 1. Delta/Change Calculation (Pehle price ke mukable kitna change hua)
        g_delta = round(g_price - st.session_state.gold_history[0], 2) if len(st.session_state.gold_history) > 1 else 0
        s_delta = round(s_price - st.session_state.silver_history[0], 2) if len(st.session_state.silver_history) > 1 else 0
        
        # 2. Moving Average KPI (Simple Moving Average of current session)
        g_sma = round(sum(st.session_state.gold_history) / len(st.session_state.gold_history), 2)
        s_sma = round(sum(st.session_state.silver_history) / len(st.session_state.silver_history), 2)

        with placeholder.container():
            # --- ROW 1: METRICS & KPIs ---
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(label="🏆 Live Gold Price", value=f"${g_price}", delta=f"{g_delta} USD")
            with col2:
                st.metric(label="📊 Gold Session Avg (SMA)", value=f"${g_sma}")
            with col3:
                st.metric(label="🥈 Live Silver Price", value=f"${s_price}", delta=f"{s_delta} USD")
            with col4:
                st.metric(label="📊 Silver Session Avg (SMA)", value=f"${s_sma}")
                
            st.markdown("---")
            
            # --- ROW 2: REAL-TIME PREMIUM CHARTS (Using Plotly) ---
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader("Gold Price Real-time Trend")
                fig_g = go.Figure()
                fig_g.add_trace(go.Scatter(x=st.session_state.time_history, y=st.session_state.gold_history,
                                           mode='lines+markers', name='Gold', line=dict(color='#FFD700', width=3)))
                fig_g.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300, template="plotly_dark")
                st.plotly_chart(fig_g, use_container_width=True)
                
            with chart_col2:
                st.subheader("Silver Price Real-time Trend")
                fig_s = go.Figure()
                fig_s.add_trace(go.Scatter(x=st.session_state.time_history, y=st.session_state.silver_history,
                                           mode='lines+markers', name='Silver', line=dict(color='#C0C0C0', width=3)))
                fig_s.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300, template="plotly_dark")
                st.plotly_chart(fig_s, use_container_width=True)
                
            st.caption(f"🔄 Live Streaming Active. Last Refresh: {current_time}")

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        
    time.sleep(5)