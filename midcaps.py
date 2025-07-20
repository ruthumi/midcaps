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
    Returns a DataFrame with Name, Ticker, Industry, Market Cap, P/E Ratio, and Price.
    """
    records = []
    for name, symbol in stock_dict.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            records.append({
                "Name": name,
                "Ticker": symbol,
                "Industry": info.get("Industry", "Unknown"),
                "Market Cap": info.get("marketCap", 0),
                "P/E Ratio": info.get("trailingPE", None),
                "Price": info.get("currentPrice", None)
            })
        except Exception:
            # Skip stocks if info retrieval fails
            continue
    return pd.DataFrame(records)

# Load data
midcap_stocks = load_midcap_stocks()
df = fetch_stock_data(midcap_stocks)

# Sidebar filters
st.sidebar.header("Filter Criteria")

# Industry filter (default: all available Industrys)
available_Industrys = df["Industry"].dropna().unique()
selected_Industrys = st.sidebar.multiselect("Industry", options=available_Industrys, default=available_Industrys)

# P/E ratio filter
pe_min, pe_max = st.sidebar.slider("P/E Ratio Range", 0.0, 200.0, (0.0, 50.0))

# Minimum market capitalization filter
min_market_cap = st.sidebar.number_input("Minimum Market Cap (₹)", min_value=0, value=10_000_000_000, step=1_000_000_000)

# Sorting preference for recommendation
sort_options = {
    "Lowest P/E": ("P/E Ratio", True),
    "Highest Market Cap": ("Market Cap", False),
    "Highest Price": ("Price", False)
}
sort_choice = st.sidebar.selectbox("Recommend Based On", list(sort_options.keys()))

# Filter dataframe based on user criteria
filtered_df = df[
    (df["Industry"].isin(selected_Industrys)) &
    (df["P/E Ratio"].fillna(0).between(pe_min, pe_max)) &
    (df["Market Cap"] >= min_market_cap)
]

# Sort based on user preference
sort_col, ascending = sort_options[sort_choice]
recommended_df = filtered_df.sort_values(by=sort_col, ascending=ascending)

# Display results
if not recommended_df.empty:
    top_stock = recommended_df.iloc[0]
    st.success(f"✅ Recommended Stock: **{top_stock['Name']} ({top_stock['Ticker']})**")
    
    st.dataframe(recommended_df.reset_index(drop=True))
    
    with st.expander("📈 6-Month Price Chart"):
        hist = yf.download(top_stock["Ticker"], period="6mo", interval="1d", progress=False)
        if not hist.empty:
            st.line_chart(hist["Close"])
        else:
            st.info("Price chart data unavailable.")
else:
    st.warning("No stocks match your criteria. Please adjust the filters and try again.")

