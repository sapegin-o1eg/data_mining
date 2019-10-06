# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import re
import scrapy
from scrapy.loader.processors import MapCompose
from datetime import datetime


def clean_birthday(birthday):
    month_dict = {'января': 'Jun',
                  'февраля': 'Feb',
                  'марта': 'Mar',
                  'апреля': 'Apr',
                  'мая': 'May',
                  'июня': 'Jun',
                  'июля': 'Jul',
                  'августа': 'Aug',
                  'сентября': 'Sep',
                  'октября': 'Oct',
                  'ноября': 'Nov',
                  'декабря': 'Dec'
    }
    try:
        b = birthday.split()
        b[1] = month_dict[b[1]]
        birthday = ' '.join(b[:3])
        return datetime.strptime(birthday, '%d %b %Y').isoformat()
    except:
        return birthday


def clean_fbid(fbid):
    return int(re.search(r'profile/(\d+)', fbid).group(1))


class FacebookscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class FacebookProfileItem(scrapy.Item):
    _id = scrapy.Field()
    fbid = scrapy.Field(input_processor=MapCompose(clean_fbid))
    name = scrapy.Field()
    birthday = scrapy.Field(input_processor=MapCompose(clean_birthday))
    friends = scrapy.Field()
    avatar_images = scrapy.Field()
