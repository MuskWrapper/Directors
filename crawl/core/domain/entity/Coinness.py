from dataclasses import dataclass
from typing import List


@dataclass
class NewsItem:
    time: str
    title: str
    content: str
    bull_count: int
    bear_count: int
    quote_count: int
    coin_tags: List[str]
    date: str
    isHighlight: bool
