import pandas as pd
import yfinance as yf

df = yf.download("AAPL", start="2024-01-01", end="2025-03-20")

df["MA5"] = df["Close"].rolling(window=5).mean()
df["MA20"] = df["Close"].rolling(window=20).mean()

df["Return"] = df["Close"].pct_change()

df["Vol_MA5"] = df["Volume"].rolling(window=5).mean()

# print(df["Vol_MA5"])