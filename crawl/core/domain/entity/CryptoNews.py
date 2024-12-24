from dataclasses import dataclass
from typing import Optional


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
