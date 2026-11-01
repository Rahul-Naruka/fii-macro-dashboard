# Naruka Wealth — Institutional Portfolio Advisory & Macro Portal

An integrated wealth advisory web application, macro regime engine, and portfolio diagnostic platform built for **Rahul Naruka** (AMFI Registered Mutual Fund Distributor, ARN: **277301**).

- **Brand**: Naruka Wealth
- **ARN**: 277301
- **Contact Person**: Rahul Naruka
- **Phone**: +91 8168391356
- **Email**: narukawealth@gmail.com
- **Location**: Rewari, Haryana - 123401
- **Live Deployment**: `https://rahul-naruka.github.io/fii-macro-dashboard/`

---

## 🛠️ Key Platform Modules & Tools

### 1. Security PIN Gateway
- Client access protected by security PIN (`0143`).
- Clean error response (`Incorrect PIN`) with zero plaintext code disclosure.
- Browser `sessionStorage` authentication with manual instant-lock control.

### 2. Macro Transmission & FII Inflows Engine (1993 – 2026)
- Evaluates 7 core indicators daily: US 10Y Yield, US YoY CPI, DXY, Brent Crude, USD/INR, Nifty Forward P/E, and EPS Growth.
- Color-coded indicator ledger covering all 34 years since FII inception in India.
- Automated daily market-close refresh via GitHub Actions (`auto_update.yml`).

### 3. Interactive Client Risk Profiler (SEBI / Institutional Rules)
- Assesses age, investment horizon, drawdown reaction, mutual fund experience, and return expectations.
- Classifies investors into 4 distinct risk profiles:
  - **Conservative** (10% - 35% Equity)
  - **Moderate** (30% - 65% Equity)
  - **Aggressive** (45% - 80% Equity)
  - **Very Aggressive** (60% - 95% Equity)

### 4. CAMS / KFintech CAS Statement Analyzer
- Parses client PDF/Excel Consolidated Account Statements (CAS) directly in the client browser with PDF.js.
- Classifies detected schemes into asset categories (Equity, Debt, Hybrid, Arbitrage) and computes existing asset allocation.

### 5. Quantitative Portfolio Health Scorecard (Out of 100)
- Evaluates existing portfolios across 4 core diagnostic pillars:
  1. **Risk Profile Alignment** (30 Points)
  2. **Macro Regime Transmission** (25 Points)
  3. **Scheme Spread & Category Overlap** (25 Points)
  4. **Fund Quality & Downside Protection** (20 Points)
- Highlights actionable portfolio gaps and overcrowding warnings.

### 6. Dynamic Rebalanced Model Portfolio (Zfunds / Platform Selection Rules)
- Curates exact mutual fund schemes with **target allocation percentages (%)** and deployment modes (SIP vs. STP vs. Lump Sum).
- Selection criteria: 3Y/5Y rolling alpha, downside capture ratio < 85%, and fund manager track record.

### 7. Executive Client Review PDF Exporter
- One-click PDF download containing investor details, diagnostic scores, allocation variance tables, and distributor sign-off.
- Features complete ARN registration, contact numbers, and regulatory disclaimers.

---

## ⚠️ Regulatory & Compliance Disclaimer
This platform and dashboard are strictly for **educational purposes and personal client suitability reviews** by Rahul Naruka, AMFI Registered Mutual Fund Distributor (ARN: 277301). Mutual fund investments are subject to market risks; read all scheme related documents carefully before investing.
