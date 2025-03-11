from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import boto3
import json
import yfinance as yf
from yahooquery import search
from deep_translator import GoogleTranslator
from func.stock_price import get_currency, get_stock_price, get_stock_symbol, find_company_symbol

### bedrock setting ###
inferenceProfileArn= os.getenv("BEDROCK_INFERENCE_PROFILE_ARN")
app = Flask(__name__)
bedrock_client = boto3.client("bedrock-runtime", region_name="ap-northeast-2")
### --------------- ###

### 주가 그래프 출력 ###
import mplfinance as mpf
from pandas_datareader import data as pdr

def stock_price_graph(compnay_symbol, str, end):
    symbol = yf.Ticer(compnay_symbol)
    stock_data = symbol.history(f"start={str}, end={end}")

    mc = mpf.make_marketcolors(up="r", down="b")
    s = mpf.make_mpf_style(base_mpf_stype="starsandstripes", maketcolors=mc)
    return mpf.plot(stock_data, type='candle', style=s, volume=True, mav=(5, 10 ,60))
### --------------- ###

### 주식 가격 출력 response ###
def chatbot_response(user_input):
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

### 일반 평문 대답 ###
def chatbot_response2(user_input):
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
    if any(keyword in user_input for keyword in stock_price_keywords):
        response = chatbot_response(user_input)
    else:
        response = chatbot_response2(user_input)

    return jsonify({"response": response})
#### ---------------- ####

### chatbot page ###
@app.route("/")
def index():
    return render_template("index.html") 
### ----------- ###

### register page ###
from Models import Webuser
from Models import db
from flask_sqlalchemy import SQLAlchemy
@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        userid = request.form.get('userid')
        username = request.form.get('username')
        password = request.form.get('password')
        re_password = request.form.get('re_password')
        print(password)
        
        if not (userid and username and password and re_password) :
            return "모두 입력해주세요"
        elif password != re_password:
            return "비밀번호를 확인해주세요"
        else:
            webuser = Webuser()
            webuser.password = password
            webuser.userid = userid
            webuser.username = username
            db.session.add(webuser)
            db.session.commit()
            return redirect(url_for('index'))
### --------------- ###

if __name__ == "__main__":
    ### db table 생성 ###
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///db.sqlite' # 절대 경로로 지정
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all() 
    ### ------------- ###

    app.run(host="0.0.0.0", port=5000, debug=True)
