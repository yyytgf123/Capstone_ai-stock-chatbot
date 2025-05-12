import yfinance as yf
import time
import requests
from deep_translator import GoogleTranslator

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def search_yahoo_symbol(company_name):
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={company_name}"
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code != 200:
            print(f"🔴 HTTP 오류: {response.status_code}")
            return None

        results = response.json().get("quotes", [])
        if results:
            return results[0]["symbol"]
    except Exception as e:
        print("❌ 심볼 검색 오류:", e)

    return None

def get_stock_symbol(company_name):
    return search_yahoo_symbol(company_name)

def get_stock_price(symbol):
    try:
        time.sleep(2) 
        stock = yf.Ticker(symbol)
        data = stock.history(period="5d")

        if data.empty:
            return "데이터 없음"

        price = data["Close"].iloc[-1]
        return round(price, 2)
    except Exception as e:
        print("❌ 주가 가져오기 오류:", e)
        return "오류"

def get_currency(symbol):
    if ".KQ" in symbol or ".KS" in symbol:
        return "원"
    return "달러"

def translate_to_english(translate):
    try:
        return GoogleTranslator(source='ko', target='en').translate(translate)
    except:
        return translate

def find_company_symbol(name):
    name_list = name.split()
    for name_li in name_list:
        if not name_li.isascii():
            name_li = translate_to_english(name_li)
        symbol = search_yahoo_symbol(name_li)
        if symbol:
            return symbol
    return None
