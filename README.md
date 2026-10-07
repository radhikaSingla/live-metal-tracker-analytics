# 🧭 MetalPulse — Real-Time Precious Metals Analytics Dashboard

A real-time **Streamlit analytics dashboard** for monitoring Gold, Silver, Platinum, Palladium, and Copper futures. The application retrieves market data through `yfinance`, processes price data using **Pandas**, calculates technical indicators, and presents interactive charts, session analytics, and configurable price alerts.

## 🔍 Key Capabilities

- **Automated data ingestion** using `yfinance`
- **Data processing and analysis** using Pandas
- **Time-series analysis** of precious metals price movements
- **Market monitoring** for Gold, Silver, Platinum, Palladium, and Copper futures
- **Technical indicator calculation** for trend analysis
- **Interactive data visualization** using Plotly and Streamlit
- **Session-based price tracking and analytics**
- **Configurable price alerts** for market movements
- **CSV export** for further analysis
- **Docker support** for application deployment

## 📊 Data & Analytics Workflow

~~~
Yahoo Finance
      ↓
Market Data Ingestion
      ↓
Price Data Processing
      ↓
Time-Series Analysis
      ↓
Technical Indicators
      ↓
Interactive Visualizations
      ↓
Price Alerts & CSV Export
~~~

## 🛠️ Tech Stack

- **Python** — Core programming language
- **Pandas** — Data processing and analysis
- **yfinance** — Market data retrieval
- **Streamlit** — Interactive dashboard development
- **Plotly** — Interactive data visualization
- **Docker** — Containerization and deployment

## 📈 Analytics Features

### Precious Metals Monitoring

The dashboard allows users to monitor:

- 🥇 Gold
- 🥈 Silver
- Platinum
- Palladium
- Copper

### Time-Series Analysis

The application tracks price movements during the active session and provides visual representations of market trends.

### Technical Indicators

Technical indicators are calculated from retrieved market data to support trend and price-movement analysis.

### Interactive Visualizations

The dashboard uses Plotly and Streamlit to provide interactive charts for exploring market data and identifying trends.

### Price Alerts

Users can configure price-based alerts to monitor significant movements in selected precious metals.

### CSV Export

Session data can be exported as CSV for additional analysis or offline use.

## 🚀 Run Locally

### 1. Clone the Repository

~~~bash
git clone https://github.com/radhikaSingla/live-metal-tracker-analytics.git
~~~

### 2. Navigate to the Project Directory

~~~bash
cd live-metal-tracker-analytics
~~~

### 3. Install Dependencies

~~~bash
pip install -r requirements.txt
~~~

### 4. Run the Streamlit Application

~~~bash
streamlit run app.py
~~~

The application will normally be available at:

`http://localhost:8501`

## ☁️ Deploy to Streamlit Community Cloud

1. Push this repository to GitHub.
2. Make sure the repository contains:
   - `app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
3. Open [Streamlit Community Cloud](https://share.streamlit.io/).
4. Sign in with GitHub.
5. Click **New app**.
6. Select this repository and branch.
7. Set the main file path to `app.py`.
8. Click **Deploy**.

Streamlit Community Cloud installs the dependencies from `requirements.txt` and provides a public URL for the application.

## 🐳 Deploy with Docker

Build the Docker image:

~~~bash
docker build -t metalpulse .
~~~

Run the container:

~~~bash
docker run -p 8501:8501 metalpulse
~~~

The application will then be available at:

`http://localhost:8501`

## 📁 Project Structure

~~~
live-metal-tracker-analytics/
│
├── .streamlit/
│   └── config.toml
│
├── app.py
├── Dockerfile
├── requirements.txt
├── .gitignore
└── README.md
~~~

## ⚠️ Data Limitations

- Market prices are retrieved from Yahoo Finance futures data through `yfinance`.
- The data is typically **10–20 minutes delayed** and should not be considered a live trading feed.
- The application is intended for **analytics and educational purposes** and should not be used as the sole basis for financial or trading decisions.
- Session history used for charts and CSV export is stored in Streamlit's `st.session_state`.
- Session data resets when the browser session restarts.
- Persistent historical storage could be added in a future version using SQLite or a hosted database.

## 🔮 Future Improvements

- Persistent historical market-data storage
- SQLite or cloud database integration
- Longer-term historical trend analysis
- Additional technical indicators
- Advanced filtering and comparison features
- Automated reporting
- Machine learning-based price trend analysis
- User authentication and personalized watchlists

## 🎯 Project Objective

The goal of MetalPulse is to demonstrate an end-to-end **data analytics workflow** — from retrieving external market data and processing time-series information to generating analytical indicators, interactive visualizations, alerts, and downloadable datasets through a user-friendly dashboard.

