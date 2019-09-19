# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://hh.ru/search/vacancy?text={self.keyword}&area=113&st=searchVacancy']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        full_url = response.urljoin(next_page)
        yield response.follow(full_url, callback=self.parse)

        vacancy = response.css(
            'div.vacancy-serp div.vacancy-serp-item div.vacancy-serp-item__row_header a.bloko-link::attr(href)').extract()

        for link in vacancy:
            yield response.follow(link, callback=self.vacansy_parse)

    def vacansy_parse(self, response: HtmlResponse):
        name = response.xpath('//h1[@class="header"][@data-qa="vacancy-title"]//text()').getall()
        name = ''.join(name)
        salary = response.css('div.vacancy-title p.vacancy-salary::text').extract_first()
        url = response.url
        employer = response.xpath('//a[@class="vacancy-company-name"]/span/text()').get()
        yield JobparserItem(name=name, salary=salary, url=url, employer=employer)
