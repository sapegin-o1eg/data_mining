# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from database.base import VacancyDB
from database.models import Vacancy
import re


class JobparserPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy
        self.sql_db = VacancyDB('sqlite:///vacancy.sqlite')

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        db_item = Vacancy(name=item.get('name'), spider=spider.name, salary=item.get('salary'), url=item.get('url'),
                          employer=item.get('employer'))
        self.sql_db.add_salary(db_item)
        return item


class SpaceCleanerPipeline(object):
    def __init__(self):
        self.start_space_re = re.compile('^ ')
        self.no_brake_space_re = re.compile('\xa0')

    def process_item(self, item, spider):
        item['salary'] = re.sub(self.no_brake_space_re, ' ', item['salary'])
        if spider.name == 'hhru':
            item['salary'] = re.sub(self.start_space_re, '', item['salary'])
            item['employer'] = re.sub(self.start_space_re, '', item['employer'])
        return item
