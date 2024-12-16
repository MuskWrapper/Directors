from zenrows import ZenRowsClient
from bs4 import BeautifulSoup
import configparser
import re

config = configparser.ConfigParser()
config.read('../config.ini')

apikey = config['system']['key']
client = ZenRowsClient(apikey)


def main():
    # 사이트 도메인 url
    main_url = "https://cointelegraph.com"

    # 각 뉴스 카테고리별 url
    market_news_url = "https://cointelegraph.com/tags/markets"
    policy_news_url = "https://cointelegraph.com/tags/regulation"
    tech_news_url = "https://cointelegraph.com/tags/technology"
    nft_news_url = "https://cointelegraph.com/tags/nft"
    business_news_url = "https://cointelegraph.com/tags/business"

    # 보고서 url
    research_report_url = "https://cointelegraph.com/tags/research-reports"

    # html 코드 가져오기
    response = client.get(research_report_url)

    soup = BeautifulSoup(response.text, 'html.parser')

    # 기사 리스트 가져오기
    content = soup.select(".post-card-inline")

    json_list = []
    # 기사 3개의 링크만 뽑아
    # 각 기사 링크 본문 기사를 크롤링해와 json 형태로 저장
    for i in range(3):
        rst_url = main_url + content[i].find('a', class_='post-card-inline__figure-link')['href']

        # 각 뉴스 url 크롤링
        news_res = client.get(rst_url)
        news_soup = BeautifulSoup(news_res.text, 'html.parser')

        # 뉴스 본문 기사 파싱
        news_rst = news_soup.select(".post__content-wrapper")

        # 태그 포함되어 있는 뉴스 데이터들 정리하기
        cleaned_text = remove_html_tags(news_rst[0].find('div', class_='post-content'))

        # json 형태로 데이터 저장
        json_list.append({"content": cleaned_text})

    print(json_list)

def remove_html_tags(text):
    # 입력이 문자열이 아닐 경우 문자열로 변환
    if not isinstance(text, str):
        text = str(text)

    # HTML 태그 제거
    clean_text = re.sub(r'<[^>]+>|<\/[^>]+>', '', text, flags=re.MULTILINE)

    # 연속된 빈 줄 제거
    clean_text = re.sub(r'\n\s*\n', '\n', clean_text)

    # 앞뒤 공백 제거
    clean_text = clean_text.strip()

    return clean_text

if __name__ == '__main__':
    main()

