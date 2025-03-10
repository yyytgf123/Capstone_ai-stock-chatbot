from flask import Flask, request, jsonify, render_template
import os
import boto3
import json
import yfinance as yf
from yahooquery import search
from company_dict import company_dict
from deep_translator import GoogleTranslator

def get_stock_symbol(company_name):
    result = search(company_name)
    quotes = result.get("quotes", [])
    if quotes:
        return quotes[0]["symbol"]
    return None

def translate_to_english(translate):
    return GoogleTranslator(source='ko', target='en').translate(translate)

def find_company_symbol(name):
    name_list = name.split()
    for name_li in name_list:
        print(name_li)
        if not name.isascii():
            symbol_storage = []
            name = translate_to_english(name_li)
            name = name.upper()
            symbol_storage.append(get_stock_symbol(name))

    result = search(symbol_storage)
    if result and 'quotes' in result and result["quotes"]:
        return result['quotes'][0]['symbol']
    return None

print(find_company_symbol("sk하이닉스 주가 알려줘"))