import requests, json
from bs4 import BeautifulSoup
from tqdm.notebook import tqdm
from flask import Flask
import boto3
import os

### bedrock setting ###
inferenceProfileArn= os.getenv("BEDROCK_INFERENCE_PROFILE_ARN")
app = Flask(__name__)
bedrock_client = boto3.client("bedrock-runtime", region_name="ap-northeast-2")

#######################
def link_tag():
    """
    url -> 네이버 뉴스 출력
    """
    type = 101
    page = 1

    main_selector = "#dic_area"

    url = f"https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1={type}"\
    f"#data=%2000:00:00&page={page}"
    html = requests.get(url, headers={"User-Agent" : "Mozilla/5.0" \
                                      "(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "\
                                      "Chrome/110.0.0.0 Safari/537.36"})

    soup = BeautifulSoup(html.text, "lxml")
    a_tag = soup.find_all("a")
    
    main = soup.select(main_selector)
    main_list = []
    for m in main:
        m_text = m.text
        m_text = m_text.strip()
        main_list.append(m_text)
    main_str = "".join(main_list)

    print(main_str)

    return main_str
#######################


### 일반 평문 대답 ###
def chatbot_response(user_input):
    news_url = link_tag()

    prompt = (
        f"너는 AI 비서야. 질문에 대해 친절하고 유익한 답변을 해줘."
        f"무조건 200자 이내에 답변을 해줘"
        f"{news_url}의 정보를 갖고 알맞게 대답해줘"        
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

chatbot_response("경제뉴스 출력해줘")