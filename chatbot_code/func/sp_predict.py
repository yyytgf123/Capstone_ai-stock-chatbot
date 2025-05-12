import sagemaker.image_uris
import yfinance as yf
import boto3
import pandas as pd
import requests
from deep_translator import GoogleTranslator
from datetime import datetime
from dateutil.relativedelta import relativedelta
import io
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def search(company_name):
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

###  Dataframe -> test/csv ###
def dataframe_to_bytes(df):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False)
    return buffer.getvalue()
### ------------------- ###

### find symbol ###
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
        if not name_li.isascii():
            name_li = translate_to_english(name_li)
        symbol = search(name_li)
        if symbol:
            return symbol
    return None
### ---------- ###

### close value return ###
def stock_close(symbol):
    today = datetime.today()
    formatted_today = today.strftime("%Y-%m-%d")
    two_months_ago = today - relativedelta(months=6)
    formatted_three_months_ago = two_months_ago.strftime("%Y-%m-%d")

    df = yf.download(symbol, start=formatted_three_months_ago, end=formatted_today)
    
    return df
### ----------------- ###

### train data ###
def stock_data(symbol):
    today = datetime.today()
    formatted_today = today.strftime("%Y-%m-%d")
    two_months_ago = today - relativedelta(months=3)
    formatted_three_months_ago = two_months_ago.strftime("%Y-%m-%d")

    """
    Predict DataSet
    """
    df = yf.download(symbol, start=formatted_three_months_ago, end=formatted_today)   
    df["MA9"] = df['Close'].rolling(window=9).mean()
    df["MA12"] = df['Close'].rolling(window=12).mean()
    df["MA26"] = df['Close'].rolling(window=26).mean()
    df["Vol_MA5"] = df['Volume'].rolling(window=5).mean()
    df["Pct_change"] = df['Close'].pct_change()
    df["Close"] = df["Close"].shift(-1) #예측 값 -> y
  
    df = df[['MA9', 'MA12', 'MA26', 'Vol_MA5','Pct_change', 'Close']]

    df.dropna(inplace=True)
    
    return df
### ---------- ###

### compare data ###
def compare_data(symbol):
    today = datetime.today()

    #현재 - 내일 주가예측, 추후 - 기간 user_input으로 받아 주가예측
    n_today = today + relativedelta(days=1)    
    formatted_n_today = n_today.strftime("%Y-%m-%d")

    df = pd.DataFrame()

    #주말 계산 필요
    #ma9
    ma9_date = today - relativedelta(days=14)
    formatted_ma9_date = ma9_date.strftime("%Y-%m-%d")
    df_ma9 = yf.download(symbol, start=formatted_ma9_date, end=formatted_n_today)
    df["MA9"] = df_ma9["Close"].rolling(window=9).mean()

    #ma12
    ma12_date = today - relativedelta(days=20)
    formatted_ma12_date = ma12_date.strftime("%Y-%m-%d")
    df_ma12 = yf.download(symbol, start=formatted_ma12_date, end=formatted_n_today)
    df["MA12"] = df_ma12["Close"].rolling(window=12).mean()

    #ma26
    ma26_date = today - relativedelta(days=40)
    formatted_mad26_date = ma26_date.strftime("%Y-%m-%d")
    df_ma26 = yf.download(symbol, start=formatted_mad26_date, end=formatted_n_today)
    df["MA26"] = df_ma26["Close"].rolling(window=26).mean()

    #vol_ma5
    vol_ma5 = today - relativedelta(days=8)
    formatted_vol_ma5 = vol_ma5.strftime("%Y-%m-%d")
    df_vol_ma5 = yf.download(symbol, start=formatted_vol_ma5, end=formatted_n_today)
    df["Vol_MA5"] = df_vol_ma5["Volume"].rolling(window=5).mean()

    #pct_change
    pct_change = today - relativedelta(days=4)
    formatted_pct_change = pct_change.strftime("%Y-%m-%d")
    pct_change = yf.download(symbol, start=formatted_pct_change, end=formatted_n_today)
    df["Pct_change"] = pct_change["Close"].pct_change()
    
    df = df[['MA9', 'MA12', 'MA26', 'Vol_MA5', 'Pct_change']]

    return df.iloc[-1:] #마지막 값만 출력


### data_set setting -> training ###
import sagemaker
from sklearn.model_selection import train_test_split

def sagemaker_training(user_input):
    symbol = find_company_symbol(user_input)
    """
    data_set sagemaker s3 upload
    """
    df = stock_data(symbol)
    df.to_csv("stock_data.csv", index=False, header=False) #df -> .csv 변경 -> data에 저장
    data_to_read = pd.read_csv("stock_data.csv", delimiter=",") #csv -> pd dataFrame

    # dy = stock_close(symbol)
    # y = dy['Close'].shift(-1) #다음 날 종가를 예측하기 위해 -1씩 밀기

    train_data, test_data = train_test_split(data_to_read, test_size=0.2) #8:2로 나눔

    bucket = "chatbot-sagemaker-s3"
    prefix = "yfinace-data/white-data" #s3 저장 경로

    sagemaker_session = sagemaker.Session() #sagemaker 리소스 연결
    #console에서 role 설정 상태
    # role = "arn:aws:iam::047719624346:role/chatbot-sagemaker-policy"    
    
    train_file_path = 'train.csv'
    #df == X
    #input 값 - MA9, MA12, MA26, Vol_MA5, Pct_Change, 타겟 값 - Close(예측할 값)
    # train_data = pd.concat([df, y], axis=1)
    train_data.to_csv(train_file_path, index=False, header=False) #index, header 불필요 데이터 제거
    s3_train_data = sagemaker_session.upload_data(path=train_file_path, bucket=bucket, key_prefix=prefix+'/train')

    test_file_path = 'test.csv'
    test_data.to_csv(test_file_path, index=False, header=False)
    s3_test_data = sagemaker_session.upload_data(path=test_file_path, bucket=bucket, key_prefix=prefix+'/test')

    """
    data_set training, xgboost algorithm 사용
    """
    sagemaker_session = sagemaker.Session()
    container = sagemaker.image_uris.retrieve("xgboost", sagemaker_session.boto_region_name, "latest") #xgboost:latest 사용

    traindata_bucket = "s3://chatbot-sagemaker-s3/output-data"

    #docker에서 제공하는 sagemaker.estimator.Estimator 사용, "Tensorflow" 고려
    xgboost = sagemaker.estimator.Estimator(container,      
                                            role = "arn:aws:iam::047719624346:role/chatbot-sagemaker-policy",
                                            train_instance_count = 1,
                                            train_instance_type = "ml.m5.xlarge",
                                            output_path = traindata_bucket,
                                            sagemaker_session=sagemaker_session,
                                            endpoint_name="sg_sp_predict") #sagemaker 모델 학습, 데이터 저장, 배포 관리 -> 세션 전달

    xgboost.set_hyperparameters(max_depth=4, #트리 최대 깊이 설정
                                eta=0.2, #가중치 크기 업데이트 조절
                                gamma=4, #리프 노드를 추가할 대 최소 손실 감소량 -> 잡음에 의해 분할방지하여 과적합 줄임
                                min_child_width=6, #리프 노드가 분할되기 위한 필요한 최소 샘플 가중치 합
                                subsample=0.6, #각 트리를 학습할 때 사용하는 샘플링 비율
                                silent=0, #학습 중 로그 출력 
                                objective='reg:linear', #최적화할 목표 함수(손실 함수), reg:linear -> MSE 기반 회귀
                                num_round=100) #트리의 개수

    s3_input_train_data = sagemaker.TrainingInput(s3_data=s3_train_data, content_type="csv")
    xgboost.fit({'train':s3_input_train_data})

    """
    모델 배포
    """
    #배포
    xgboost_deploy = xgboost.deploy(initial_instance_count=1,
                                    instance_type='ml.m5.xlarge')
    
    endpoint_name = xgboost_deploy.endpoint_name #response에 넣을 값

    #비교 데이터 input
    runtime = boto3.client('runtime.sagemaker')
    
    test_data = compare_data(symbol)    
    type_trans_test_data = dataframe_to_bytes(test_data)
     
    response = runtime.invoke_endpoint(EndpointName=endpoint_name,
                                       ContentType='text/csv',
                                       Body=type_trans_test_data)
    
    result = json.loads(response['Body'].read().decode())
    
    return result
### ------------------------------------------- ###