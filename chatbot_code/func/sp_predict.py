import yfinance as yf
import pandas as pd
import boto3
import os
from dotenv import load_dotenv
from yahooquery import search
from deep_translator import GoogleTranslator
from datetime import datetime
from dateutil.relativedelta import relativedelta

### 임시 ###
load_dotenv()
inferenceProfileArn= os.getenv("BEDROCK_INFERENCE_PROFILE_ARN")
bedrock_client = boto3.client("bedrock-runtime", region_name="ap-northeast-2")
### --- ###

bucket_name = "chatbot-sagemaker-s3"
upload_file_name = "stock_data.csv"

### fid symbol ###
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
    symbol_storage = []
    for name_li in name_list:
        if not name.isascii():
            name = translate_to_english(name_li)
            name = name.upper()
            symbol_storage.append(get_stock_symbol(name))

    result = search(symbol_storage)
    if result and 'quotes' in result and result["quotes"]:
        return result['quotes'][0]['symbol']
    return None
### ---------- ###

### get .csv ###
def stock_data(symbol):
    today = datetime.today()
    formatted_today = today.strftime("%Y-%m-%d")
    two_months_ago = today - relativedelta(months=3)
    formatted_three_months_ago = two_months_ago.strftime("%Y-%m-%d")

    df = yf.download(symbol, start=formatted_three_months_ago, end=formatted_today)
    df = df[['Open','High','Low','Close','Volume']]
    df['Target'] = df['Close'].shift(-1)
    df.dropna(inplace=True)
    return df
### ---------- ###

def s3_upload(user_input):
    symbol = find_company_symbol(user_input)
    """
    .csv -> s3
    """
    df = stock_data(symbol)
    df.to_csv("stock_data.csv", index=False) #df -> .csv 변경   
    s3_client = boto3.client("s3")
    
    # s3에 파일 지속적으로 쌓임 -> 고려
    # s3_client.upload_file("stock_data.csv", bucket_name, f"stock_data_{symbol}.csv")
    s3_client.upload_file("stock_data.csv", bucket_name, upload_file_name)
### --------------- ###

# 이후 작업
# 1. s3(.csv)로 sagemaker 모델로 훈련
# 2. sagemaker endpoint
# 3. bedrock 출력