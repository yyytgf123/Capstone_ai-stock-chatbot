# import sagemaker.image_uris
# import yfinance as yf
# import boto3
# import numpy as np
# import io
# import os
# import pandas as pd
# from yahooquery import search
# from deep_translator import GoogleTranslator
# from datetime import datetime
# from dateutil.relativedelta import relativedelta

# ### find symbol ###
# def get_stock_symbol(company_name):
#     result = search(company_name)
#     quotes = result.get("quotes", [])
#     if quotes:
#         return quotes[0]["symbol"]
#     return None

# def translate_to_english(translate):
#     return GoogleTranslator(source='ko', target='en').translate(translate)

# def find_company_symbol(name):
#     name_list = name.split()
#     symbol_storage = []
#     for name_li in name_list:
#         if not name.isascii():
#             name = translate_to_english(name_li)
#             name = name.upper()
#             symbol_storage.append(get_stock_symbol(name))

#     result = search(symbol_storage)
#     if result and 'quotes' in result and result["quotes"]:
#         return result['quotes'][0]['symbol']
#     return None
# ### ---------- ###

# ### get .csv ###
# def stock_data(symbol):
#     today = datetime.today()
#     formatted_today = today.strftime("%Y-%m-%d")
#     two_months_ago = today - relativedelta(months=3)
#     formatted_three_months_ago = two_months_ago.strftime("%Y-%m-%d")

#     df = yf.download(symbol, start=formatted_three_months_ago, end=formatted_today)
#     df = df[['Open','High','Low','Close','Volume']]

#     """
#     MACD DataSet
#     """
#     df["MA5"] = df['Close'].rolling(window=5).mean
#     df["MA20"] = df['Close'].rolling(window=20).mean

#     print(df)

#     # X = df[["Open", "High", "Low", "Volume", "MA5", "MA20", "Return", "Vol_MA5"]]

#     df['Target'] = df['Close'].shift(-1)
#     df.dropna(inplace=True)
#     return df
# ### ---------- ###

# ### data_set sagemaker s3 upload ###
# import sagemaker
# from sklearn.model_selection import train_test_split

# def traindata_s3_upload(user_input):
#     symbol = find_company_symbol(user_input)
#     """
#     .csv -> s3
#     """
#     df = stock_data(symbol)
#     df.to_csv("stock_data.csv", index=False, header=False) #df -> .csv 변경 -> data에 저장
#     data_to_read = pd.read_csv("stock_data.csv", delimiter=";") #csv -> pd dataFrame

#     print(data_to_read)

#     train_data, test_data = train_test_split(data_to_read, test_size=0.2) #8:2로 나눔
#     # test_data, validation_data = train_test_split(data_to_read, test_size=0.5)

#     bucket = "chatbot-sagemaker-s3"
#     prefix = "sagemkaer/white-data" #s3 저장 경로

#     sagemaker_session = sagemaker.Session() #sagemaker 리소스 연결
#     #console에서 role 설정 상태
#     # role = "arn:aws:iam::047719624346:role/chatbot-sagemaker-policy"    
    
#     train_file_path = 'train.csv'
#     train_data.to_csv(train_file_path, index=False, header=False) #index, header 불필요 데이터 제거
#     s3_train_data = sagemaker_session.upload_data(path=train_file_path, bucket=bucket, key_prefix=prefix+'/train')

#     test_file_path = 'test.csv'
#     test_data.to_csv(test_file_path, index=False, header=False)
#     s3_test_data = sagemaker_session.upload_data(path=test_file_path, bucket=bucket, key_prefix=prefix+'/test')

#     """
#     보류
#     """
#     # validation_file_path = 'validation.csv'
#     # validation_data.to_csv(validation_file_path, index=False, header=False)
#     # s3_validation_data = sagemaker_session.upload_data(path=validation_file_path, bucket=bucket, key_prefix=prefix+'/validation')
# ### --------- ###

# ### data_set training, xgboost algorithm 사용 ###
# from sagemaker.amazon.amazon_estimator import get_image_uri
# from sagemaker import get_execution_role

# bucket = "chatbot-sagemaker-s3"

# sagemaker_session = sagemaker.Session()
# container = sagemaker.image_uris.retrieve("xgboost", sagemaker_session.boto_region_name, "latest") #xgboost:latest 사용

# #docker에서 제공하는 sagemaker.estimator.Estimator 사용, "Tensorflow" 고려
# xgboost = sagemaker.estimator.Estimator(container,      
#                                         role = get_execution_role(),
#                                         train_instance_count = 2,
#                                         train_instance_type = "ml.c4.xlarge",
#                                         output_path = bucket,
#                                         sagemaker_session=sagemaker_session) #sagemaker 모델 학습, 데이터 저장, 배포 관리 -> 세션 전달

# xgboost.set_hyperparameters(max_depth=4, #트리 최대 깊이 설정
#                             eta=0.2, #가중치 크기 업데이트 조절
#                             gamma=4, #리프 노드를 추가할 대 최소 손실 감소량 -> 잡음에 의해 분할방지하여 과적합 줄임
#                             min_child_width=6, #리프 노드가 분할되기 위한 필요한 최소 샘플 가중치 합
#                             subsample=0.6, #각 트리를 학습할 때 사용하는 샘플링 비율
#                             silent=0, #학습 중 로그 출력 
#                             objective='reg:squarederror', #최적화할 목표 함수(손실 함수), reg:linear -> MSE 기반 회귀
#                             num_round=100) #트리의 개수