# FII Macro Transmission & Investment Signal Dashboard (2005 – 2026)

Automated, daily-updating institutional signal engine and macro dashboard deployed for `Rahul-Naruka/fii-macro-dashboard`.

- **Live URL**: `https://Rahul-Naruka.github.io/fii-macro-dashboard/`
- **Signal JSON Feed**: `https://Rahul-Naruka.github.io/fii-macro-dashboard/data/latest_signal.json`

---

## 🚀 How It Works (100% Automated & Free)

1. **Daily Automated Trigger (`.github/workflows/auto_update.yml`)**:
   - Runs Monday through Friday at 18:30 IST (13:00 UTC) right after Indian markets close.
   - Executes `scripts/update_signals.py` to pull the latest daily data:
     - **US 10-Yr Treasury Yield** (`^TNX`)
     - **US Dollar Index** (`DX-Y.NYB`)
     - **Brent Crude Oil** (`BZ=F`)
     - **USD/INR Exchange Rate** (`INR=X`)
     - **Nifty 50 Index** (`^NSEI`)
2. **Signal Classification**:
   - Scores the indicators against your Excel rule matrix:
     - **Green (Favourable)**: US 10Y < 3.50%, DXY < 95, Crude < $75, USD/INR Stable.
     - **Yellow (Neutral)**: US 10Y 3.50%-4.25%, DXY 95-101.5, Crude $75-$85.
     - **Red (Unfavourable)**: US 10Y > 4.25%, DXY > 101.5, Crude > $85, USD/INR depreciating > ₹88.
3. **Automated Commit & Deployment**:
   - Automatically writes to `data/latest_signal.json`.
   - GitHub Pages re-deploys within 60 seconds with no server costs.

---

## 🛠️ Step-by-Step Setup Guide

### 1. Initialize & Push from Your Terminal
Extract this package on your computer, navigate into the folder, and run:
```bash
git init
git add .
git commit -m "Initial commit: FII Macro Transmission Dashboard"
git branch -M main
git remote add origin https://github.com/Rahul-Naruka/fii-macro-dashboard.git
git push -u origin main
```

### 2. Configure GitHub Permissions (Crucial 1-minute step)
1. In your GitHub repository (`Rahul-Naruka/fii-macro-dashboard`), open **Settings** > **Actions** > **General**.
2. Scroll to **Workflow permissions**:
   - Select **"Read and write permissions"**.
   - Check the box **"Allow GitHub Actions to create and approve pull requests"**.
   - Click **Save**.
3. Open **Settings** > **Pages**:
   - Under **Build and deployment** > **Source**, choose **GitHub Actions**.

### 3. Trigger Your First Build
1. Go to the **Actions** tab in your repository.
2. Under "All workflows", select **Auto Update FII Signals & Deploy Dashboard**.
3. Click **Run workflow** > **Run workflow**.
4. Once completed (green checkmark), open:
   `https://Rahul-Naruka.github.io/fii-macro-dashboard/`

---

## 🌐 Embed Into Your Existing Website

### Option A: Responsive iFrame
```html
<iframe 
  src="https://Rahul-Naruka.github.io/fii-macro-dashboard/" 
  width="100%" 
  height="750px" 
  frameborder="0" 
  style="border-radius: 16px; border: 1px solid #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.25);"
  loading="lazy">
</iframe>
```

### Option B: Direct JSON REST API
```javascript
fetch("https://Rahul-Naruka.github.io/fii-macro-dashboard/data/latest_signal.json")
  .then(res => res.json())
  .then(data => {
    console.log("Current FII Regime:", data.signal); // "FAVOURABLE" | "NEUTRAL" | "UNFAVOURABLE"
    console.log("Score:", data.score);
    console.log("Summary:", data.summary);
  });
```
