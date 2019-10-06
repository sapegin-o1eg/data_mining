# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
import scrapy
from scrapy.pipelines.images import ImagesPipeline


class FacebookscraperPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.users

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item


class FacebookUserPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item.get('avatar_images'):
            for img in item['avatar_images']:
                try:
                    yield scrapy.Request(img)
                except TypeError:
                    pass

    def item_completed(self, results, item, info):
        if results:
            item['avatar_images'] = [itm[1] for itm in results if itm[0]]
        return item
