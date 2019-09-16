import requests
from bs4 import BeautifulSoup
import time
import random
from pymongo import MongoClient


class AvitoFlats:

    def __init__(self, verbose=None):
        self.user_agent = """Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/76.0.3809.132 Safari/537.36"""
        self.base = 'https://www.avito.ru'
        self.ad_urls = []
        self.next = None
        self.verbose = verbose
        self.proxy = {}

    def get_urls(self, url):
        if url:
            if self.verbose:
                print(f'get_urls -> {url}')
            time.sleep(random.randint(1, 3))
            response = requests.get(url, headers={'User-Agent': self.user_agent}, proxies=self.proxy)
            soup = BeautifulSoup(response.text, 'lxml')
            body = soup.html.body
            ads = body.findAll('div', attrs={'class': 'item__line'})
            urls = [f'{self.base}{itm.find("a").attrs["href"]}' for itm in ads]
            self.ad_urls.extend(urls)
            next_page = body.find('a', attrs={'class': 'js-pagination-next'})
            if next_page:
                self.next = next_page.attrs['href']
                self.get_urls(f'{self.base}{self.next}')

    def parse_ad(self, url):
        time.sleep(random.randint(1, 3))
        response = requests.get(url, headers={'User-Agent': self.user_agent}, proxies=self.proxy)
        soup = BeautifulSoup(response.text, 'lxml')
        body = soup.html.body
        title = body.find('h1', attrs={'class': 'title-info-title'}).span.text
        name = body.find('div', attrs={'class': 'js-seller-info-name'}).a.get_text(strip=True)
        profile_url = body.find('div', attrs={'class': 'js-seller-info-name'}).a.attrs['href']
        price = body.find('span', attrs={'class': 'js-item-price', 'itemprop': 'price'}).attrs.get('content')
        result = {'title': title,
                  'owner_name': name,
                  'owner_profile_url': f'{self.base}{profile_url}',
                  'price': int(price) if price and price.isdigit else None,
                  'ad_url': response.url,
                  'params': [tuple(itm.text.split(':')) for itm in
                             soup.body.findAll('li', attrs={'class': 'item-params-list-item'})]
                  }
        if self.verbose:
            print(f'parse_ad -> {result}')
        return result

    def store_to_db(self):
        client = MongoClient('localhost', 27017)
        database = client.lesson2
        collection = database.avito
        for ad in self.ad_urls:
            result = self.parse_ad(ad)
            collection.insert_one(result)


if __name__ == '__main__':
    flats = AvitoFlats(verbose=True)
    flats.get_urls('https://www.avito.ru/dzhankoy/kvartiry/prodam?cd=1')
    flats.store_to_db()


