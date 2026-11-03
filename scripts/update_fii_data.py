import os
import json
import time
from datetime import datetime
import requests
import yfinance as yf

DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "daily-fii-macro.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/reports/fii-dii",
}

def get_nse_session():
    """Establishes an authenticated session with NSE to capture cookies."""
    session = requests.Session()
    session.headers.update(HEADERS)
    try:
        session.get("https://www.nseindia.com", timeout=10)
        time.sleep(1.5)
    except Exception as e:
        print(f"Warning: Failed to pre-warm NSE cookies: {e}")
    return session

def fetch_nse_fii_dii(session):
    """Fetches latest FII and DII cash segment provisional data from NSE."""
    url = "https://www.nseindia.com/api/fiidiiTradeReact"
    try:
        res = session.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            parsed = {}
            for item in data:
                cat = "FII" if "FII" in item.get("category", "").upper() else "DII"
                parsed[cat] = {
                    "buyValue": float(str(item.get("buyValue", 0)).replace(",", "")),
                    "sellValue": float(str(item.get("sellValue", 0)).replace(",", "")),
                    "netValue": float(str(item.get("netValue", 0)).replace(",", "")),
                    "date": item.get("date", datetime.today().strftime("%d-%b-%Y")),
                }
            return parsed
        else:
            print(f"NSE API returned HTTP {res.status_code}")
    except Exception as e:
        print(f"Error scraping FII/DII from NSE: {e}")
    return None

def fetch_macro_indicators():
    """Pulls 5+ years of daily OHLC history for Benchmark Indices & Macro via Yahoo Finance."""
    tickers = {
        "nifty50": {"symbol": "^NSEI", "name": "NIFTY 50", "category": "Equity Index"},
        "niftyBank": {"symbol": "^NSEBANK", "name": "NIFTY Bank", "category": "Sector Index"},
        "niftyMidcap": {"symbol": "NIFTYMIDCAP150.NS", "name": "NIFTY Midcap 150", "category": "Equity Index"},
        "goldBees": {"symbol": "GOLDBEES.NS", "name": "Gold ETF (Nippon GoldBeES)", "category": "Precious Metals"},
        "usdinr": {"symbol": "USDINR=X", "name": "USD / INR Exchange Rate", "category": "Currency Macro"},
        "us10yYield": {"symbol": "^TNX", "name": "US 10Y Treasury Yield", "category": "Global Macro"}
    }

    macro_data = {}
    for key, meta in tickers.items():
        try:
            ticker = yf.Ticker(meta["symbol"])
            hist = ticker.history(period="5y")
            if not hist.empty:
                hist.reset_index(inplace=True)
                records = []
                for _, row in hist.iterrows():
                    d_str = row["Date"].strftime("%Y-%m-%d")
                    records.append({"date": d_str, "value": round(float(row["Close"]), 2)})
                macro_data[key] = {
                    "name": meta["name"],
                    "category": meta["category"],
                    "symbol": meta["symbol"],
                    "history": records
                }
        except Exception as e:
            print(f"Failed fetching macro ticker {meta['symbol']}: {e}")
    return macro_data

def fetch_mfapi_nav(scheme_code, label, category):
    """Pulls historical NAV sequence from MFAPI.in (Free daily Indian Mutual Fund API)."""
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    try:
        r = requests.get(url, timeout=12)
        if r.status_code == 200:
            raw = r.json()
            history = []
            # Keep last ~1850 trading days (~5.5 years) sorted oldest to newest
            for item in reversed(raw.get("data", [])[:1400]):
                try:
                    dt = datetime.strptime(item["date"], "%d-%m-%Y").strftime("%Y-%m-%d")
                    history.append({"date": dt, "value": round(float(item["nav"]), 4)})
                except Exception:
                    continue
            return {
                "name": label or raw.get("meta", {}).get("scheme_name", f"Scheme {scheme_code}"),
                "category": category,
                "schemeCode": scheme_code,
                "history": history
            }
    except Exception as e:
        print(f"Error fetching MF {scheme_code}: {e}")
    return None

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    session = get_nse_session()

    print("1. Fetching FII / DII Daily Activity...")
    fii_dii_latest = fetch_nse_fii_dii(session)

    print("2. Fetching Macro & Index Historical Closes...")
    macro_trends = fetch_macro_indicators()

    print("3. Fetching Benchmark Mutual Funds via MFAPI...")
    mf_schemes = [
        (122639, "Parag Parikh Flexi Cap Fund (Direct)", "Flexi Cap Equity"),
        (118778, "Nippon India Large Cap Fund (Direct)", "Large Cap Equity"),
        (127042, "Motilal Oswal Midcap Fund (Direct)", "Mid Cap Equity"),
        (125497, "Nippon India Small Cap Fund (Direct)", "Small Cap Equity"),
        (120503, "ICICI Pru Balanced Advantage Fund (Direct)", "Dynamic Asset Allocation"),
        (119598, "HDFC Corporate Bond Fund (Direct)", "Corporate Debt")
    ]
    benchmarks = {}
    for code, label, cat in mf_schemes:
        res = fetch_mfapi_nav(code, label, cat)
        if res:
            benchmarks[f"mf_{code}"] = res

    # Load existing historical FII logs to append daily flow
    existing_payload = {}
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r") as f:
                existing_payload = json.load(f)
        except Exception:
            existing_payload = {}

    fii_history = existing_payload.get("fiiDiiHistory", [])
    if fii_dii_latest and "FII" in fii_dii_latest:
        today_date = fii_dii_latest["FII"]["date"]
        if not any(entry.get("date") == today_date for entry in fii_history):
            fii_history.append({
                "date": today_date,
                "fiiBuyCr": fii_dii_latest["FII"]["buyValue"],
                "fiiSellCr": fii_dii_latest["FII"]["sellValue"],
                "fiiNetCr": fii_dii_latest["FII"]["netValue"],
                "diiNetCr": fii_dii_latest.get("DII", {}).get("netValue", 0.0)
            })

    # Calculate 30-day cumulative FII flow for tactical MoM signal
    trailing_22 = fii_history[-22:] if len(fii_history) >= 1 else []
    mom_fii_net_cr = round(sum(x.get("fiiNetCr", 0) for x in trailing_22), 2)
    mom_dii_net_cr = round(sum(x.get("diiNetCr", 0) for x in trailing_22), 2)

    if mom_fii_net_cr < -15000:
        fii_regime = "Heavy FII Selling / Defensive Tilt"
        tactical_shift = -5 # Shift 5% from High-Beta Equity to Arbitrage/Debt & BAF
    elif mom_fii_net_cr > 10000:
        fii_regime = "Strong FII Inflows / Risk-On Momentum"
        tactical_shift = 5 # Tilt 5% into Core Flexi/Large & Midcap
    else:
        fii_regime = "Neutral Consolidation / Balanced Stance"
        tactical_shift = 0

    output_payload = {
        "lastUpdated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "macroRegime": {
            "trailingMonthlyFiiNetCr": mom_fii_net_cr,
            "trailingMonthlyDiiNetCr": mom_dii_net_cr,
            "regimeStatus": fii_regime,
            "tacticalEquityTiltPct": tactical_shift
        },
        "latestFiiDii": fii_dii_latest or existing_payload.get("latestFiiDii", {}),
        "fiiDiiHistory": fii_history[-90:],
        "indices": macro_trends if macro_trends else existing_payload.get("indices", {}),
        "funds": benchmarks if benchmarks else existing_payload.get("funds", {})
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output_payload, f, indent=2)

    print(f"Successfully updated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
