# 🧭 MetalPulse — Real-Time Precious Metals Analytics Dashboard

A real-time **Streamlit analytics dashboard** for monitoring Gold, Silver, Platinum, Palladium, and Copper futures. The application retrieves market data through `yfinance`, processes incoming price data, calculates technical indicators, and presents interactive charts, session analytics, and configurable price alerts.

### 🔍 Key Capabilities

- **Automated data ingestion** using `yfinance`
- **Real-time market monitoring** for precious metals futures
- **Time-series analysis** of price movements
- **Technical indicators** for market trend analysis
- **Interactive data visualizations** using Streamlit
- **Price alerts** for monitoring market movements
- **CSV export** for further analysis
- **Docker support** for deployment

### 🛠️ Tech Stack

**Python · Streamlit · Pandas · yfinance · Plotly · Docker**


## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

## Deploy to Streamlit Community Cloud (free, fastest option)

1. Push this repo (including `app.py`, `requirements.txt`, and
   `.streamlit/config.toml`) to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with
   GitHub.
3. Click **New app**, pick this repository/branch, and set the main file
   path to `app.py`.
4. Click **Deploy**. Streamlit Cloud installs `requirements.txt`
   automatically and gives you a public URL.
5. Any future push to the branch auto-redeploys the app.

## Deploy with Docker (any cloud VM, Fly.io, Render, etc.)

```bash
docker build -t metalpulse .
docker run -p 8501:8501 metalpulse
```

## Notes

- Prices come from Yahoo Finance futures data via `yfinance` and are
  typically **10–20 minutes delayed** — this is not a live trading feed
  and shouldn't be used to make trading decisions.
- Session history (used for the charts and CSV export) resets whenever
  the browser tab/session restarts, since it's held in
  `st.session_state` rather than a database. If you want history to
  persist across restarts, the next step would be writing each tick to
  a small SQLite file or a hosted database.
