from bs4 import BeautifulSoup
from dataclasses import asdict, dataclass
from typing import List, Optional

from crawl.core.domain.entity.CryptoSalte import InsightNewsItem, Category
from utils.ZenrowsUtil import ZenrowsUtil


class CryptoSlateInsightsUseCase:
    def __init__(self, util: ZenrowsUtil):
        self.zenrows = util
        self.insights_url = "https://cryptoslate.com/insights/"

    async def fetch_insights(self):
        """Fetch and parse insights news from CryptoSlate."""
        soup = await self.zenrows.fetch_page(self.insights_url, 5000, None)
        news_items = self.parse_insights(soup)
        return self.convert_insights_to_dict(news_items)

    def parse_insights(self, soup: BeautifulSoup) -> List[InsightNewsItem]:
        """Parse the insights news section using the provided selector."""
        news_items = []

        # Find the insights news container
        insights_container = soup.select_one(
            '#main > div.container.clearfix > div.news-feed.slate > div.list-feed.insights.icon-feed')
        if not insights_container:
            return news_items

        # Find all news articles
        for article in insights_container.find_all('article'):
            try:
                # Get article link element
                link = article.find('a')
                if not link:
                    continue

                # Get title
                title_elem = article.find('h2')
                title = title_elem.get_text(strip=True) if title_elem else ""

                # Get URL
                url = link.get('href', '')

                # Get image URL
                img = article.find('img', class_='attachment-medium')
                image_url = img.get('src', '') if img else ''

                # Get categories
                categories_div = article.find('div', class_='inner')
                categories = []
                if categories_div:
                    for cat_span in categories_div.find_all('span'):
                        cat_name = cat_span.get_text(strip=True)
                        if cat_name:
                            categories.append(Category(name=cat_name))

                # Get published time
                time_span = article.find('span', class_='read')
                published_time = time_span.get_text(strip=True) if time_span else ""

                # Get data source if available (e.g., "Data via Farside Investors")
                data_source = None
                insights_span = article.find('span', class_='insights')
                if insights_span:
                    data_source_text = insights_span.get_text(strip=True)
                    if "Data via" in data_source_text:
                        data_source = data_source_text.replace("Data via", "").strip()

                news_items.append(InsightNewsItem(
                    title=title,
                    url=url,
                    image_url=image_url,
                    categories=categories,
                    published_time=published_time,
                    data_source=data_source
                ))

            except Exception as e:
                print(f"Failed to parse insight news item: {e}")
                continue

        return news_items

    @staticmethod
    def convert_insights_to_dict(news_items: List[InsightNewsItem]) -> dict:
        """Convert insights news items to a dictionary format."""
        return {
            "data": {
                "insights": [asdict(item) for item in news_items]
            }
        }
