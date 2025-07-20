import pandas as pd
import streamlit as st
import yfinance as yf
def load_midcap_stocks():
    df = pd.read_csv("ind_niftymidcap150list.csv")
    df["Symbol"] = df["Symbol"].astype(str).str.upper() + ".NS"
    return dict(zip(df["Company Name"], df["Symbol"]))
  
midcap_stocks = load_midcap_stocks()

# Page configuration
st.set_page_config(page_title="📈 Midcap Stock Recommender", layout="wide")
st.title("🤖 Nifty Midcap 150 Stock Recommender")

def fetch_stock_data(stock_dict):
    """
    Fetch key stock information for given tickers from Yahoo Finance.
    Returns a DataFrame with Name, Ticker, Sector, Market Cap, P/E Ratio, and Price.
    """
    records = []
    for name, symbol in stock_dict.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            records.append({
                "Name": name,
                "Ticker": symbol,
                "Sector": info.get("sector", "Unknown"),
                "Market Cap": info.get("marketCap", 0),
                "P/E Ratio": info.get("trailingPE", None),
                "Price": info.get("currentPrice", None)
            })
        except Exception:
            # Skip stocks if info retrieval fails
            continue
    return pd.DataFrame(records)


