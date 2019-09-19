from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparser import settings
from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.superjob import SuperjobruSpider


if __name__ == '__main__':
    keyword = 'Python'
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HhruSpider, keyword=keyword)
    process.crawl(SuperjobruSpider, keyword=keyword)
    process.start()
