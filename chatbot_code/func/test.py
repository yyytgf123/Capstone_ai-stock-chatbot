from datetime import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import pandas as pd
import pickle

### compare data ###
def compare_data(symbol):
    today = datetime.today()

    #현재 - 내일 주가예측, 추후 - 기간 user_input으로 받아 주가예측
    n_today = today + relativedelta(days=1)    
    formatted_n_today = n_today.strftime("%Y-%m-%d")

    df = pd.DataFrame()

    #주말 계산 필요
    #ma9
    ma9_date = today - relativedelta(days=14)
    formatted_ma9_date = ma9_date.strftime("%Y-%m-%d")
    df_ma9 = yf.download(symbol, start=formatted_ma9_date, end=formatted_n_today)
    df["MA9"] = df_ma9["Close"].rolling(window=9).mean()

    #ma12
    ma12_date = today - relativedelta(days=20)
    formatted_ma12_date = ma12_date.strftime("%Y-%m-%d")
    df_ma12 = yf.download(symbol, start=formatted_ma12_date, end=formatted_n_today)
    df["MA12"] = df_ma12["Close"].rolling(window=12).mean()

    #ma26
    ma26_date = today - relativedelta(days=40)
    formatted_mad26_date = ma26_date.strftime("%Y-%m-%d")
    df_ma26 = yf.download(symbol, start=formatted_mad26_date, end=formatted_n_today)
    df["MA26"] = df_ma26["Close"].rolling(window=26).mean()

    #vol_ma5
    vol_ma5 = today - relativedelta(days=8)
    formatted_vol_ma5 = vol_ma5.strftime("%Y-%m-%d")
    df_vol_ma5 = yf.download(symbol, start=formatted_vol_ma5, end=formatted_n_today)
    df["Vol_MA5"] = df_vol_ma5["Volume"].rolling(window=5).mean()

    #pct_change
    pct_change = today - relativedelta(days=4)
    formatted_pct_change = pct_change.strftime("%Y-%m-%d")
    pct_change = yf.download(symbol, start=formatted_pct_change, end=formatted_n_today)
    df["Pct_change"] = pct_change["Close"].pct_change()
    
    df = df[['MA9', 'MA12', 'MA26', 'Vol_MA5', 'Pct_change']]

    # df.iloc[-1:] #마지막 행만 가져옴

    return df.iloc[-1:]

import io
def dataframe_to_bytes(df):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False)
    return buffer.getvalue()

test_data = compare_data("AAPL")

type_trans_test_data = dataframe_to_bytes(test_data)

print(type_trans_test_data)
