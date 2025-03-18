import yfinance as yf
import pandas as pd
import boto3
import json
import os
from dotenv import load_dotenv
from yahooquery import search
from deep_translator import GoogleTranslator
from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_stock_symbol(company_name):
    result = search(company_name)
    quotes = result.get("quotes", [])
    print(quotes)
    if quotes:
        return quotes[0]["symbol"]
    return None

print(get_stock_symbol("AAPL"))
