import yfinance as yf
import pandas as pd
import requests
# from yahooquery import search
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

def translate_to_english(translate):
    return GoogleTranslator(source='ko', target='en').translate(translate)

def find_company_symbol(name):
    name_list = name.split()
    for name_li in name_list:
        if not name_li.isascii():
            name_li = translate_to_english(name_li)
        symbol = search_yahoo_symbol(name_li)
        if symbol:
            return symbol
    return None

### ----------------- ###


def find_f_statement(user_input):
    symbol = find_company_symbol(user_input)
    # symbol -> ticker
    ticker = yf.Ticker(symbol)

    financials = ticker.financials #재무상태표
    balance_sheet =  ticker.balance_sheet #손익계산서
    cash_flow = ticker.cash_flow #현금흐름표
    # -------------------------------- #
    date = financials.columns[0]
    date2 = balance_sheet.columns[0]

    revenue = financials.loc["Total Revenue", date] #매출
    operating_income = financials.loc["Operating Income", date] #영업이익
    net_income = financials.loc["Net Income", date] #순이익

    total_assets = balance_sheet.loc["Total Assets", date2] #자산 총계
    total_equity = balance_sheet.loc["Stockholders Equity", date2] #자본 총계
    total_liabilities = balance_sheet.loc["Total Liabilities Net Minority Interest", date2]

    ORM = operating_income / revenue #영업이익률
    net_profit_margion = net_income / revenue #순이익률
    DE_ratio = total_liabilities / total_equity #부채비율
    ROE = net_income / total_equity #ROE
    ROA = net_income / total_assets #ROA

    f_statement_data = [ORM, net_profit_margion, DE_ratio, ROE, ROA]
    
    return f_statement_data