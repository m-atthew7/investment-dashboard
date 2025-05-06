import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Streamlit App Title
st.title("Cumulative Portfolio Value Calculator")

# User Input: Select Stocks
st.sidebar.header("User Input")
tickers = st.sidebar.text_input("Enter stock tickers (comma-separated):", "AAPL, MSFT, GOOGL")
tickers = [ticker.strip().upper() for ticker in tickers.split(",")]

# User Input: Initial Investment
initial_investment = st.sidebar.number_input("Initial Investment ($):", min_value=1000, value=10000, step=500)

# User Input: Start and End Date
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2023-12-31"))

# Fetch Stock Data
st.write("### Fetching Stock Data...")
raw_data = yf.download(
    tickers,
    start=start_date,
    end=end_date,
    progress=False,
    group_by='ticker',
    auto_adjust=True
)

# Extract Close prices
try:
    if isinstance(raw_data.columns, pd.MultiIndex):
        data = raw_data.loc[:, pd.IndexSlice[:, 'Close']]
        data.columns = data.columns.get_level_values(0)  # Flatten columns
    else:
        data = raw_data[['Close']]  # For single ticker
except KeyError:
    st.error("'Close' column not found in downloaded data.")
    st.stop()

# Show error if no data is returned
if data.empty:
    st.error("No stock data returned. Try different tickers or date range.")
    st.stop()

st.write("Stock Prices:", data.tail())

# Calculate Daily Returns
daily_returns = data.pct_change().dropna()

# Add input for custom weights
st.sidebar.write("### Portfolio Weights")
weights = []
for ticker in tickers:
    weight = st.sidebar.number_input(f"Weight for {ticker}:", min_value=0.0, max_value=1.0, value=1.0/len(tickers))
    weights.append(weight)

# Normalize weights to sum to 1
weights = np.array(weights)
weights /= np.sum(weights)

# Display normalized weights
st.write("Normalized Weights:")
for i, ticker in enumerate(tickers):
    st.write(f"{ticker}: {weights[i]:.2%}")

# Calculate Portfolio Daily Returns
portfolio_returns = daily_returns.dot(weights)

# Calculate Cumulative Portfolio Value
cumulative_returns = (1 + portfolio_returns).cumprod()
portfolio_value = initial_investment * cumulative_returns

# Plot Cumulative Portfolio Value
st.write("### Cumulative Portfolio Value Over Time")
fig, ax = plt.subplots()
ax.plot(portfolio_value, color='green', linewidth=2)
ax.axhline(initial_investment, color='red', linestyle='--', label="Initial Investment")
ax.set_xlabel("Date")
ax.set_title("Cumulative Portfolio Value")
ax.set_ylabel("Portfolio Value ($)")
ax.legend()
plt.xticks(rotation=45)
st.pyplot(fig)

# Display Final Portfolio Value
st.write("### Final Portfolio Value:")
if not portfolio_value.empty:
    st.write(f"${portfolio_value.iloc[-1]:,.2f}")
else:
    st.write("No data to display.")
