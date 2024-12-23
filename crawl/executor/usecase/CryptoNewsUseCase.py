from bs4 import BeautifulSoup
from dataclasses import asdict, dataclass
from typing import List, Optional

from utils.ZenrowsUtil import ZenrowsUtil

@dataclass
class CryptoNewsItem:
    title: str
    url: str
    category: Optional[str]
    description: str
    published_time: str
    author: Optional[str]
    image_url: Optional[str]
    is_featured: bool  # True for main news, False for mini news

class CryptoNewsUseCase:
    def __init__(self, util: ZenrowsUtil):
        self.zenrows = util
        self.news_url = "https://cryptonews.com/news/"

    async def fetch_news(self):
        """Fetch and parse news from CryptoNews."""
        soup = await self.zenrows.fetch_page(self.news_url, 5000, None)
        news_items = self.parse_news(soup)
        return self.convert_news_to_dict(news_items)

    def parse_news(self, soup: BeautifulSoup) -> List[CryptoNewsItem]:
        """Parse the news section using the provided selector."""
        news_items = []

        # Find the main news container
        main_container = soup.select_one('body > div.main > div.container.archive-template > div:nth-child(2) > main')
        if not main_container:
            return news_items

        # Parse featured (large) news items
        featured_news = main_container.find('div', class_='archive-template-latest-news-list')
        if featured_news:
            for article in featured_news.find_all('div', class_='archive-template-latest-news__wrap'):
                try:
                    news_item = self._parse_news_item(article, is_featured=True)
                    if news_item:
                        news_items.append(news_item)
                except Exception as e:
                    print(f"Failed to parse featured news item: {e}")

        # Parse mini news items
        mini_news = main_container.find('div', class_='archive-template-latest-news-list-mini')
        if mini_news:
            for article in mini_news.find_all('div', class_='archive-template-latest-news__wrap'):
                try:
                    news_item = self._parse_news_item(article, is_featured=False)
                    if news_item:
                        news_items.append(news_item)
                except Exception as e:
                    print(f"Failed to parse mini news item: {e}")

        return news_items

    def _parse_news_item(self, article_div, is_featured: bool) -> Optional[CryptoNewsItem]:
        """Parse individual news item."""
        try:
            # Get the article link
            article = article_div.find('a', class_='archive-template-latest-news')
            if not article:
                return None

            # Get title
            title_elem = article.find('h5') if is_featured else article.find('div',
                                                                             class_='archive-template-latest-news__title')
            title = title_elem.get_text(strip=True) if title_elem else ""

            # Get URL
            url = article.get('href', '')

            # Get category
            category_div = article.find('div', class_='archive-template-latest-news__label')
            category = category_div.get_text(strip=True) if category_div else None

            # Get description
            desc_div = article.find('div', class_='archive-template-latest-news__description')
            description = desc_div.get_text(strip=True) if desc_div else ""

            # Get publication time
            time_div = article.find('div', class_='archive-template-latest-news__time')
            published_time = time_div.get_text(strip=True) if time_div else ""

            # Get author
            author_div = article.find('div', class_='archive-template-latest-news__author')
            author = author_div.get_text(strip=True).replace(',', '').replace('by', '').strip() if author_div else None

            # Get image URL (only for featured news)
            image_url = None
            if is_featured:
                bg_div = article.find('div', class_='archive-template-latest-news__bg')
                if bg_div:
                    style = bg_div.get('style', '')
                    if 'background-image: url(' in style:
                        image_url = style.split('url(')[1].split(')')[0]

            return CryptoNewsItem(
                title=title,
                url=url,
                category=category,
                description=description,
                published_time=published_time,
                author=author,
                image_url=image_url,
                is_featured=is_featured
            )

        except Exception as e:
            print(f"Failed to parse news item details: {e}")
            return None

    @staticmethod
    def convert_news_to_dict(news_items: List[CryptoNewsItem]) -> dict:
        """Convert news items to a dictionary format."""
        return {
            "data": {
                "news": [asdict(item) for item in news_items]
            }
        }