import yfinance as yf
import boto3
import numpy as np
import io
import os
import pandas as pd
from yahooquery import search
from deep_translator import GoogleTranslator
from datetime import datetime
from dateutil.relativedelta import relativedelta
# sagemkaer #
import sagemaker
from sklearn.model_selection import train_test_split
from sagemaker import get_execution_role
# --------- #

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

### s3 upload ###
def traindata_s3_upload(user_input):
    symbol = find_company_symbol(user_input)
    """
    .csv -> s3
    """
    df = stock_data(symbol)
    df.to_csv("stock_data.csv", index=False, header=False) #df -> .csv 변경 -> data에 저장
    data_to_read = pd.read_csv("stock_data.csv", delimiter=";") #csv -> pd dataFrame

    print(data_to_read)

    train_data, test_data = train_test_split(data_to_read, test_size=0.2)
    test_data, validation_data = train_test_split(data_to_read, test_size=0.5)

    bucket = "chatbot-sagemaker-s3"
    prefix = "sagemkaer/white-data" #s3 저장 경로

    sagemaker_session = sagemaker.Session() #sagemaker 리소스 관리
    role = "arn:aws:iam::047719624346:role/chatbot-sagemaker-policy"    
    
    train_file_path = 'train.csv'
    train_data.to_csv(train_file_path, index=False, header=False) #index, header 불필요 데이터 제거
    s3_train_data = sagemaker_session.upload_data(path=train_file_path, bucket=bucket, key_prefix=prefix+'/train')

    test_file_path = 'test.csv'
    test_data.to_csv(test_file_path, index=False, header=False)
    s3_test_data = sagemaker_session.upload_data(path=test_file_path, bucket=bucket, key_prefix=prefix+'/test')

    validation_file_path = 'validation.csv'
    validation_data.to_csv(validation_file_path, index=False, header=False)
    s3_validation_data = sagemaker_session.upload_data(path=validation_file_path, bucket=bucket, key_prefix=prefix+'/validation')
### --------- ###

traindata_s3_upload("애플")