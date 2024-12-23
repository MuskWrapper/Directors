from typing import Optional, List

from bs4 import BeautifulSoup
from dataclasses import asdict, dataclass
from datetime import datetime

from utils.ZenrowsUtil import ZenrowsUtil


@dataclass
class LatestNewsItem:
    title: str
    content: Optional[str]
    url: str
    category: str
    published_time: str
    image_url: Optional[str]


class CoinDeskLatestNewsUseCase:
    def __init__(self, util: ZenrowsUtil):
        self.zenrows = util
        self.base_url = "https://www.coindesk.com"
        self.latest_news_url = "https://www.coindesk.com/latest-crypto-news"

    async def fetch_latest_news(self):
        """Fetch and parse the latest crypto news from CoinDesk."""
        soup = await self.zenrows.fetch_page(self.latest_news_url, 5000, None)
        latest_news = self.parse_latest_news(soup)
        return self.convert_latest_news_to_dict(latest_news)

    def parse_latest_news(self, soup: BeautifulSoup) -> List[LatestNewsItem]:
        """Parse the latest news section using the specific selector."""
        news_items = []

        # Find the latest news container using the provided selector
        latest_news_container = soup.select_one(
            'div.flex.flex-wrap.justify-center.flex-col.border-0.md\\:gap-6.mdmax\\:gap-4.container-mobile-md.container-tablet-medium.container-desktop-lg.md\\:mt-8.mdmax\\:mt-6.mdmax\\:mx-0')

        if not latest_news_container:
            return news_items

        # Find all news article divs
        for article in latest_news_container.find_all('div', class_='flex gap-4'):
            try:
                # Get article details div
                article_content = article.find('div', class_='flex flex-col')
                if not article_content:
                    continue

                # Get category
                category_link = article_content.find('a', class_='text-charcoal-600')
                category = category_link.get_text(strip=True) if category_link else "Uncategorized"

                # Get title and URL
                title_link = article_content.find('a', class_='text-color-charcoal-900')
                if not title_link:
                    continue

                title = title_link.find('h3').get_text(strip=True)
                url = title_link['href']
                if not url.startswith('http'):
                    url = self.base_url + url

                # Get content preview
                content = None
                content_p = article_content.find('p', class_='line-clamp-3')
                if content_p:
                    content = content_p.get_text(strip=True)

                # Get published time
                time_span = article_content.find('span', class_='uppercase')
                published_time = self.parse_time(time_span.get_text(strip=True)) if time_span else None

                # Get image URL
                image_url = None
                img_tag = article.find('img')
                if img_tag and 'src' in img_tag.attrs:
                    image_url = img_tag['src']

                news_items.append(LatestNewsItem(
                    title=title,
                    content=content,
                    url=url,
                    category=category,
                    published_time=published_time,
                    image_url=image_url
                ))

            except Exception as e:
                print(f"Failed to parse latest news item: {e}")
                continue

        return news_items

    @staticmethod
    def parse_time(time_str: str) -> str:
        """Convert relative time to ISO format timestamp."""
        try:
            if 'AGO' in time_str:
                # Handle relative time (e.g., "2 HRS AGO")
                hours = int(time_str.split()[0])
                current_time = datetime.now()
                article_time = current_time.replace(hour=current_time.hour - hours)
                return article_time.isoformat()
            else:
                # Handle absolute date (e.g., "Dec 20, 2024")
                dt = datetime.strptime(time_str, '%b %d, %Y')
                return dt.isoformat()
        except Exception as e:
            print(f"Failed to parse time: {e}")
            return time_str

    @staticmethod
    def convert_latest_news_to_dict(news_items: List[LatestNewsItem]) -> dict:
        """Convert latest news items to a dictionary format."""
        return {
            "data": {
                "latest_news": [asdict(item) for item in news_items]
            }
        }
