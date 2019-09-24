# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field()
    salary = scrapy.Field()
    url = scrapy.Field()


class InstagramLikerItem(scrapy.Item):
    _id = scrapy.Field()
    liker_id = scrapy.Field()
    liker_username = scrapy.Field()
    liker_full_name = scrapy.Field()
    liker_profile_pic_url = scrapy.Field()
    post_shortcode = scrapy.Field()
    post_owner = scrapy.Field()
    post_url = scrapy.Field()


class InstagramCommentatorItem(scrapy.Item):
    _id = scrapy.Field()
    commentator_id = scrapy.Field()
    commentator_username = scrapy.Field()
    commentator_profile_pic_url = scrapy.Field()
    commentator_text = scrapy.Field()
    post_shortcode = scrapy.Field()
    post_owner = scrapy.Field()
    post_url = scrapy.Field()


