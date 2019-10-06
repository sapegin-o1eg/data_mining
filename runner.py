import os
from os.path import join, dirname
from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from facebookscraper import settings
from facebookscraper.spiders.facebook import FacebookSpider

do_env = join(dirname(__file__), '.env')
load_dotenv(do_env)

FACEBOOK_LOGIN = os.getenv('FACEBOOK_LOGIN')
FACEBOOK_PWD = os.getenv('FACEBOOK_PWD')


if __name__ == '__main__':
    target_users = ['100013578120930', '100001619088393', 'dima.martinov.73', '100001177000141', 'burkovskaya.yulk']
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(FacebookSpider, FACEBOOK_LOGIN, FACEBOOK_PWD, target_users)
    process.start()
