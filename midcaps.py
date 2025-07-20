import pandas as pd

def load_midcap_list():
   df = pd.read_csv('gdrive/MyDrive/oil.csv')
    df["Symbol"] = df["Symbol"].astype(str) + ".NS"
    return dict(zip(df["Company Name"], df["Symbol"]))

midcap_stocks = load_midcap_list()

import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config("📈 Midcap Stock Recommender", layout="wide")
st.title("🤖 Nifty Midcap 150 Stock Recommender")

@st.cache_data
def load_midcap_list():
    url = "https://www.niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv"
    df = pd.read_csv(url)
    df["Symbol"] = df["Symbol"].astype(str) + ".NS"
    return dict(zip(df["Company Name"], df["Symbol"]))

midcap_stocks = load_midcap_list()

@st.cache_data
def fetch_stock_data(stock_dict):
    rows = []
    for name, symbol in stock_dict.items():
        try:
            info = yf.Ticker(symbol).info
            rows.append({
                "Name": name,
                "Ticker": symbol,
                "Sector": info.get("sector", "Unknown"),
                "Market Cap": info.get("marketCap", 0),
                "P/E Ratio": info.get("trailingPE", None),
                "Price": info.get("currentPrice", None)
            })
        except:
            continue
    return pd.DataFrame(rows)

df = fetch_stock_data(midcap_stocks)

# Sidebar filters
st.sidebar.header("Filter Criteria")
sectors = st.sidebar.multiselect("Sector", df["Sector"].dropna().unique(), default=df["Sector"].dropna().unique())
pe_min, pe_max = st.sidebar.slider("P/E Ratio", 0.0, 200.0, (0.0, 50.0))
min_mc = st.sidebar.number_input("Min Market Cap (₹)", min_value=0, value=1e10)
sort_by = st.sidebar.selectbox("Recommend Based On", ["Lowest P/E", "Highest Market Cap", "Highest Price"])

# Filter & Recommend
filtered = df[
    (df["Sector"].isin(sectors)) &
    (df["P/E Ratio"].fillna(0).between(pe_min, pe_max)) &
    (df["Market Cap"] >= min_mc)
]

if sort_by == "Lowest P/E":
    recommended = filtered.sort_values("P/E Ratio")
elif sort_by == "Highest Market Cap":
    recommended = filtered.sort_values("Market Cap", ascending=False)
else:
    recommended = filtered.sort_values("Price", ascending=False)

if not recommended.empty:
    top = recommended.iloc[0]
    st.success(f"✅ Recommended: **{top['Name']} ({top['Ticker']})**")
    st.dataframe(pd.DataFrame([top]))
    with st.expander("📈 6-Month Price Chart"):
        hist = yf.download(top["Ticker"], period="6mo", interval="1d")
        st.line_chart(hist["Close"])
else:
    st.warning("No stocks match your criteria. Try different filters!")
