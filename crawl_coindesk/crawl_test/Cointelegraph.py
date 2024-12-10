# pip install requests
import requests
import configparser

config = configparser.ConfigParser()
config.read('../config.ini')

apikey = config['system']['key']


async def main():
    url = 'https://cointelegraph.com/'
    params = {
        'url': url,
        'apikey': apikey,
    }
    response = requests.get('https://api.zenrows.com/v1/', params=params)
    print(response.text)
