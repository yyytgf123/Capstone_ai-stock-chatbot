import yfinance as yf
import pandas as pd
import boto3
from datetime import datetime
from dateutil.relativedelta import relativedelta

bucket_name = "chatbot-sagemaker-s3"
s3_key = "stock_data.csv"

def stock_data():
    today = datetime.today()
    formatted_today = today.strftime("%Y-%m-%d")
    two_months_ago = today - relativedelta(months=3)
    formatted_three_months_ago = two_months_ago.strftime("%Y-%m-%d")

    df = yf.download("AAPL", start=formatted_three_months_ago, end=formatted_today)
    df = df[['Open','High','Low','Close','Volume']]
    df['Target'] = df['Close'].shift(-1)
    df.dropna(inplace=True)
    return df

df = stock_data()
df.to_csv("stock_data.csv", index=False)

s3_client = boto3.client("s3")
s3_client.upload_file("stock_data.csv", bucket_name, s3_key)

# 이후 작업
# 1. s3(.csv)로 sagemaker 모델로 훈련
# 2. sagemaker endpoint
# 3. bedrock 출력