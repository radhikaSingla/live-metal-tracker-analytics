"""
MetalPulse — Live Precious Metals Terminal
--------------------------------------------------------------------------
An upgraded, deployment-ready rebuild of the original single-metal-pair
Streamlit dashboard. Key upgrades over the original app:

  * No more blocking `while True` loop — uses Streamlit's native
    `st.fragment(run_every=...)` so the UI stays responsive while it
    auto-refreshes (the old loop froze all widgets and could never be
    stopped cleanly).
  * Tracks 5 metals (Gold, Silver, Platinum, Palladium, Copper) instead
    of just 2, user-selectable from the sidebar.
  * Live prices are cached (st.cache_data) so repeated reruns don't
    hammer Yahoo Finance.
  * Adds analytics the original didn't have: normalized session
    % change comparison, 14-period RSI, a correlation heatmap across
    selected metals, 52-week high/low context, and CSV export of the
    session history.
  * User-configurable price alerts (toast notification when a metal
    crosses a target price).
  * Distinct "obsidian terminal" visual identity instead of the
    generic gradient background.
"""

from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# --------------------------------------------------------------------------
# Page & brand configuration
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="MetalPulse | Live Precious Metals Terminal",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

METALS = {
    "Gold": {"ticker": "GC=F", "color": "#FFD700", "icon": "🥇"},
    "Silver": {"ticker": "SI=F", "color": "#C7CCD6", "icon": "🥈"},
    "Platinum": {"ticker": "PL=F", "color": "#8FD3FE", "icon": "⛏️"},
    "Palladium": {"ticker": "PA=F", "color": "#CEA8FF", "icon": "🔩"},
    "Copper": {"ticker": "HG=F", "color": "#FF9457", "icon": "🔶"},
}

# --------------------------------------------------------------------------
# Obsidian terminal theme
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
    html, body, [class*="css"]  { font-family: 'JetBrains Mono', 'Courier New', monospace; }
    .stApp {
        background: radial-gradient(circle at 20% 0%, #191926 0%, #0b0b12 55%, #050508 100%);
    }
    .mp-hero {
        padding: 6px 0 18px 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 18px;
    }
    .mp-hero h1 {
        font-size: 2.1rem;
        margin-bottom: 0;
        background: linear-gradient(90deg, #FFD700, #C7CCD6 60%, #8FD3FE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .mp-hero p { color: #8a8a99; margin-top: 2px; }
    .metric-box {
        padding: 18px 16px;
        border-radius: 14px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        backdrop-filter: blur(6px);
        text-align: center;
        transition: box-shadow 0.3s ease;
    }
    .up-effect { border-color: rgba(0,255,136,0.5); box-shadow: 0 0 18px rgba(0,255,136,0.12); }
    .down-effect { border-color: rgba(255,68,68,0.5); box-shadow: 0 0 18px rgba(255,68,68,0.12); }
    .metric-box h4 { margin: 0 0 6px 0; font-weight: 600; font-size: 0.9rem; letter-spacing: 0.03em; }
    .metric-box h2 { margin: 0; font-size: 1.9rem; }
    .metric-box .sub { color: #888; font-size: 0.78rem; margin-top: 6px; }
    .mp-caption { color: #6f6f7d; font-size: 0.82rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="mp-hero">
        <h1>🧭 MetalPulse</h1>
        <p>Live precious &amp; industrial metals terminal — streaming quotes, momentum, and cross-metal analytics.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Sidebar controls
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Terminal controls")
    selected_metals = st.multiselect(
        "Metals to track", list(METALS.keys()), default=["Gold", "Silver"]
    )
    refresh_interval = st.slider("Auto-refresh interval (seconds)", 10, 120, 30, step=10)
    history_len = st.slider("Session history length (points)", 10, 100, 30, step=10)

    st.markdown("---")
    st.markdown("### 🔔 Price alerts")
    st.caption("Get notified when a metal crosses a target price.")
    alert_targets = {}
    for _name in selected_metals:
        alert_targets[_name] = st.number_input(
            f"{_name} alert price ($)", min_value=0.0, value=0.0, step=1.0, key=f"alert_{_name}"
        )

    st.markdown("---")
    st.caption(
        "Data source: Yahoo Finance futures quotes (typically 10–20 min delayed), "
        "via the `yfinance` library. Not intended for trading decisions."
    )

if not selected_metals:
    st.info("Select at least one metal from the sidebar to start streaming.")
    st.stop()

# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = {}
for _name in selected_metals:
    st.session_state.history.setdefault(_name, {"price": [], "time": []})


# --------------------------------------------------------------------------
# Cached data access
# --------------------------------------------------------------------------
@st.cache_data(ttl=30, show_spinner=False)
def fetch_live_price(ticker: str) -> float:
    data = yf.Ticker(ticker).history(period="1d", interval="1m")
    if data.empty:
        data = yf.Ticker(ticker).history(period="5d")
    if data.empty:
        raise ValueError(f"No data returned for {ticker}")
    return float(data["Close"].iloc[-1])


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_year_range(ticker: str):
    data = yf.Ticker(ticker).history(period="1y")
    if data.empty:
        return None, None
    return float(data["Close"].max()), float(data["Close"].min())


@st.cache_data(ttl=600, show_spinner=False)
def fetch_rsi(ticker: str, window: int = 14):
    data = yf.Ticker(ticker).history(period="5d", interval="15m")
    if data.empty or len(data) < window + 1:
        return pd.Series(dtype=float)
    delta = data["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.dropna()


# --------------------------------------------------------------------------
# Live dashboard fragment — this is the key upgrade: it re-runs on its own
# timer without blocking the rest of the app or freezing the sidebar.
# --------------------------------------------------------------------------
@st.fragment(run_every=refresh_interval)
def live_dashboard():
    now = datetime.now().strftime("%H:%M:%S")
    prices, fetch_errors = {}, []

    for name in selected_metals:
        ticker = METALS[name]["ticker"]
        try:
            prices[name] = fetch_live_price(ticker)
        except Exception as exc:  # noqa: BLE001
            fetch_errors.append(f"{name} ({ticker}): {exc}")

    if fetch_errors:
        st.warning("Some quotes couldn't be fetched this cycle:\n\n" + "\n".join(fetch_errors))

    if not prices:
        st.error("No live prices available right now. Will retry on the next refresh.")
        return

    # Update per-metal history
    for name, price in prices.items():
        hist = st.session_state.history[name]
        hist["price"].append(price)
        hist["time"].append(now)
        if len(hist["price"]) > history_len:
            hist["price"].pop(0)
            hist["time"].pop(0)

    # --- Row 1: metric cards -------------------------------------------------
    cols = st.columns(len(prices))
    for col, (name, price) in zip(cols, prices.items()):
        hist = st.session_state.history[name]["price"]
        delta = round(price - hist[0], 2) if len(hist) > 1 else 0.0
        pct = round((delta / hist[0]) * 100, 2) if len(hist) > 1 and hist[0] else 0.0
        css_class = "up-effect" if delta >= 0 else "down-effect"
        color = "#00ff88" if delta >= 0 else "#ff4444"

        target = alert_targets.get(name, 0.0)
        if target and price >= target and delta >= 0:
            st.toast(f"🔔 {name} reached your target of ${target:,.2f}", icon="🔔")

        with col:
            st.markdown(
                f"""
                <div class="metric-box {css_class}">
                    <h4>{METALS[name]['icon']} {name}</h4>
                    <h2>${price:,.2f}</h2>
                    <p style="color:{color}; margin: 4px 0 0 0;">{delta:+.2f} USD ({pct:+.2f}%)</p>
                    <p class="sub">session start: ${hist[0]:,.2f}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("")

    # --- Row 2: normalized session comparison --------------------------------
    if len(prices) > 1:
        st.subheader("📈 Session performance comparison (normalized %)")
        fig = go.Figure()
        for name in prices:
            hist = st.session_state.history[name]
            base = hist["price"][0]
            norm = [(p / base - 1) * 100 for p in hist["price"]]
            fig.add_trace(
                go.Scatter(
                    x=hist["time"], y=norm, mode="lines+markers", name=name,
                    line=dict(color=METALS[name]["color"], width=3),
                )
            )
        fig.update_layout(
            height=320, template="plotly_dark", margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis_title="% change vs session start",
        )
        st.plotly_chart(fig, width="stretch")

    # --- Row 3: per-metal detail (price trend + RSI + 52wk range) ------------
    st.subheader("🔍 Per-metal detail")
    detail_cols = st.columns(len(prices))
    for col, name in zip(detail_cols, prices):
        with col:
            with st.expander(f"{METALS[name]['icon']} {name}", expanded=False):
                hist = st.session_state.history[name]

                fig_p = go.Figure()
                fig_p.add_trace(
                    go.Scatter(
                        x=hist["time"], y=hist["price"], mode="lines+markers",
                        line=dict(color=METALS[name]["color"], width=2),
                    )
                )
                fig_p.update_layout(
                    height=220, template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    title="Session price trend",
                )
                st.plotly_chart(fig_p, width="stretch")

                rsi_series = fetch_rsi(METALS[name]["ticker"])
                if not rsi_series.empty:
                    latest_rsi = rsi_series.iloc[-1]
                    zone = "Overbought" if latest_rsi > 70 else "Oversold" if latest_rsi < 30 else "Neutral"
                    st.metric("RSI (14, 15m)", f"{latest_rsi:.1f}", zone)
                else:
                    st.caption("Not enough intraday data yet for RSI.")

                y_high, y_low = fetch_year_range(METALS[name]["ticker"])
                if y_high is not None:
                    st.caption(f"52-week range: ${y_low:,.2f} – ${y_high:,.2f}")

    # --- Row 4: correlation heatmap ------------------------------------------
    if len(prices) > 1:
        min_len = min(len(st.session_state.history[n]["price"]) for n in prices)
        if min_len >= 3:
            st.subheader("🧮 Correlation across selected metals")
            corr_df = pd.DataFrame(
                {n: st.session_state.history[n]["price"][-min_len:] for n in prices}
            )
            corr = corr_df.corr()
            fig_c = go.Figure(
                data=go.Heatmap(
                    z=corr.values, x=corr.columns, y=corr.columns,
                    colorscale="RdYlGn", zmin=-1, zmax=1, text=corr.round(2).values,
                    texttemplate="%{text}",
                )
            )
            fig_c.update_layout(
                height=320, template="plotly_dark", margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_c, width="stretch")
        else:
            st.caption("Collecting more data points before correlation can be computed…")

    # --- Row 5: export ---------------------------------------------------------
    export_df = pd.DataFrame(
        {
            "time": st.session_state.history[selected_metals[0]]["time"],
            **{n: st.session_state.history[n]["price"] for n in selected_metals
               if len(st.session_state.history[n]["price"]) == len(st.session_state.history[selected_metals[0]]["time"])},
        }
    )
    st.download_button(
        "⬇️ Download session data (CSV)",
        export_df.to_csv(index=False).encode("utf-8"),
        file_name=f"metalpulse_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )

    st.markdown(
        f'<p class="mp-caption">🔄 Live. Last refresh {now} · auto-refreshing every {refresh_interval}s</p>',
        unsafe_allow_html=True,
    )


live_dashboard()
