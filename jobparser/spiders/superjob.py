# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SuperjobruSpider(scrapy.Spider):
    name = 'superjobru'
    allowed_domains = ['superjob.ru']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://www.superjob.ru/vacancy/search/?keywords={self.keyword}&geo%5Bc%5D%5B0%5D=1']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.f-test-link-dalshe::attr(href)').extract_first()
        full_url = response.urljoin(next_page)
        yield response.follow(full_url, callback=self.parse)

        vacancy = response.xpath('//a[re:test(@class, "^\S{5} _\S{5}.*_\S{5} _\S{5}$")]/@href').extract()

        for link in vacancy:
            response.urljoin(link)
            yield response.follow(link, callback=self.vacansy_parse)

    def vacansy_parse(self, response: HtmlResponse):
        name = response.xpath('//h1[re:test(@class, "^_\S{5} \S{5} \S{5} _\S{5}$")]/text()').get()
        salary = response.xpath('//span[re:test(@class, "^_\S{5} _\S{5} \S{5} \S{5} _\S{5}$")]//text()').getall()
        salary = ''.join(salary)
        url = response.url
        employer = response.xpath('//h2[re:test(@class, "^_\S{5} \S{5} _\S{5} _\S{5} _\S{5} _\S{5}$")]/text()').get()
        yield JobparserItem(name=name, salary=salary, url=url, employer=employer)
