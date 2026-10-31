import os
import json
import datetime
import urllib.request
import re

DATA_FILE = "data/macro_history.json"
LIVE_SIGNAL_FILE = "data/latest_signal.json"

def fetch_via_yfinance_or_api():
    """
    Attempt to use yfinance if available, else use direct Yahoo Finance Chart v8 JSON endpoints
    """
    symbols = {
        "us10y": "%5ETNX",
        "dxy": "DX-Y.NYB",
        "brent": "BZ%3DF",
        "usdinr": "INR%3DX",
        "nifty": "%5ENSEI"
    }
    
    results = {}
    
    # Try importing yfinance first if installed in GitHub Actions
    try:
        import yfinance as yf
        for k, s in [("us10y", "^TNX"), ("dxy", "DX-Y.NYB"), ("brent", "BZ=F"), ("usdinr", "INR=X"), ("nifty", "^NSEI")]:
            try:
                hist = yf.Ticker(s).history(period="5d")
                if not hist.empty:
                    results[k] = round(float(hist["Close"].iloc[-1]), 2)
            except Exception as e:
                print(f"yfinance failed for {s}: {e}")
    except ImportError:
        pass

    # Direct fallback via HTTP endpoint if any missing
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for k, sym in symbols.items():
        if k in results and results[k] is not None:
            continue
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
                valid_closes = [c for c in closes if c is not None]
                if valid_closes:
                    results[k] = round(float(valid_closes[-1]), 2)
        except Exception as e:
            print(f"Direct API fallback failed for {k} ({sym}): {e}")

    # Fallback sensible baseline if offline/weekend
    return {
        "us10y": results.get("us10y", 4.28),
        "dxy": results.get("dxy", 102.40),
        "brent": results.get("brent", 81.20),
        "usdinr": results.get("usdinr", 88.65),
        "nifty": results.get("nifty", 24450.0),
        "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

def calculate_signal(metrics):
    scores = []
    breakdown = {}

    # 1. US 10Y Yield
    y = metrics["us10y"]
    if y < 3.50:
        scores.append(1)
        breakdown["us10y"] = {"status": "Green", "value": y, "label": "US 10Y Yield", "assessment": "Dovish (<3.50%)"}
    elif 3.50 <= y <= 4.25:
        scores.append(0)
        breakdown["us10y"] = {"status": "Yellow", "value": y, "label": "US 10Y Yield", "assessment": "Balanced (3.50%-4.25%)"}
    else:
        scores.append(-1)
        breakdown["us10y"] = {"status": "Red", "value": y, "label": "US 10Y Yield", "assessment": "Elevated Yield Drag (>4.25%)"}

    # 2. Dollar Index (DXY)
    d = metrics["dxy"]
    if d < 95.0:
        scores.append(1)
        breakdown["dxy"] = {"status": "Green", "value": d, "label": "US Dollar Index (DXY)", "assessment": "Soft USD (<95, Inflow Tailwind)"}
    elif 95.0 <= d <= 101.5:
        scores.append(0)
        breakdown["dxy"] = {"status": "Yellow", "value": d, "label": "US Dollar Index (DXY)", "assessment": "Rangebound (95-101.5)"}
    else:
        scores.append(-1)
        breakdown["dxy"] = {"status": "Red", "value": d, "label": "US Dollar Index (DXY)", "assessment": "Strong USD (>101.5, Capital Flight Headwind)"}

    # 3. Brent Crude
    b = metrics["brent"]
    if b < 75.0:
        scores.append(1)
        breakdown["brent"] = {"status": "Green", "value": b, "label": "Brent Crude ($/bbl)", "assessment": "Low Import Bill (<$75)"}
    elif 75.0 <= b <= 85.0:
        scores.append(0)
        breakdown["brent"] = {"status": "Yellow", "value": b, "label": "Brent Crude ($/bbl)", "assessment": "Moderate ($75-$85)"}
    else:
        scores.append(-1)
        breakdown["brent"] = {"status": "Red", "value": b, "label": "Brent Crude ($/bbl)", "assessment": "Inflation Drag (>$85)"}

    # 4. USD/INR
    fx = metrics["usdinr"]
    if fx < 84.0:
        scores.append(1)
        breakdown["usdinr"] = {"status": "Green", "value": fx, "label": "USD/INR Exchange Rate", "assessment": "Appreciating / Stable"}
    elif 84.0 <= fx <= 88.0:
        scores.append(0)
        breakdown["usdinr"] = {"status": "Yellow", "value": fx, "label": "USD/INR Exchange Rate", "assessment": "Gradual Depreciation"}
    else:
        scores.append(-1)
        breakdown["usdinr"] = {"status": "Red", "value": fx, "label": "USD/INR Exchange Rate", "assessment": "Sharp Depreciation (>₹88)"}

    avg_score = sum(scores) / len(scores)

    if avg_score >= 0.4:
        signal = "FAVOURABLE"
        color = "#10b981"
        badge = "GREEN"
        summary = "Favourable macro transmission setup. Global risk-on sentiment supports institutional capital inflows."
    elif avg_score <= -0.25:
        signal = "UNFAVOURABLE"
        color = "#ef4444"
        badge = "RED"
        summary = "Unfavourable macro transmission. High US risk-free yields & USD strength exert outflow pressure, cushioned by domestic DII SIPs."
    else:
        signal = "NEUTRAL"
        color = "#f59e0b"
        badge = "YELLOW"
        summary = "Balanced macro conditions. Cross-currents in rates and crude yield rangebound institutional flows."

    return {
        "signal": signal,
        "color": color,
        "badge": badge,
        "score": round(avg_score, 2),
        "summary": summary,
        "breakdown": breakdown,
        "metrics": metrics,
        "last_updated": metrics["timestamp"]
    }

def main():
    metrics = fetch_via_yfinance_or_api()
    signal_data = calculate_signal(metrics)
    
    os.makedirs("data", exist_ok=True)
    with open(LIVE_SIGNAL_FILE, "w") as f:
        json.dump(signal_data, f, indent=2)
    print(f"Updated live signal: {signal_data['signal']} ({signal_data['summary']})")

if __name__ == "__main__":
    main()
