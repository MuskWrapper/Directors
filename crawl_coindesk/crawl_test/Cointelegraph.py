# pip install requests
from zenrows import ZenRowsClient
import configparser

config = configparser.ConfigParser()
config.read('../config.ini')

apikey = config['system']['key']
client = ZenRowsClient(apikey)


async def main():
    url = "https://cointelegraph.com/"
    response = client.get(url)

    print(response.text)
