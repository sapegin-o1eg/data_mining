# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import re
import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


def cleaner_photo(values):
    if values[:2] == '//':
        return f'http:{values}'
    return values


def strip_spaces(value):
    return value.strip()


def to_int(value):
    if value.isdigit():
        return int(value)
    return None


def extract_area(value):
    area = re.search(r'^\d+\.{0,1}\d+', value)
    if area:
        return float(area.group())
    return None


class RealestateparserItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(to_int), output_processor=TakeFirst())
    currency = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(cleaner_photo))
    floors = scrapy.Field(input_processor=MapCompose(strip_spaces, to_int), output_processor=TakeFirst())
    floor = scrapy.Field(input_processor=MapCompose(strip_spaces, to_int), output_processor=TakeFirst())
    type = scrapy.Field(input_processor=MapCompose(strip_spaces), output_processor=TakeFirst())
    rooms = scrapy.Field(input_processor=MapCompose(strip_spaces), output_processor=TakeFirst())
    area_total = scrapy.Field(input_processor=MapCompose(extract_area), output_processor=TakeFirst())
    area_living = scrapy.Field(input_processor=MapCompose(extract_area), output_processor=TakeFirst())


