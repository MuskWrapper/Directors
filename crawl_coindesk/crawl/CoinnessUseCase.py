# coinness_crawler.py
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
import re

from crawl_coindesk.ZenrowsUtil import ZenrowsUtil


@dataclass
class NewsItem:
    time: str
    title: str
    content: str
    bull_count: int
    bear_count: int
    quote_count: int
    coin_tags: List[str]
    date: str
    isHighlight: bool


class CrawlCoinnessUseCase:
    def __init__(self, util=ZenrowsUtil()):
        self.zenrows = util

    async def fetch_coinness_news(self):
        js_instructions = '''
          [
              {"click": "#root > div > div.Wrap-sc-v065lx-0.hwmGSB > div > main > button"},
              {"wait": 500}
          ]
          '''
        url = "https://coinness.com/"
        soup = await self.zenrows.fetch_page(url, 5000, js_instructions)
        current_date = self.extract_date(soup)
        news_items = self.parse_news(soup, current_date)
        result = self.convert_news_to_dict(news_items)
        return result

    @staticmethod
    def extract_date(soup: BeautifulSoup) -> str:
        """페이지에서 날짜 정보를 추출합니다."""
        date_text = soup.select_one('#root > div > div.Wrap-sc-v065lx-0.hwmGSB > div > main > div.Wrap-sc-n14h4a-0.izBKQg > div > div.Wrap-sc-907me6-0.cjdwpI > div').text
        match = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', date_text)

        if match:
            year, month, day = match.groups()
            return f"{year}-{month:0>2}-{day:0>2}"
        return "날짜 정보 없음"

    @staticmethod
    def convert_time_format(time_str: str) -> str:
        """
        12시간제 시간을 24시간제로 변환합니다.
        예: "08:05" -> "20:05"
        """
        try:
            hours, minutes = map(int, time_str.split(":"))
            if hours < 8:
                hours += 12
            return f"{hours:02d}:{minutes:02d}"
        except Exception as e:
            print(f"Failed to convert time: {e}")
            return time_str

    @classmethod
    def parse_news(cls, soup: BeautifulSoup, current_date: str) -> list[NewsItem]:
        """뉴스 정보를 파싱하여 리스트로 반환합니다."""
        news_items = []

        for news_div in soup.select('div.BreakingNewsWrap-sc-glfxh-1'):
            try:
                time = news_div.select_one('div.TimeBlock-sc-glfxh-2').text
                time = cls.convert_time_format(time)  # 시간 포맷 변환

                title_div = news_div.select_one('div.BreakingNewsTitle-sc-glfxh-4')
                if title_div and title_div.get('class'):
                    isHighlight = 'dFiHgV' in title_div.get('class', [])
                else:
                    isHighlight = False

                title = news_div.select_one('div.BreakingNewsTitle-sc-glfxh-4 a').text
                content = news_div.select_one('div.BreakingNewsContents-sc-glfxh-5 span').text.strip()
                like_count = int(news_div.select_one('span[type="bull"]').text)
                dislike_count = int(news_div.select_one('span[type="bear"]').text)
                quote_count = int(news_div.select_one('span.QuoteCount-sc-w7d7vw-0').text)

                coin_tag_element = news_div.select_one('div.CoinWrap-sc-1ghqi0-0')
                coin_tags = []
                if coin_tag_element:
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

    @staticmethod
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
