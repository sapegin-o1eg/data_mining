# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from database.base import VacancyDB
from database.models import Vacancy


class JobparserPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy
        self.sql_db = VacancyDB('sqlite:///vacancy.sqlite')

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        db_item = Vacancy(name=item.get('name'), spider=spider.name, salary=item.get('salary'))
        self.sql_db.add_salary(db_item)
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
