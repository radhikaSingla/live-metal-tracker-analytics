import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="Advanced Live Metal Tracker", layout="wide")

# --- PREMIUM METALLIC THEME (CUSTOM CSS) ---
st.markdown("""
    <style>
    .reportview-container {
        background: linear-gradient(135deg, #1f1f2e, #11111a);
    }
    .metric-box {
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        margin-bottom: 10px;
        text-align: center;
    }
    .up-effect {
        border: 2px solid #00ff88;
        background: rgba(0, 255, 136, 0.05);
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.2);
    }
    .down-effect {
        border: 2px solid #ff4444;
        background: rgba(255, 68, 68, 0.05);
        box-shadow: 0 0 15px rgba(255, 68, 68, 0.2);
    }
    .gold-text { color: #FFD700; font-weight: bold; }
    .silver-text { color: #C0C0C0; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title(" Premium Real-Time Gold & Silver Analytics Dashboard")
st.write("An enterprise-grade analytics terminal with smart UI background indicators and responsive design.")

# History maintain karne ke liye session state
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
        
        st.session_state.gold_history.append(g_price)
        st.session_state.silver_history.append(s_price)
        st.session_state.time_history.append(current_time)
        
        if len(st.session_state.gold_history) > 20:
            st.session_state.gold_history.pop(0)
            st.session_state.silver_history.pop(0)
            st.session_state.time_history.pop(0)
            
        # Delta/Change Calculation
        g_delta = round(g_price - st.session_state.gold_history[0], 2) if len(st.session_state.gold_history) > 1 else 0
        s_delta = round(s_price - st.session_state.silver_history[0], 2) if len(st.session_state.silver_history) > 1 else 0
        
        g_sma = round(sum(st.session_state.gold_history) / len(st.session_state.gold_history), 2)
        s_sma = round(sum(st.session_state.silver_history) / len(st.session_state.silver_history), 2)

        # Dynamic Color Glow Class Selection
        gold_class = "up-effect" if g_delta >= 0 else "down-effect"
        silver_class = "up-effect" if s_delta >= 0 else "down-effect"

        with placeholder.container():
            # --- ROW 1: METRICS WITH DYNAMIC EFFECTS ---
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                    <div class="metric-box {gold_class}">
                        <h4 class="gold-text">🏆 Live Gold</h4>
                        <h2>${g_price}</h2>
                        <p style="color: {'#00ff88' if g_delta >= 0 else '#ff4444'}">{g_delta} USD</p>
                    </div>
                """, unsafe_allow_html=True)
                
            with col2:
                st.markdown(f"""
                    <div class="metric-box" style="border: 1px solid #FFD700; background: rgba(255,215,0,0.02);">
                        <h4 class="gold-text">📊 Session Avg (SMA)</h4>
                        <h2>${g_sma}</h2>
                        <p style="color: gray;">Current Session</p>
                    </div>
                """, unsafe_allow_html=True)
                
            with col3:
                st.markdown(f"""
                    <div class="metric-box {silver_class}">
                        <h4 class="silver-text">🥈 Live Silver</h4>
                        <h2>${s_price}</h2>
                        <p style="color: {'#00ff88' if s_delta >= 0 else '#ff4444'}">{s_delta} USD</p>
                    </div>
                """, unsafe_allow_html=True)
                
            with col4:
                st.markdown(f"""
                    <div class="metric-box" style="border: 1px solid #C0C0C0; background: rgba(192,192,192,0.02);">
                        <h4 class="silver-text">📊 Session Avg (SMA)</h4>
                        <h2>${s_sma}</h2>
                        <p style="color: gray;">Current Session</p>
                    </div>
                """, unsafe_allow_html=True)
                
            st.markdown("---")
            
            # --- ROW 2: REAL-TIME PREMIUM CHARTS ---
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader("Gold Price Real-time Trend")
                fig_g = go.Figure()
                fig_g.add_trace(go.Scatter(x=st.session_state.time_history, y=st.session_state.gold_history,
                                           mode='lines+markers', name='Gold', line=dict(color='#FFD700', width=3)))
                fig_g.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300, template="plotly_dark",
                                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_g, use_container_width=True)
                
            with chart_col2:
                st.subheader("Silver Price Real-time Trend")
                fig_s = go.Figure()
                fig_s.add_trace(go.Scatter(x=st.session_state.time_history, y=st.session_state.silver_history,
                                           mode='lines+markers', name='Silver', line=dict(color='#C0C0C0', width=3)))
                fig_s.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300, template="plotly_dark",
                                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_s, use_container_width=True)
                
            st.caption(f"🔄 Live Metallic Terminal Active. Last Refresh: {current_time}")

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        
    time.sleep(5)