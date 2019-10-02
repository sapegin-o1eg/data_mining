# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from realestateparser.items import RealestateparserItem


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/alushta/kvartiry/prodam?cd=1']

    def parse(self, response):
        ads_links = response.xpath('//a[@class="item-description-title-link"]/@href').extract()
        for ad in ads_links:
            yield response.follow(ad, callback=self.parse_ad)

        next_page = response.xpath('//a[contains(text(), "Следующая страница")]/@href').get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)


    def parse_ad(self, response):
        loader = ItemLoader(item=RealestateparserItem(), response=response)

        css_title = 'h1.title-info-title span.title-info-title-text::text'
        loader.add_css('title', css_title)

        xpath_photos = '//div[contains(@class, "gallery-img-wrapper")]'\
                       '//div[contains(@class, "gallery-img-frame")]/@data-url'
        xpath_floors = '//li[@class="item-params-list-item"][./span[contains(text(), "Этажей в доме:")]]/text()'
        xpath_floor = '//li[@class="item-params-list-item"][./span[contains(text(), "Этаж:")]]/text()'
        xpath_type = '//li[@class="item-params-list-item"][./span[contains(text(), "Тип дома:")]]/text()'
        xpath_rooms = '//li[@class="item-params-list-item"][./span[contains(text(), "Количество комнат:")]]/text()'
        xpath_area_total = '//li[@class="item-params-list-item"][./span[contains(text(), "Общая площадь:")]]/text()'
        xpath_area_living = '//li[@class="item-params-list-item"][./span[contains(text(), "Жилая площадь:")]]/text()'
        xpath_currency = '//span[@class="price-value-prices-list-item-currency_sign"]/@content'
        xpath_price = '//span[@class="js-item-price"]/@content'
        loader.add_xpath('photos', xpath_photos)
        loader.add_xpath('floors', xpath_floors)
        loader.add_xpath('floor', xpath_floor)
        loader.add_xpath('type', xpath_type)
        loader.add_xpath('rooms', xpath_rooms)
        loader.add_xpath('area_total', xpath_area_total)
        loader.add_xpath('area_living', xpath_area_living)
        loader.add_xpath('currency', xpath_currency)
        loader.add_xpath('price', xpath_price)

        yield loader.load_item()
