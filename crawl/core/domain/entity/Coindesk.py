from dataclasses import dataclass
from typing import Optional, List


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

@dataclass
class LatestNewsItem:
    title: str
    content: Optional[str]
    url: str
    category: str
    published_time: str
    image_url: Optional[str]
