from deep_translator import GoogleTranslator
import FinanceDataReader as fdr
import pandas as pd

def translate_to_english(text):
    return GoogleTranslator(source='ko', target='en').translate(text)

def find_company_symbol(user_input):
    # 사용자 입력을 단어별 리스트로 변환
    user_input_list = user_input.split()

    translated_words = []
    for word in user_input_list:
        if not word.isascii():  # 한글인 경우 번역
            translated_word = translate_to_english(word)
            translated_words.append(translated_word)
        else:
            translated_words.append(word)

    # 번역된 단어 리스트 출력 (디버깅용)
    print(f"Translated Words: {translated_words}")

    # KRX + NYSE + NASDAQ 데이터 로드
    stocks_krx = fdr.StockListing('KRX')  # 한국 거래소
    stocks_nyse = fdr.StockListing('NYSE')  # 뉴욕 거래소
    stocks_nasdaq = fdr.StockListing('NASDAQ')  # 나스닥

    # 모든 거래소 데이터를 하나로 합침
    stocks = pd.concat([stocks_krx, stocks_nyse, stocks_nasdaq], ignore_index=True)

    # 종목 심볼을 찾기 위한 리스트
    symbol_storage = []

    # 번역된 단어가 회사명과 "부분적으로라도" 일치하는 경우 찾기
    for translated_word in translated_words:
        match = stocks[stocks["Name"].str.contains(translated_word, case=False, na=False)]

        # 여러 개의 검색 결과가 나오면, 가장 관련 있는 항목을 먼저 선택
        if not match.empty:
            sorted_match = match.sort_values(by="MarketCap", ascending=False)  # 시가총액 기준 정렬 (가장 큰 기업 우선)
            best_match_symbol = sorted_match.iloc[0]["Symbol"]  # 첫 번째 결과만 사용
            symbol_storage.append(best_match_symbol)

    return symbol_storage if symbol_storage else "해당 회사의 주식 심볼을 찾을 수 없습니다."

# 테스트 실행
print(find_company_symbol("애플 주가 알려줘"))
