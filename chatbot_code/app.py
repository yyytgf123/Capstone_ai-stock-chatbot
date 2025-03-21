from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
from dotenv import load_dotenv
import boto3
import json
from func.stock_price import get_currency, get_stock_price, get_stock_symbol, find_company_symbol

### bedrock setting ###
load_dotenv()
inferenceProfileArn= os.getenv("BEDROCK_INFERENCE_PROFILE_ARN")
app = Flask(__name__)
bedrock_client = boto3.client("bedrock-runtime", region_name="ap-northeast-2")
### --------------- ###

### 일반 평문 대답 ###
def chatbot_response(user_input):
    prompt = (
        f"너는 AI 비서야. 질문에 대해 친절하고 유익한 답변을 해줘."
        f"일반적인 질문이면 적절한 답변을 해줘."
        f"무조건 200자 이내에 답변을 해줘"
        f"질문: {user_input}"
    )

    response = bedrock_client.invoke_model(
        modelId=inferenceProfileArn,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "top_k": 250,
            "stop_sequences": [],
            "temperature": 1,
            "top_p": 0.999,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ]
        }),
    )

    ai_response = json.loads(response["body"].read())["content"][0]["text"]

    return ai_response.strip()
### --------------- ###

### 주식 가격 출력 response ###
def chatbot_response2(user_input):
    company_name = find_company_symbol(user_input)
    symbol = get_stock_symbol(company_name)
    stock_info = ""

    if symbol:
        stock_price = get_stock_price(symbol)
        currency = get_currency(symbol)
        stock_info = f"{company_name}의 주가는 {stock_price}{currency}입니다. "

    prompt = (
        f"너는 AI 비서야. 질문에 대해 친절하고 유익한 답변을 해줘."
        f"주식 정보가 포함된 경우 가격을 포함해서 답변해줘."
        f"무조건 200자 이내에 답변을 해줘"
        f"질문: {user_input}\n"
        f"답변:"
    )

    response = bedrock_client.invoke_model(
        modelId=inferenceProfileArn,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "top_k": 250,
            "stop_sequences": [],
            "temperature": 1,
            "top_p": 0.999,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ]
        }),
    )

    ai_response = json.loads(response["body"].read())["content"][0]["text"]

    return stock_info if stock_info else ai_response.strip()
### --------------------- ###

### 경제 뉴스 출력 ###
from func.news import get_urls, extract_Data

def chatbot_response3(user_input):
    url = 'https://sedaily.com/NewsList/GA01'
    soup = get_urls(url)

    news_list = soup.select('.sub_news_list li')
    news_dict = {}

    for news in news_list:
        title = news.select_one('.text_area').get_text().strip()
        summary = news.select_one('.text_sub').get_text().strip()
        news_dict[title] = summary

    prompt = (
        f"너는 AI 비서야. 질문에 대해 친절하고 유익한 답변을 해줘."
        f"무조건 500자 이내에 답변을 해줘"
        f"질문 : {user_input}"
        f"대답 참고 : 뉴스 날짜 + {news_dict}"
        # html 사이즈 파악 후 한 줄에 입력될 글자 수 지정 필요
    )

    response = bedrock_client.invoke_model(
        modelId=inferenceProfileArn,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "top_k": 250,
            "stop_sequences": [],
            "temperature": 1,
            "top_p": 0.999,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ]
        }),
    )

    ai_response = json.loads(response["body"].read())["content"][0]["text"]

    return ai_response.strip()
### --------------- ###

### 주가 예측 ###
def chatbot_response4(user_input):
    # 프롬프트 구성 (주가 예측을 보장하지 않도록 수정)
    prompt = (
        f"너는 AI 비서야. 질문에 대해 친절하고 유익한 답변을 해줘.\n"
        f"무조건 500자 이내에 답변을 해줘.\n"
        f"질문 : {user_input}\n"
        f"아래는 2025년 1월 1일부터의 주가 데이터야. 이 데이터를 기반으로 향후 주가에 대한 전망을 분석해줘.\n"
        f"단, 주가는 다양한 외부 요인에 의해 변동될 수 있으며, AI의 분석이 100% 정확하지 않을 수도 있어."
    )

    # Bedrock 모델 호출
    response = bedrock_client.invoke_model(
        modelId=inferenceProfileArn,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "top_k": 250,
            "stop_sequences": [],
            "temperature": 1,
            "top_p": 0.999,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ]
        }),
    )

    ai_response = json.loads(response["body"].read())["content"][0]["text"]

    return ai_response
### --------------- ###

#### Flask 엔드포인트 ####
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "메시지가 없습니다."}), 400

    user_input = data["message"].strip() 

    if not user_input:
        return jsonify({"error": "빈 메시지입니다."}), 400
    
    """
    주가 질문 시 -> chatbot_response
    주가 그래프 출력 -> chatbot_response3
    일반 평문 질문 시 -> chatbot_response2
    """
    stock_price_keywords = ["주가", "가격", "주식가격", "주식 가격"]
    news_keywords = ["경제뉴스", "경제 뉴스", "최신 경제"]
    sp_predict_keywords = ["주가예측"]
    if any(keyword in user_input for keyword in stock_price_keywords):
        response = chatbot_response2(user_input)
    elif any(keyword in user_input for keyword in news_keywords):
        response = chatbot_response3(user_input)
    elif any(keyword in user_input for keyword in sp_predict_keywords):
        response = chatbot_response4(user_input)
    else:
        response = chatbot_response(user_input)
    return jsonify({"response": response})
#### ---------------- ####

### chatbot ###
@app.route("/")
def index():
    return render_template("index.html") 
### ----------- ###

### 한줄 뉴스 ###
from func.web.news import get_economic_news

@app.route("/get_news", methods=["GET"])
def get_news():
    news = get_economic_news()
    return jsonify(news)
### ----------- ###

### 주요 자산 page ###
from func.web.asset_price import get_asset_prices

@app.route("/get_asset_prices", methods=["GET"])
def asset_prices():
    prices = get_asset_prices()
    return jsonify(prices)
### ----------- ###

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
