import os
import json
import pandas as pd
import requests
import yfinance as yf

SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_data.json")

def load_sample_data():
    """Load sample chart + latest values from data/sample_data.json.
    Returns (chart_df, latest_dict, tic_latest, tic_change)
    """
    with open(SAMPLE_PATH, "r") as f:
        j = json.load(f)
    chart = pd.DataFrame(j.get("chart", []))
    if not chart.empty:
        chart["Date"] = pd.to_datetime(chart["Date"])
        chart.set_index("Date", inplace=True)
    latest = j.get("latest", {})
    tic_latest = j.get("tic_latest")
    tic_change = j.get("tic_change")
    return chart, latest, tic_latest, tic_change

def fetch_market_data(use_sample=False):
    """Fetch market data via yfinance. On failure or if use_sample=True, return sample data.
    Returns (data_df, latest_dict, used_sample_bool)
    """
    tickers = {
        "BTC-USD": "Bitcoin",
        "GC=F": "Gold Spot $",
        "^TNX": "10-Year Treasury Yield %",
        "DX-Y.NYB": "DXY",
        "URA": "Uranium ETF (URA)",
        "CCJ": "Cameco (CCJ)"
    }

    def _rename_df(df):
        return df.rename(columns={k: v for k, v in tickers.items()})

    if use_sample:
        chart, latest, tic_latest, tic_change = load_sample_data()
        return _rename_df(chart), latest, True

    try:
        data = yf.download(list(tickers.keys()), period="2y")["Close"]
        # If yfinance returned an empty DataFrame or all-NaN, treat as failure
        if data.empty or data.isnull().all().all():
            raise RuntimeError("yfinance returned empty data")
        latest = data.iloc[-1].round(2).to_dict()
        latest = {v: latest[k] for k, v in tickers.items()}
        # Try to fetch 10y breakeven from FRED; if it fails we'll set None and let caller handle it
        try:
            t10 = pd.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=T10YIE").iloc[-1]["T10YIE"]
            latest["10y Breakeven %"] = round(float(t10), 2)
        except Exception:
            latest["10y Breakeven %"] = None

        return _rename_df(data), latest, False

    except Exception:
        # Fallback to sample data if remote fetch failed
        chart, latest, tic_latest, tic_change = load_sample_data()
        return _rename_df(chart), latest, True

def get_tic_grand_total_billions(use_sample=False):
    """Parse TIC Grand Total from Treasury text file. Returns (latest_val, change_1m, used_sample_bool) or (None, None, False).
    """
    url = "https://ticdata.treasury.gov/Publish/mfh.txt"
    if use_sample:
        try:
            _, _, tic_latest, tic_change = load_sample_data()
            return tic_latest, tic_change, True
        except Exception:
            return None, None, True

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        for line in r.text.splitlines():
            if "Grand Total" in line and len(line.split()) > 5:
                parts = line.split()
                try:
                    latest_val = float(parts[2])
                    prev_val = float(parts[3])
                    change_1m = latest_val - prev_val
                    return latest_val, change_1m, False
                except Exception:
                    continue
        return None, None, False
    except Exception:
        # Network/parsing failed; fallback to sample if available
        try:
            _, _, tic_latest, tic_change = load_sample_data()
            return tic_latest, tic_change, True
        except Exception:
            return None, None, True
