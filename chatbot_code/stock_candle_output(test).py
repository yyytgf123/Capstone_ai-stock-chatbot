import mplfinance as mpf
import yfinance as yf
from pandas_datareader import data as pdr
import yfinance as yf

aapl = yf.Ticker('AAPL')
stock_data = aapl.history(start="2025-01-03", end="2025-03-08")

mc = mpf.make_marketcolors(up="r", down="b")
s = mpf.make_mpf_style(base_mpf_style="starsandstripes", marketcolors=mc)
mpf.plot(stock_data, type='candle', style=s, volume=True, mav=(5, 10, 60))