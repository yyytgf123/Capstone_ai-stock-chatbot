import requests
import yfinance as yf

### 주요자산 가격 ###
def get_asset_prices():
    try:

        # 원/달러 환율
        exchange_rate = yf.Ticker("USDKRW=X").history(period="1d")["Close"].iloc[-1]

        # 금, 은, 원유(WTI) 가격 가져오기 (yfinance 사용)
        gold = yf.Ticker("GC=F").history(period="1d")["Close"].iloc[-1]
        silver = yf.Ticker("SI=F").history(period="1d")["Close"].iloc[-1]
        oil = yf.Ticker("CL=F").history(period="1d")["Close"].iloc[-1]

        # 비트코인 가격 가져오기 (CoinGecko API 사용) 추가로 install
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url)
        bitcoin = response.json()["bitcoin"]["usd"]

        return {
            "gold_krw": round(gold * exchange_rate, 2),
            "silver_krw": round(silver * exchange_rate, 2),
            "oil_krw": round(oil * exchange_rate, 2),
            "bitcoin_krw": round(bitcoin * exchange_rate, 2),
            "exchange_rate": round(exchange_rate, 2)  # 현재 원/달러 환율
        }
    except Exception as e:
        print("자산 가격 가져오기 오류:", str(e))
        return {"error": "실시간 데이터를 가져오는 중 오류 발생"}
### --------------------- ###
