from dataclasses import asdict, dataclass
from typing import Dict, Any, List

from bs4 import BeautifulSoup

from crawl.core.domain.entity.YahooFinance import NewsContent
from utils.ZenrowsUtil import ZenrowsUtil


class YahooFinanceUseCase:
    def __init__(self, util: ZenrowsUtil):
        self.zenrows = util
        self.base_url = "https://finance.yahoo.com/topic/crypto/"
        self.urls = {
            "tech": "https://finance.yahoo.com/topic/tech/",
            "economy": "https://finance.yahoo.com/topic/economic-news/",
            "crypto": "https://finance.yahoo.com/topic/crypto/",
            "housing": "https://finance.yahoo.com/topic/housing-market/"
        }

    async def fetch_news(self, category: str = "crypto") -> Dict[str, Any]:
        """Fetch news from Yahoo Finance for a specific category."""
        url = self.urls.get(category, self.urls["crypto"])
        soup = await self.zenrows.fetch_page(url, 5000, None)
        news_items = await self._parse_news(soup)
        return self.convert_news_to_dict(news_items)

    async def _parse_news(self, soup: BeautifulSoup) -> List[NewsContent]:
        """Parse news items from the page."""
        news_items = []
        content_list = soup.select('.stream-items')
        if not content_list:
            return news_items

        main_content = content_list[0]
        links = main_content.find_all('a', class_='subtle-link')

        for i in range(min(3, len(links))):
            try:
                link = links[i]
                article_url = link['href']
                article_soup = await self.zenrows.fetch_page(article_url, 5000, None)

                article_content = article_soup.select(".body-wrap")
                if article_content:
                    content = self._clean_text(article_content[0].find('div', class_='body'))
                    news_items.append(NewsContent(content=content))

            except Exception as e:
                print(f"Failed to parse Yahoo Finance news item: {e}")
                continue

        return news_items

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean HTML text content."""
        if not isinstance(text, str):
            text = str(text)
        return ' '.join(text.split())

    @staticmethod
    def convert_news_to_dict(news_items: List[NewsContent]) -> Dict[str, Any]:
        """Convert news items to dictionary format."""
        return {
            "data": {
                "articles": [asdict(item) for item in news_items]
            }
        }
