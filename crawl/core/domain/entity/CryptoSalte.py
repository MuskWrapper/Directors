from dataclasses import dataclass
from typing import Optional, List


@dataclass
class TopNewsItem:
    title: str
    url: str
    image_url: str
    category: str
    author: str
    published_time: str
    type: Optional[str] = None

@dataclass
class Category:
    name: str

@dataclass
class InsightNewsItem:
    title: str
    url: str
    image_url: str
    categories: List[Category]
    published_time: str
    data_source: Optional[str] = None  # For "Data via Farside Investors" cases