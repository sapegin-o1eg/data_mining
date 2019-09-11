# Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему,
# пройдя авторизацию. Ответ сервера записать в файл.

import requests
import json


class UrbanDictionaryApi:
    USER_AGENT = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/74.0.3729.169 Safari/537.36"""

    def __init__(self):
        self.url = 'https://mashape-community-urban-dictionary.p.rapidapi.com/define'
        self.headers = {
            'User-Agent': self.USER_AGENT,
            'x-rapidapi-host': 'mashape-community-urban-dictionary.p.rapidapi.com',
            'x-rapidapi-key': '8b9c3a2b8emsh2f598171528c015p1082cfjsn5135413947ed'
        }

    def define(self, term):
        querystring = {"term": term}
        response = requests.request("GET", self.url, headers=self.headers, params=querystring)
        parsed = json.loads(response.text)
        pretty_json = json.dumps(parsed, indent=4)
        with open(f'{term}.json', 'w') as outfile:
            print(pretty_json, file=outfile)


if __name__ == '__main__':
    repos = UrbanDictionaryApi()
    repos.define('asap')
