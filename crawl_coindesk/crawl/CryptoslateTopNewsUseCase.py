from bs4 import BeautifulSoup
from dataclasses import asdict, dataclass
from typing import List, Optional

from crawl_coindesk.ZenrowsUtil import ZenrowsUtil


@dataclass
class TopNewsItem:
    title: str
    url: str
    image_url: str
    category: str
    author: str
    published_time: str
    type: Optional[str] = None

class CryptoSlateUseCase:
    def __init__(self, util: ZenrowsUtil):
        self.zenrows = util
        self.top_news_url = "https://cryptoslate.com/top-news/"

    async def fetch_top_news(self):
        """Fetch and parse top news from CryptoSlate."""
        soup = await self.zenrows.fetch_page(self.top_news_url, 5000, None)
        news_items = self.parse_top_news(soup)
        return self.convert_news_to_dict(news_items)

    @staticmethod
    def parse_top_news(soup: BeautifulSoup) -> List[TopNewsItem]:
        """Parse the top news section using the provided selector."""
        news_items = []

        # Find the top news container
        news_container = soup.select_one('#\\32 4Hours > div.posts')
        if not news_container:
            return news_items

        # Find all news articles
        for article in news_container.find_all('article'):
            try:
                # Get article link element
                link = article.find('a')
                if not link:
                    continue

                # Get title and URL
                title_elem = article.find('h2')
                title = title_elem.get_text(strip=True) if title_elem else ""
                url = link.get('href', '')

                # Get image URL
                img = article.find('img')
                image_url = img.get('src', '') if img else ''

                # Get post metadata
                post_meta = article.find('div', class_='post-meta')
                if not post_meta:
                    continue

                # Get category and type
                category_span = post_meta.find('span', {'class': None})
                type_span = post_meta.find('span', class_='type')

                category = category_span.get_text(strip=True) if category_span else "Uncategorized"
                article_type = type_span.get_text(strip=True) if type_span else None

                # Get author
                author_span = post_meta.find_all('span')
                author = author_span[1].get_text(strip=True) if len(author_span) > 1 else "Unknown"

                # Get published time
                time_span = post_meta.find('span', class_='read')
                published_time = time_span.get_text(strip=True) if time_span else None

                news_items.append(TopNewsItem(
                    title=title,
                    url=url,
                    image_url=image_url,
                    category=category,
                    type=article_type,
                    author=author,
                    published_time=published_time
                ))

            except Exception as e:
                print(f"Failed to parse news item: {e}")
                continue

        return news_items

    @staticmethod
    def convert_news_to_dict(news_items: List[TopNewsItem]) -> dict:
        """Convert news items to a dictionary format."""
        return {
            "data": {
                "top_news": [asdict(item) for item in news_items]
            }
        }