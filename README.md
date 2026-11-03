# FII Macro Dashboard — Upgrade Package

This package upgrades `https://rahul-naruka.github.io/fii-macro-dashboard/` with:
1. **Multi-Horizon Return & CAGR Engine (`1M`, `3M`, `1Y`, `3Y CAGR`, `5Y CAGR`)** across indices, macro indicators, and mutual funds.
2. **Automated Daily Data Reference Pipeline** via GitHub Actions (`.github/workflows/fetch-data.yml`) + Python (`scripts/update_fii_data.py`) pulling from NSE India, Yahoo Finance, and `api.mfapi.in`.
3. **MoM Dynamic Asset Allocation & Suggested Mutual Funds** tailored to 5 distinct Risk Profiles (`Conservative`, `Moderate`, `Balanced`, `Aggressive`, `Very Aggressive`), dynamically tilting equity/debt weights based on trailing 1-month FII flows.

---

## Directory Structure

```text
fii-macro-dashboard-upgrade/
├── .github/
│   └── workflows/
│       └── fetch-data.yml         # Runs Mon-Fri at 8:00 PM IST to update daily JSON
├── css/
│   └── styles.css                 # Responsive dark-mode financial UI styles
├── data/
│   └── daily-fii-macro.json       # Pre-populated 5Y dataset + daily auto-updated store
├── js/
│   └── dashboard-upgrade.js       # CAGR calculator, MoM risk allocator & DOM renderer
├── scripts/
│   └── update_fii_data.py         # Daily scraper for NSE FII/DII, Yahoo Finance & MFAPI
├── index.html                     # Complete ready-to-deploy dashboard page
├── requirements.txt               # Python dependencies for GitHub Action
└── README.md                      # Deployment & integration guide
```

---

## Quick Deployment Instructions

1. **Copy Files into Your Repo**:
   Extract this ZIP directly into your `fii-macro-dashboard` GitHub repository root (or merge the `<section>` blocks from `index.html` and include `js/dashboard-upgrade.js` + `css/styles.css`).
2. **Enable GitHub Actions Write Permissions**:
   - In your GitHub repo, go to **Settings → Actions → General**.
   - Scroll down to **Workflow permissions** and select **Read and write permissions**, then click **Save**.
3. **Trigger Initial Live Sync**:
   - Go to the **Actions** tab in your repository, select **Daily FII Macro & Mutual Fund NAV Sync**, and click **Run workflow**.
