import os

from bs4 import BeautifulSoup
from zenrows import ZenRowsClient
from typing import Optional, Dict, List


class ZenrowsUtil:
    def __init__(self):
        self.client = ZenRowsClient(os.environ.get('ZENROWS_API_KEY', None))

    async def fetch_page(self, url: str, wait: int, js_instructions: Optional[str]) -> BeautifulSoup:
        """웹 페이지를 가져와서 파싱된 BeautifulSoup 객체를 반환합니다."""
        print("fetching")

        try:
            params = {
                'js_render': True,
                'wait': wait,
                'js_instructions': js_instructions
            }

            # 응답을 텍스트로 가져오기
            response = self.client.get(url, params=params)
            html_content = response.text

            # BeautifulSoup 객체 생성 및 반환
            print(html_content)

            return BeautifulSoup(html_content)

        except Exception as error:
            print(f"Failed to fetch page: {error}")
            print(f"Response type: {type(response)}")
            print(f"Response: {response}")
            raise error
