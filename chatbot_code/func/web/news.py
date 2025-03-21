import requests
from bs4 import BeautifulSoup

### 한줄 경제 뉴스（네이버뉴스 가져옴 일단 실시간 속보가 아닌 주요뉴스로）###
def get_economic_news():
    try:
        url = "https://finance.naver.com/news/mainnews.naver"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://finance.naver.com"
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        news_items = soup.select(".newsList li a")  # 뉴스 리스트 가져오기

        news_list = []
        for news in soup.select(".newsList li a")[:10]:  # 뉴스 10개 가져오기
            if news:
                title = news.get_text(strip=True)
                link = "https://finance.naver.com" + news["href"]
                news_list.append({"title": title, "link": link})

        if not news_list:
            print("뉴스 데이터를 찾을 수 없습니다. CSS Selector 확인 필요.")
            return []

        return news_list

    except Exception as e:
        print("경제 뉴스 가져오기 오류:", str(e))
        return []
### --------------------- ###
