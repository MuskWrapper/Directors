import asyncio
import json

from crawl.executor.usecase.CoinnessUseCase import CrawlCoinnessUseCase

async def main():
    crawler = CrawlCoinnessUseCase()
    result = await crawler.fetch_coinness_news()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())