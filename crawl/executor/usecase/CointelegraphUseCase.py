from dataclasses import dataclass, asdict
from typing import List, Dict, Any

from bs4 import BeautifulSoup

from utils.ZenrowsUtil import ZenrowsUtil


@dataclass
class NewsContent:
    content: str


class CointelegraphUseCase:
    def __init__(self, util: ZenrowsUtil):
        self.zenrows = util
        self.base_url = "https://cointelegraph.com"
        self.urls = {
            "market": "https://cointelegraph.com/tags/markets",
            "policy": "https://cointelegraph.com/tags/regulation",
            "tech": "https://cointelegraph.com/tags/technology",
            "nft": "https://cointelegraph.com/tags/nft",
            "business": "https://cointelegraph.com/tags/business",
            "research": "https://cointelegraph.com/tags/research-reports"
        }

    async def fetch_news(self, category: str = "market") -> Dict[str, Any]:
        """Fetch news from Cointelegraph for a specific category."""
        url = self.urls.get(category, self.urls["market"])
        soup = await self.zenrows.fetch_page(url, 5000, None)
        news_items = await self._parse_news(soup)
        return self.convert_news_to_dict(news_items)

    async def _parse_news(self, soup: BeautifulSoup) -> List[NewsContent]:
        """Parse news items from the page."""
        news_items = []
        content_list = soup.select(".post-card-inline")

        for i in range(min(3, len(content_list))):
            try:
                article = content_list[i]
                link = article.find('a', class_='post-card-inline__figure-link')
                if not link:
                    continue

                article_url = self.base_url + link['href']
                article_soup = await self.zenrows.fetch_page(article_url, 5000, None)

                article_content = article_soup.select(".post__content-wrapper")
                if article_content:
                    content = self._clean_text(article_content[0].find('div', class_='post-content'))
                    news_items.append(NewsContent(content=content))

            except Exception as e:
                print(f"Failed to parse Cointelegraph news item: {e}")
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
