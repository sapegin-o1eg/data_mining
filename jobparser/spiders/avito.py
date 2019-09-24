# -*- coding: utf-8 -*-
import scrapy
from jobparser.items import JobparserItem


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    base_url = 'https:/avito.ru'

    def __init__(self, keyword, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [f'https://www.avito.ru/rossiya/vakansii?q={keyword}']

    def parse(self, response):
        jobs = response.xpath('//div[@class="item_table-wrapper"]')

        for job in jobs:
            url = job.xpath('.//a/@href').get()
            url = f'{self.base_url}{url}' if url else None
            name = job.xpath('.//a/@title').get()
            currency = job.xpath('.//span[@itemprop="priceCurrency"]/@content').get()
            value = job.xpath('.//span[@class="price "]/@content').get()
            salary = {'currency': currency, 'min_value': value}

            yield JobparserItem(name=name, salary=salary, url=url)

        next_page = response.xpath('//a[contains(text(), "Следующая страница")]/@href').get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)
