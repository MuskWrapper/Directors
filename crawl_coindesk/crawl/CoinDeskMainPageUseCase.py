from bs4 import BeautifulSoup
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime

from crawl_coindesk.ZenrowsUtil import ZenrowsUtil


@dataclass
class NewsStory:
    title: str
    content: Optional[str]
    url: str
    published_time: str
    category: Optional[str]
    image_url: Optional[str]
    is_sponsored: bool

@dataclass
class Author:
    name: str
    url: str

@dataclass
class MostReadStory:
    rank: int
    title: str
    url: str
    content: Optional[str]
    authors: List[Author]
    published_time: str
    image_url: Optional[str]

class CoinDeskMainPageUseCase:
    def __init__(self, util: ZenrowsUtil):
        self.zenrows = util
        self.base_url = "https://www.coindesk.com"

    async def fetch_top_stories(self):
        """Fetch and parse top stories from CoinDesk's main page."""
        url = self.base_url
        soup = await self.zenrows.fetch_page(url, 5000, None)
        news_items = self.parse_top_stories(soup)
        return self.convert_news_to_dict(news_items)

    def parse_top_stories(self, soup: BeautifulSoup) -> List[NewsStory]:
        """Parse the top stories section using the provided selector."""
        news_items = []
        stories_container = soup.select_one(
            'div.grid.gap-4.grid-cols-4.md\\:grid-cols-8.lg\\:grid-cols-12.xl\\:grid-cols-16 > div.order-2.col-span-4.md\\:order-3.md\\:col-span-5.lg\\:col-span-9.xl\\:order-3.xl\\:col-span-12.xl\\:row-span-6 > div.flex.flex-col')

        if not stories_container:
            return news_items

        for article in stories_container.find_all('div', class_='flex'):
            try:
                # Find article link and title
                title_link = article.find('a', class_='hover:underline')
                if not title_link:
                    continue

                title = title_link.find('h3').get_text(strip=True)
                url = title_link['href']
                if not url.startswith('http'):
                    url = self.base_url + url

                # Extract content preview if available
                content = None
                content_p = article.find('p', class_='line-clamp-3')
                if content_p:
                    content = content_p.get_text(strip=True)

                # Check if article is sponsored
                is_sponsored = bool(article.find('span', string='SPONSORED'))

                # Extract publication time
                time_span = article.find('span', class_='uppercase')
                published_time = self.parse_time(time_span.get_text(strip=True)) if time_span else None

                # Get category
                category = None
                category_span = article.find('span', class_='category')
                if category_span:
                    category = category_span.get_text(strip=True)

                # Get image URL
                image_url = None
                img_tag = article.find('img')
                if img_tag and 'src' in img_tag.attrs:
                    image_url = img_tag['src']

                news_items.append(NewsStory(
                    title=title,
                    content=content,
                    url=url,
                    published_time=published_time,
                    category=category,
                    image_url=image_url,
                    is_sponsored=is_sponsored
                ))

            except Exception as e:
                print(f"Failed to parse news item: {e}")
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

    async def fetch_most_read(self):
        """Fetch and parse most read stories from CoinDesk's main page."""
        url = self.base_url
        soup = await self.zenrows.fetch_page(url, 5000, None)
        news_items = self.parse_most_read(soup)
        return self.convert_most_read_to_dict(news_items)

    def parse_most_read(self, soup: BeautifulSoup) -> List[MostReadStory]:
        """Parse the most read section using the provided selector."""
        news_items = []
        most_read_container = soup.select_one('div.order-3 > div')

        if not most_read_container:
            return news_items

        # Find all news article divs in the most read section
        for article in most_read_container.find_all('div', class_='flex flex-col gap-1 md:flex-row'):
            try:
                # Get rank number
                rank_span = article.find('span', class_='text-color-charcoal-900 uppercase')
                if not rank_span:
                    continue
                rank = int(rank_span.text.strip('0.').strip())

                # Get article details
                article_content = article.find('div', class_='bg-white flex gap-6')
                if not article_content:
                    continue

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

                # Get authors
                authors = []
                author_links = article_content.find_all('a', class_='text-color-charcoal-900 hover:underline')
                for author_link in author_links:
                    if author_link.get('title'):  # Only process links with title attribute (author links)
                        authors.append(Author(
                            name=author_link.get('title'),
                            url=self.base_url + author_link['href'] if not author_link['href'].startswith('http') else
                            author_link['href']
                        ))

                # Get published time
                time_span = article_content.find('span', class_='uppercase',
                                                 string=lambda text: text and ('AGO' in text or '202' in text))
                published_time = self.parse_time(time_span.get_text(strip=True)) if time_span else None

                # Get image URL
                image_url = None
                img_tag = article.find('img', class_='rounded')
                if img_tag and 'src' in img_tag.attrs:
                    image_url = img_tag['src']

                news_items.append(MostReadStory(
                    rank=rank,
                    title=title,
                    url=url,
                    content=content,
                    authors=authors,
                    published_time=published_time,
                    image_url=image_url
                ))

            except Exception as e:
                print(f"Failed to parse most read item: {e}")
                continue

        # Sort by rank to ensure correct order
        news_items.sort(key=lambda x: x.rank)
        return news_items

    @staticmethod
    def convert_most_read_to_dict(news_items: List[MostReadStory]) -> dict:
        """Convert most read items to a dictionary format."""
        return {
            "data": {
                "most_read": [asdict(item) for item in news_items]
            }
        }

    @staticmethod
    def convert_news_to_dict(news_items: List[NewsStory]) -> dict:
        """Convert news items to a dictionary format."""
        return {
            "data": {
                "top_stories": [asdict(item) for item in news_items]
            }
        }