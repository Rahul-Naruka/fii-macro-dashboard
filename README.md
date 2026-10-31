# FII Macro Transmission & Investment Signal Dashboard (2005 – 2026)

Full automated version configured for repository: `Rahul-Naruka/fii-macro-dashboard`

- **Live URL**: `https://rahul-naruka.github.io/fii-macro-dashboard/`
- **Signal JSON Feed**: `https://rahul-naruka.github.io/fii-macro-dashboard/data/latest_signal.json`

---

## 🚀 Key Features

1. **7 Core Macro & Valuation Transmission Indicators**:
   - **US 10-Yr Treasury Yield** (`^TNX`)
   - **US YoY CPI Inflation (%)**
   - **US Dollar Index** (`DX-Y.NYB`)
   - **Brent Crude Oil** (`BZ=F`)
   - **USD/INR Exchange Rate** (`INR=X`)
   - **Nifty Forward P/E (x)**
   - **Nifty EPS Growth (%)**
2. **Automated Traffic-Light Signal System**:
   - Evaluates whether macro transmission is **Favourable (Green)**, **Neutral (Yellow)**, or **Unfavourable (Red)**.
3. **Daily Automated Refresh via GitHub Actions**:
   - Runs every trading day at 18:30 IST (13:00 UTC) right after market close.
   - Dual-path sync writes to both `data/` and `docs/data/`.
   - Built-in cache busting prevents browser and CDN caching.
4. **Interactive Historical Charts (2005 – 2026)**:
   - FII vs DII Net Capital Flows.
   - US 10Y Yield, US YoY CPI Inflation, and Brent Crude Oil.
