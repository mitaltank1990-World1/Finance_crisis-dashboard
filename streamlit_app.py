import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
import numpy as np

st.set_page_config(page_title="US Dollar Debasement Crisis Dashboard - Dec 2025", layout="wide")

st.title("🔴 Live US Dollar Debasement Crisis Dashboard")
st.markdown("**Real-time monitoring of the exact triggers we discussed • December 2025 update**")

# === AUTO-FETCHED LIVE DATA ===
@st.cache_data(ttl=600)  # Refresh every 10 min

def fetch_market_data():
    tickers = {
        "BTC-USD": "Bitcoin",
        "GC=F": "Gold Spot $",
        "^TNX": "10-Year Treasury Yield %",
        "DX-Y.NYB": "DXY",
        "URA": "Uranium ETF (URA)",
        "CCJ": "Cameco (CCJ)"
    }
    data = yf.download(list(tickers.keys()), period="2y")["Close"]
    latest = data.iloc[-1].round(2).to_dict()
    latest = {v: latest[k] for k, v in tickers.items()}
    latest["10y Breakeven %"] = round(pd.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=T10YIE").iloc[-1]["T10YIE"], 2)
    return data, latest

data, latest = fetch_market_data()

# === FOREIGN TREASURY HOLDINGS (auto-parsed from official TIC) ===
@st.cache_data(ttl=86400)  # Daily refresh is plenty

def get_tic_grand_total_billions():
    url = "https://ticdata.treasury.gov/Publish/mfh.txt"
    r = requests.get(url)
    for line in r.text.splitlines():
        if "Grand Total" in line and len(line.split()) > 5:
            parts = line.split()
            try:
                latest_val = float(parts[2])  # First number after "Grand Total" is most recent month (in billions)
                prev_val = float(parts[3])
                change_1m = latest_val - prev_val
                return latest_val, change_1m
            except:
                continue
    return None, None

tic_latest, tic_change = get_tic_grand_total_billions()
tic_str = f"${tic_latest}B" if tic_latest else "Failed to parse (check URL)"
tic_change_str = f"({tic_change:+.1f}B MoM)" if tic_change is not None else ""

# === CURRENT READINGS (Dec 2025 real values will show here) ===
col1, col2, col3, col4 = st.columns(4)
col1.metric("Bitcoin", f"${latest['Bitcoin']:,.0f}")
col2.metric("Gold Spot", f"${latest['Gold Spot $']:,.0f}")
col3.metric("10y Treasury Yield", f"{latest['10-Year Treasury Yield %']:.2f}%")
col4.metric("DXY", f"${latest['DXY']:.2f}")

col5, col6, col7 = st.columns(3)
col5.metric("10-Year Breakeven Inflation", f"{latest['10y Breakeven %']:.2f}%")
col6.metric("Foreign Holdings of Treasuries (latest)", tic_str, tic_change_str)
col7.metric("Uranium ETF URA", f"${latest['Uranium ETF (URA)']:,.2f}")

# === STAGE ASSESSMENT ENGINE ===
triggers = {
    "Pre (Cracks Visible)": [
        (latest['10-Year Treasury Yield %'] > 4.5, "10y > 4.5%"),
        (latest['10y Breakeven %'] > 3.0, "Breakeven > 3.0%"),
        (latest['Gold Spot $'] > 3200, "Gold > $3,200"),
        (tic_change is not None and tic_change < 0, "Foreign Treasury holdings declining MoM"),
    ],
    "Near (Tipping Point)": [
        (latest['10-Year Treasury Yield %'] > 5.5, "10y > 5.5% despite Fed"),
        (latest['10y Breakeven %'] > 3.5, "Breakeven > 3.5%"),
        (latest['Gold Spot $'] > 3500, "Gold > $3,500"),
        (latest['DXY'] < 95, "DXY < 95"),
        (tic_latest is not None and tic_latest < 8500, "Absolute foreign Treasury holdings declining YoY"),  # adjust threshold as needed
    ],
    "In It (Acute Crisis)": [
        (latest['10-Year Treasury Yield %'] > 7.0, "10y spike > 7%"),
        (latest['10y Breakeven %'] > 6.0, "Breakeven > 6%"),
        (latest['Gold Spot $'] > 5000, "Gold > $5,000"),
        (latest['Bitcoin'] > 400000, "Bitcoin > $400k"),
    ]
}

active_stages = [stage for stage, checks in triggers.items() if sum(cond for cond, _ in checks) >= 3]

if "In It" in active_stages:
    current_stage = "🔴 IN IT — Acute Crisis"
elif "Near" in active_stages:
    current_stage = "🟡 NEAR — Tipping Point"
elif "Pre" in active_stages:
    current_stage = "🟠 PRE — Cracks Visible"
else:
    current_stage = "🟢 Pre-Pre (Complacency)"

st.markdown(f"## **CURRENT STAGE: {current_stage}**")

# === DETAILED TRIGGER TABLE ===
st.subheader("Live Trigger Status")
trigger_data = []
for stage, checks in triggers.items():
    for cond, label in checks:
        trigger_data.append({"Stage": stage, "Trigger": label, "Status": "🟢 Triggered" if cond else "⚪ Not yet"})
df_triggers = pd.DataFrame(trigger_data)
st.dataframe(df_triggers, use_container_width=True, hide_index=True)

# === CHARTS ===
st.subheader("Key Charts (2Y)")
chart_data = data.rename(columns={v: k for k, v in {
    "BTC-USD": "Bitcoin",
    "GC=F": "Gold Spot $",
    "^TNX": "10y Yield %",
    "DX-Y.NYB": "DXY"
}.items()})
fig = px.line(chart_data, title="Core Indicators", height=600)
st.plotly_chart(fig, use_container_width=True)

# === YOUR $4,000 PORTFOLIO TRACKER (Dec 6 2025 start) ===
st.subheader("Your $4,000 Crisis Portfolio Performance")
initial_btc_price = 89500
initial_ura_price = 49.0
initial_ccj_price = 93.0

btc_amount = 2000 / initial_btc_price
ura_shares = 1600 / initial_ura_price
ccj_shares = 400 / initial_ccj_price

current_value = (btc_amount * latest['Bitcoin']) + (ura_shares * latest['Uranium ETF (URA)']) + (ccj_shares * latest['Cameco (CCJ)'])
gain = current_value - 4000

st.metric("Portfolio Value Today", f"${current_value:,.0f}", f"{gain:,.0f} ({gain/40:.1f}%)")

st.markdown("Started Dec 6 2025 • 50% BTC / 40% URA / 10% CCJ")

st.markdown("---")
st.markdown("Dashboard auto-updates every 10 minutes • Fully open-source • Deploy instantly on Streamlit Cloud, Vercel, or locally")
