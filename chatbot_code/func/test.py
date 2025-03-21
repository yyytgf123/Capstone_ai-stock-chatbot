from datetime import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf

def stock_data(symbol):
    today = datetime.today()
    formatted_today = today.strftime("%Y-%m-%d")
    two_months_ago = today - relativedelta(months=3)
    formatted_three_months_ago = two_months_ago.strftime("%Y-%m-%d")

    df = yf.download(symbol, start=formatted_three_months_ago, end=formatted_today)    
    """
    MACD DataSet
    """
    df["MA5"] = df['Close'].rolling(window=5).mean
    df["MA20"] = df['Close'].rolling(window=20).mean
    df = df[['Open','High','Low','Close','Volume','MA5', 'MA20']]
    
    # print(df["MA5"])

    df['Target'] = df['Close'].shift(-1)
    df.dropna(inplace=True)

# print(stock_data("AAPL"))
