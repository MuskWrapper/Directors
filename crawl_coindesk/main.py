from bs4 import BeautifulSoup
from zenrows import ZenRowsClient
import urllib.parse
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import json


@dataclass
class NewsItem:
    time: str
    title: str
    content: str
    bull_count: int
    bear_count: int
    quote_count: int
    coin_tags: List[str]
    date: str  # 날짜 필드 추가
    isHighlight: bool  # 중요 뉴스 여부 필드 추가


async def fetch_page(url: str, wait: int, js_instructions: Optional[str]) -> BeautifulSoup:
    """웹 페이지를 가져와서 파싱된 BeautifulSoup 객체를 반환합니다."""
    print("fetching")

    client = ZenRowsClient("")

    try:
        params = {
            'js_render': True,
            'wait': wait,
            'js_instructions': js_instructions
        }

        # 응답을 텍스트로 가져오기
        response = client.get(url, params=params)
        html_content = response.text

        # BeautifulSoup 객체 생성 및 반환
        return BeautifulSoup(html_content, 'lxml')

    except Exception as error:
        print(f"Failed to fetch page: {error}")
        print(f"Response type: {type(response)}")
        print(f"Response: {response}")
        raise error


def extract_date(soup: BeautifulSoup) -> str:
    """페이지에서 날짜 정보를 추출합니다."""
    date_text = soup.select_one('div.eZCcWE').text
    match = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', date_text)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month:0>2}-{day:0>2}"
    return "날짜 정보 없음"


def convert_time_format(time_str: str) -> str:
    """
    12시간제 시간을 24시간제로 변환합니다.
    예: "08:05" -> "20:05"
    """
    try:
        # 시간과 분을 분리
        hours, minutes = map(int, time_str.split(":"))

        # 현재 시간이 8시 이전이면 (+12)를 해서 오후 시간으로 변환
        if hours < 8:
            hours += 12

        return f"{hours:02d}:{minutes:02d}"
    except Exception as e:
        print(f"Failed to convert time: {e}")
        return time_str


def parse_news(soup: BeautifulSoup, current_date: str) -> list[NewsItem]:
    """뉴스 정보를 파싱하여 리스트로 반환합니다."""
    news_items = []

    for news_div in soup.select('div.BreakingNewsWrap-sc-glfxh-1'):
        try:
            time = news_div.select_one('div.TimeBlock-sc-glfxh-2').text
            time = convert_time_format(time)  # 시간 포맷 변환

            title_div = news_div.select_one('div.BreakingNewsTitle-sc-glfxh-4')
            if title_div and title_div.get('class'):
                isHighlight = 'dFiHgV' in title_div.get('class', [])
            else:
                isHighlight = False  # 클래스를 찾을 수 없는 경우 기본값

            title = news_div.select_one('div.BreakingNewsTitle-sc-glfxh-4 a').text
            content = news_div.select_one('div.BreakingNewsContents-sc-glfxh-5 span').text.strip()
            like_count = int(news_div.select_one('span[type="bull"]').text)
            dislike_count = int(news_div.select_one('span[type="bear"]').text)
            quote_count = int(news_div.select_one('span.QuoteCount-sc-w7d7vw-0').text)
            coin_tag_element = news_div.select_one('div.CoinWrap-sc-1ghqi0-0')
            coin_tags = []
            if coin_tag_element:
                # 모든 코인 버튼을 찾아서 텍스트 추출
                coin_buttons = coin_tag_element.select('button.MiniCoinBadge-sc-1ghqi0-1')
                coin_tags = [btn.text.strip() for btn in coin_buttons]

            news_items.append(NewsItem(
                time=time,
                title=title,
                content=content,
                bull_count=like_count,
                bear_count=dislike_count,
                quote_count=quote_count,
                coin_tags=coin_tags,
                date=current_date,
                isHighlight=isHighlight
            ))

        except Exception as e:
            print(f"Failed to parse news item: {e}")
            print(f"HTML content of news_div: {news_div}")
            continue

    return news_items


def convert_news_to_dict(news_items: List[NewsItem]) -> dict:
    """뉴스 아이템을 JSON 형식의 딕셔너리로 변환합니다."""
    result = {"data": []}

    grouped_news = {}
    for item in news_items:
        if item.date not in grouped_news:
            grouped_news[item.date] = []
        news_dict = asdict(item)
        grouped_news[item.date].append(news_dict)

    for date, items in grouped_news.items():
        result["data"].append({
            "date": date,
            "items": items
        })

    return result


async def main():
    js_instructions = '''
       [
           {"click": "#root > div > div.Wrap-sc-v065lx-0.hwmGSB > div > main > button"},
           {"wait": 500}
       ]
       '''
    # root > div > div.Wrap-sc-v065lx-0.hwmGSB > div > main > div.Wrap-sc-n14h4a-0.izBKQg > div:nth-child(2)
    url = "https://coinness.com/"
    soup = await fetch_page(url, 5000, js_instructions)
    current_date = extract_date(soup)
    news_items = parse_news(soup, current_date)

    # JSON 형식으로 변환
    result = convert_news_to_dict(news_items)

    # JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
