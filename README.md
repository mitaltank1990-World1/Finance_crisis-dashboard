# Finance_crisis-dashboard

Live Streamlit dashboard that monitors several market indicators tied to a US dollar debasement / financial-crisis thesis (Bitcoin, Gold, 10y yields, DXY, foreign Treasury holdings, uranium instruments, etc).

This repository should contain:
- A README (this file) with project description and run instructions
- The Streamlit app code (streamlit_app.py)
- Any supporting files (requirements.txt, assets, etc.)

Quick start (local)
1. Create a Python virtualenv and activate it.
2. Install dependencies:
   pip install -r requirements.txt
   (Example requirements: streamlit, yfinance, pandas, requests, plotly, numpy)
3. Run the dashboard:
   streamlit run streamlit_app.py

Notes
- The app auto-fetches market data (yfinance) and parses TIC foreign holdings from the Treasury TIC text file.
- Caching is used to limit requests: market data every 10 minutes, TIC once daily.
- The README was accidentally replaced with the Streamlit script; this commit restores the README and moves the app into streamlit_app.py.

Licensing / Contributing
- Add license and contribution guidelines as needed.
