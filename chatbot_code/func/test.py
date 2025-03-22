from datetime import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import pandas as pd
import pickle

def compare_data(symbol):
    today = datetime.today()

    #현재 - 내일 주가예측, 추후 - 기간 user_input으로 받아 주가예측
    n_today = today + relativedelta(days=1)    
    formatted_n_today = n_today.strftime("%Y-%m-%d")

    df = pd.DataFrame()

    #주말 계산 필요
    #ma9
    ma9_date = today - relativedelta(days=11)
    formatted_ma9_date = ma9_date.strftime("%Y-%m-%d")
    df_ma9 = yf.download(symbol, start=formatted_ma9_date, end=formatted_n_today)
    df["MA9"] = df_ma9["Close"].rolling(window=9).mean()

    #ma12
    ma12_date = today - relativedelta(days=16)
    formatted_ma12_date = ma12_date.strftime("%Y-%m-%d")
    df_ma12 = yf.download(symbol, start=formatted_ma12_date, end=formatted_n_today)
    df["MA12"] = df_ma12["Close"].rolling(window=12).mean()

    #ma21
    ma21_date = today - relativedelta(days=29)
    formatted_mad21_date = ma21_date.strftime("%Y-%m-%d")
    df_ma21 = yf.download(symbol, start=formatted_mad21_date, end=formatted_n_today)
    df["MA21"] = df_ma21["Close"].rolling(window=21).mean()

    #vol_ma5
    vol_ma5 = today - relativedelta(days=7)
    formatted_vol_ma5 = vol_ma5.strftime("%Y-%m-%d")
    df_vol_ma5 = yf.download(symbol, start=formatted_vol_ma5, end=formatted_n_today)
    df["Vol_MA5"] = df_vol_ma5["Volume"].rolling(window=5).mean()

    #pct_change
    pct_change = today - relativedelta(days=3)
    formatted_pct_change = pct_change.strftime("%Y-%m-%d")
    pct_change = yf.download(symbol, start=formatted_pct_change, end=formatted_n_today)
    df["Pct_change"] = pct_change["Close"].pct_change()
    
    df.dropna(inplace=True)

    return df

import io
def dataframe_to_bytes(df):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False)
    return buffer.getvalue()

stock = compare_data("AAPL")


trans_stock = dataframe_to_bytes(stock)

print(trans_stock)