# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient


class JobparserPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item


class InstagramparserPipeline(object):
    def __init__(self, *args, **kwargs):
        super(InstagramparserPipeline, self).__init__(*args, **kwargs)
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instaparser

    def process_item(self, item, spider):
        if item.get('commentator_id'):
            collection = self.mongo_base['commentators']
            collection.insert_one(item)
        elif item.get('liker_id'):
            collection = self.mongo_base['likers']
            collection.insert_one(item)

        return item
