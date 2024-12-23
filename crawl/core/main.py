import asyncio
import json
import os
from typing import Dict, Any

from crawl.executor.usecase.CoinnessUseCase import CrawlCoinnessUseCase
from crawl.executor.usecase.CoinDeskLatestNewsUseCase import CoinDeskLatestNewsUseCase
from crawl.executor.usecase.CoinDeskMainPageUseCase import CoinDeskMainPageUseCase
from crawl.executor.usecase.CryptoNewsUseCase import CryptoNewsUseCase
from crawl.executor.usecase.CryptoslateInsightUseCase import CryptoSlateInsightsUseCase
from crawl.executor.usecase.CryptoslateTopNewsUseCase import CryptoSlateUseCase
from utils.ZenrowsUtil import ZenrowsUtil


def save_to_json(data: Dict[str, Any], filename: str) -> None:
    """Save data to a JSON file in the results directory."""
    # Create results directory if it doesn't exist
    os.makedirs("./../../assets/results", exist_ok=True)

    filepath = os.path.join('./../../assets/results', filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved to {filepath}")
    except Exception as e:
        print(f"❌ Error saving to {filepath}: {str(e)}")


async def execute_use_case(name: str, coro) -> Dict[str, Any]:
    """Execute a use case, save results to file, and handle any errors."""
    try:
        result = await coro
        print(f"✅ Successfully executed {name}")

        # Save individual result to JSON file
        filename = f"{name}.json"
        save_to_json(result, filename)

        return {name: result}
    except Exception as e:
        error_result = {"error": str(e)}
        print(f"❌ Error executing {name}: {str(e)}")

        # Save error result to JSON file
        filename = f"{name}_error.json"
        save_to_json(error_result, filename)

        return {name: error_result}


async def main():
    """Execute all use cases concurrently and save their results separately."""
    # Initialize ZenrowsUtil once and share it across use cases
    zenrows_util = ZenrowsUtil()

    # Initialize all use cases
    coinness_usecase = CrawlCoinnessUseCase(zenrows_util)
    coindesk_latest_usecase = CoinDeskLatestNewsUseCase(zenrows_util)
    coindesk_main_usecase = CoinDeskMainPageUseCase(zenrows_util)
    cryptonews_usecase = CryptoNewsUseCase(zenrows_util)
    cryptoslate_insights_usecase = CryptoSlateInsightsUseCase(zenrows_util)
    cryptoslate_top_usecase = CryptoSlateUseCase(zenrows_util)

    # Create tasks for all use cases
    tasks = [
        execute_use_case("coinness_news", coinness_usecase.fetch_coinness_news()),
        execute_use_case("coindesk_latest_news", coindesk_latest_usecase.fetch_latest_news()),
        execute_use_case("coindesk_top_stories", coindesk_main_usecase.fetch_top_stories()),
        execute_use_case("coindesk_most_read", coindesk_main_usecase.fetch_most_read()),
        execute_use_case("cryptonews", cryptonews_usecase.fetch_news()),
        execute_use_case("cryptoslate_insights", cryptoslate_insights_usecase.fetch_insights()),
        execute_use_case("cryptoslate_top_news", cryptoslate_top_usecase.fetch_top_news())
    ]

    print("Starting execution of all use cases...")
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks)

    # Combine all results into a single dictionary for reference
    combined_results = {}
    for result in results:
        combined_results.update(result)

if __name__ == "__main__":
    asyncio.run(main())