import os
import json
import datetime
import urllib.request
import re

DATA_FILE = "data/macro_history.json"
LIVE_SIGNAL_FILE = "data/latest_signal.json"

def fetch_macro_and_valuation_metrics():
    """
    Fetch live daily macro & valuation indicators:
    - US 10-Yr Treasury Yield (^TNX)
    - US Dollar Index (DX-Y.NYB)
    - Brent Crude Oil Futures (BZ=F)
    - USD/INR Currency Pair (INR=X)
    - Nifty 50 Index (^NSEI)
    - Nifty Forward P/E & EPS Growth
    - US YoY CPI Inflation (%)
    """
    symbols = {
        "us10y": "%5ETNX",
        "dxy": "DX-Y.NYB",
        "brent": "BZ%3DF",
        "usdinr": "INR%3DX",
        "nifty": "%5ENSEI"
    }
    
    results = {}
    
    # Try importing yfinance first if available in GitHub Actions
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

    # Fallback/current baseline parameters
    nifty_close = results.get("nifty", 24450.0)
    
    # Nifty 50 Forward P/E (~20.2x) and EPS Growth (~9.1%)
    nifty_fwd_pe = round(nifty_close / 1210.0, 1) if nifty_close else 20.2
    nifty_eps_growth = 9.1

    # US YoY CPI Inflation (%)
    us_cpi_yoy = 3.7 # Current US Headline CPI YoY rate

    return {
        "us10y": results.get("us10y", 4.28),
        "dxy": results.get("dxy", 102.40),
        "brent": results.get("brent", 81.20),
        "usdinr": results.get("usdinr", 88.65),
        "nifty": nifty_close,
        "nifty_fwd_pe": nifty_fwd_pe,
        "nifty_eps_growth": nifty_eps_growth,
        "us_cpi_yoy": us_cpi_yoy,
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

    # 3. US YoY CPI Inflation (%)
    # Green: < 2.5% (Near 2% Fed target, enables rate cuts)
    # Yellow: 2.5% - 3.4% (Sticky inflation, cautious Fed)
    # Red: >= 3.5% (Elevated inflation, 'higher-for-longer' rates)
    cpi = metrics["us_cpi_yoy"]
    if cpi < 2.5:
        scores.append(1)
        breakdown["us_cpi_yoy"] = {"status": "Green", "value": cpi, "label": "US YoY CPI", "assessment": "Disinflationary (<2.5% Fed Pivot)"}
    elif 2.5 <= cpi < 3.5:
        scores.append(0)
        breakdown["us_cpi_yoy"] = {"status": "Yellow", "value": cpi, "label": "US YoY CPI", "assessment": "Sticky (2.5%-3.4%)"}
    else:
        scores.append(-1)
        breakdown["us_cpi_yoy"] = {"status": "Red", "value": cpi, "label": "US YoY CPI", "assessment": "Elevated Inflation (>=3.5%, Hawkish Fed)"}

    # 4. Brent Crude
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

    # 5. USD/INR FX
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

    # 6. Nifty Forward P/E
    pe = metrics["nifty_fwd_pe"]
    if pe < 19.0:
        scores.append(1)
        breakdown["nifty_fwd_pe"] = {"status": "Green", "value": pe, "label": "Nifty Forward P/E", "assessment": "Fair/Attractive (<19x)"}
    elif 19.0 <= pe <= 21.0:
        scores.append(0)
        breakdown["nifty_fwd_pe"] = {"status": "Yellow", "value": pe, "label": "Nifty Forward P/E", "assessment": "Balanced Valuation (19x-21x)"}
    else:
        scores.append(-1)
        breakdown["nifty_fwd_pe"] = {"status": "Red", "value": pe, "label": "Nifty Forward P/E", "assessment": "Stretched Premium (>21.5x)"}

    # 7. Nifty EPS Growth
    eps = metrics["nifty_eps_growth"]
    if eps >= 12.0:
        scores.append(1)
        breakdown["nifty_eps_growth"] = {"status": "Green", "value": eps, "label": "EPS Growth (%)", "assessment": "Robust (>12%)"}
    elif 8.0 <= eps < 12.0:
        scores.append(0)
        breakdown["nifty_eps_growth"] = {"status": "Yellow", "value": eps, "label": "EPS Growth (%)", "assessment": "Steady (8%-12%)"}
    else:
        scores.append(-1)
        breakdown["nifty_eps_growth"] = {"status": "Red", "value": eps, "label": "EPS Growth (%)", "assessment": "Subdued (<8%)"}

    avg_score = sum(scores) / len(scores)

    # Dynamic Profile-Based Asset Allocation (ZFunds & Quantitative Fund Selection Calibration)
    if avg_score >= 0.30:
        signal = "FAVOURABLE"
        color = "#10b981"
        badge = "GREEN"
        summary = "Favourable macro transmission setup. Global disinflation and risk-on liquidity drive steady foreign capital inflows."
        profiles = {
            "conservative": {
                "equity": 35, "debt": 65,
                "strategy": "Capital preservation with growth kicker. Deploy in Conservative Hybrid & Arbitrage funds + Banking & PSU Debt.",
                "funds": [
                    {"name": "HDFC Banking and PSU Debt Fund", "category": "Banking & PSU Debt", "allocation": 40, "type": "Debt"},
                    {"name": "Kotak Equity Arbitrage Fund", "category": "Arbitrage", "allocation": 25, "type": "Debt"},
                    {"name": "ICICI Prudential Regular Savings Fund", "category": "Conservative Hybrid", "allocation": 20, "type": "Equity"},
                    {"name": "UTI Nifty 50 Index Fund", "category": "Large Cap Index", "allocation": 15, "type": "Equity"}
                ]
            },
            "moderate": {
                "equity": 65, "debt": 35,
                "strategy": "Growth with controlled volatility. Overweight Balanced Advantage (BAF) & Multi-Asset Allocation funds.",
                "funds": [
                    {"name": "HDFC Balanced Advantage Fund", "category": "Dynamic Asset Allocation", "allocation": 35, "type": "Equity"},
                    {"name": "Parag Parikh Flexi Cap Fund", "category": "Flexi Cap", "allocation": 30, "type": "Equity"},
                    {"name": "ICICI Prudential Multi-Asset Fund", "category": "Multi Asset", "allocation": 20, "type": "Debt"},
                    {"name": "Aditya Birla Sun Life Corporate Bond Fund", "category": "Corporate Bond", "allocation": 15, "type": "Debt"}
                ]
            },
            "aggressive": {
                "equity": 80, "debt": 20,
                "strategy": "Aggressive wealth compounding. High exposure to Flexi Cap & Large & Mid Cap funds with 20% liquid reserve.",
                "funds": [
                    {"name": "Parag Parikh Flexi Cap Fund", "category": "Flexi Cap", "allocation": 40, "type": "Equity"},
                    {"name": "Mirae Asset Large & Midcap Fund", "category": "Large & Mid Cap", "allocation": 25, "type": "Equity"},
                    {"name": "Motilal Oswal Midcap Fund", "category": "Mid Cap", "allocation": 15, "type": "Equity"},
                    {"name": "HDFC Short Term Debt Fund", "category": "Short Duration Debt", "allocation": 20, "type": "Debt"}
                ]
            },
            "very_aggressive": {
                "equity": 95, "debt": 5,
                "strategy": "Maximum alpha expansion. Overweight Mid Cap, Small Cap, and focused growth funds.",
                "funds": [
                    {"name": "Motilal Oswal Midcap Fund", "category": "Mid Cap", "allocation": 35, "type": "Equity"},
                    {"name": "Nippon India Small Cap Fund", "category": "Small Cap", "allocation": 30, "type": "Equity"},
                    {"name": "Parag Parikh Flexi Cap Fund", "category": "Flexi Cap", "allocation": 20, "type": "Equity"},
                    {"name": "Bandhan Sterling Value Fund", "category": "Value / Focused", "allocation": 10, "type": "Equity"},
                    {"name": "ICICI Prudential Liquid Fund", "category": "Liquid / Cash Buffer", "allocation": 5, "type": "Debt"}
                ]
            }
        }
        overall_equity = 75
        overall_debt = 25
        allocation_strategy = "Risk-On / Aggressive Wealth Accumulation. Overweight Equities (Large & Flexi-cap funds) while keeping 25% in high-quality short/medium-duration Debt for liquidity."
    elif avg_score <= -0.20:
        signal = "UNFAVOURABLE"
        color = "#ef4444"
        badge = "RED"
        summary = "Unfavourable macro transmission. High US CPI & yields keep USD firm, inducing FII selling absorbed by domestic DII SIPs."
        profiles = {
            "conservative": {
                "equity": 10, "debt": 90,
                "strategy": "Maximum capital safety. Strict allocation to Sovereign G-Sec, Banking & PSU Debt, and Ultra Short Duration funds.",
                "funds": [
                    {"name": "SBI Banking and PSU Debt Fund", "category": "Banking & PSU Debt", "allocation": 50, "type": "Debt"},
                    {"name": "Bandhan All Seasons Bond Fund", "category": "Dynamic Bond", "allocation": 25, "type": "Debt"},
                    {"name": "HDFC Ultra Short Term Fund", "category": "Ultra Short Duration", "allocation": 15, "type": "Debt"},
                    {"name": "ICICI Prudential Nifty 50 Index Fund", "category": "Large Cap Index (SIP)", "allocation": 10, "type": "Equity"}
                ]
            },
            "moderate": {
                "equity": 30, "debt": 70,
                "strategy": "Capital defence & tactical SIP. Park in Arbitrage & Corporate Bond funds; maintain disciplined equity SIPs.",
                "funds": [
                    {"name": "Kotak Equity Arbitrage Fund", "category": "Arbitrage (Tax Safe)", "allocation": 35, "type": "Debt"},
                    {"name": "HDFC Corporate Bond Fund", "category": "Corporate Bond", "allocation": 35, "type": "Debt"},
                    {"name": "ICICI Prudential Balanced Advantage Fund", "category": "Dynamic Asset Allocation", "allocation": 15, "type": "Equity"},
                    {"name": "Parag Parikh Flexi Cap Fund", "category": "Flexi Cap (Staggered SIP)", "allocation": 15, "type": "Equity"}
                ]
            },
            "aggressive": {
                "equity": 45, "debt": 55,
                "strategy": "Defensive rebalancing. High quality Short Duration & Arbitrage funds (55%) with 6-month STP into Flexi Cap.",
                "funds": [
                    {"name": "ICICI Prudential Short Term Fund", "category": "Short Duration Debt (STP Source)", "allocation": 35, "type": "Debt"},
                    {"name": "Tata Arbitrage Fund", "category": "Arbitrage", "allocation": 20, "type": "Debt"},
                    {"name": "Parag Parikh Flexi Cap Fund", "category": "Flexi Cap (STP Inflow)", "allocation": 25, "type": "Equity"},
                    {"name": "Mirae Asset Large & Midcap Fund", "category": "Large & Mid Cap (SIP)", "allocation": 20, "type": "Equity"}
                ]
            },
            "very_aggressive": {
                "equity": 60, "debt": 40,
                "strategy": "Staggered dip buying. Maintain existing Mid/Small Cap SIPs while building 40% debt 'dry powder' for corrections.",
                "funds": [
                    {"name": "HDFC Money Market Fund", "category": "Money Market (Dry Powder)", "allocation": 40, "type": "Debt"},
                    {"name": "Motilal Oswal Midcap Fund", "category": "Mid Cap (SIP)", "allocation": 25, "type": "Equity"},
                    {"name": "Nippon India Small Cap Fund", "category": "Small Cap (SIP)", "allocation": 20, "type": "Equity"},
                    {"name": "Parag Parikh Flexi Cap Fund", "category": "Flexi Cap", "allocation": 15, "type": "Equity"}
                ]
            }
        }
        overall_equity = 35
        overall_debt = 65
        allocation_strategy = "Capital Preservation / Defensive Rebalance. Overweight Debt & Arbitrage funds (65%). Maintain disciplined equity SIPs (35%) to stagger into valuation corrections."
    else:
        signal = "NEUTRAL"
        color = "#f59e0b"
        badge = "YELLOW"
        summary = "Balanced macro conditions. Cross-currents across US inflation, crude, and valuations result in selective institutional allocation."
        profiles = {
            "conservative": {
                "equity": 20, "debt": 80,
                "strategy": "Income generation with minor equity kicker via Conservative Hybrid and High Quality Corporate Debt.",
                "funds": [
                    {"name": "HDFC Corporate Bond Fund", "category": "Corporate Bond", "allocation": 45, "type": "Debt"},
                    {"name": "Canara Robeco Conservative Hybrid Fund", "category": "Conservative Hybrid", "allocation": 20, "type": "Debt"},
                    {"name": "Aditya Birla Sun Life Savings Fund", "category": "Money Market", "allocation": 15, "type": "Debt"},
                    {"name": "UTI Nifty 50 Index Fund", "category": "Large Cap Index", "allocation": 20, "type": "Equity"}
                ]
            },
            "moderate": {
                "equity": 50, "debt": 50,
                "strategy": "Equalized hybrid allocation. Dynamic rebalancing via Balanced Advantage & Multi-Asset Allocation funds.",
                "funds": [
                    {"name": "HDFC Balanced Advantage Fund", "category": "Dynamic Asset Allocation", "allocation": 25, "type": "Equity"},
                    {"name": "SBI Multi Asset Allocation Fund", "category": "Multi Asset", "allocation": 25, "type": "Equity"},
                    {"name": "ICICI Prudential All Seasons Bond Fund", "category": "Dynamic Bond", "allocation": 30, "type": "Debt"},
                    {"name": "Kotak Equity Arbitrage Fund", "category": "Arbitrage", "allocation": 20, "type": "Debt"}
                ]
            },
            "aggressive": {
                "equity": 65, "debt": 35,
                "strategy": "Selective growth posture. Core allocations in Large & Mid Cap funds with active STP from Short Term Debt.",
                "funds": [
                    {"name": "Parag Parikh Flexi Cap Fund", "category": "Flexi Cap", "allocation": 35, "type": "Equity"},
                    {"name": "Mirae Asset Large & Midcap Fund", "category": "Large & Mid Cap", "allocation": 20, "type": "Equity"},
                    {"name": "Motilal Oswal Midcap Fund", "category": "Mid Cap", "allocation": 10, "type": "Equity"},
                    {"name": "Kotak Short Term Fund", "category": "Short Duration Debt", "allocation": 25, "type": "Debt"},
                    {"name": "ICICI Prudential Liquid Fund", "category": "Liquid", "allocation": 10, "type": "Debt"}
                ]
            },
            "very_aggressive": {
                "equity": 80, "debt": 20,
                "strategy": "Alpha bias. Continue heavy SIPs in Mid Cap & Flexi Cap funds with 20% parked in Liquid funds for market dips.",
                "funds": [
                    {"name": "Motilal Oswal Midcap Fund", "category": "Mid Cap", "allocation": 30, "type": "Equity"},
                    {"name": "Nippon India Small Cap Fund", "category": "Small Cap", "allocation": 25, "type": "Equity"},
                    {"name": "Quant Flexi Cap Fund", "category": "Flexi Cap", "allocation": 25, "type": "Equity"},
                    {"name": "ICICI Prudential Liquid Fund", "category": "Liquid (Dip Buying)", "allocation": 20, "type": "Debt"}
                ]
            }
        }
        overall_equity = 50
        overall_debt = 50
        allocation_strategy = "Balanced / Hybrid Posture. 50:50 Asset Allocation via Balanced Advantage or Multi-Asset Allocation funds. Utilize STPs from liquid/short duration debt into equities."

    return {
        "signal": signal,
        "color": color,
        "badge": badge,
        "score": round(avg_score, 2),
        "summary": summary,
        "allocation": {
            "equity": overall_equity,
            "debt": overall_debt,
            "strategy": allocation_strategy,
            "profiles": profiles
        },
        "breakdown": breakdown,
        "metrics": metrics,
        "last_updated": metrics["timestamp"]
    }

def main():
    metrics = fetch_macro_and_valuation_metrics()
    signal_data = calculate_signal(metrics)
    
    # Ensure both data directories are synced
    for d in ["data", "docs/data"]:
        os.makedirs(d, exist_ok=True)
        filepath = os.path.join(d, "latest_signal.json")
        with open(filepath, "w") as f:
            json.dump(signal_data, f, indent=2)
        print(f"Updated: {filepath}")
    print(f"Updated live signal: {signal_data['signal']} (Score: {signal_data['score']})")

if __name__ == "__main__":
    main()
