# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class AwardWinningMoviePipeline(object):
    def __init__(self):
        self.connection = pymongo.MongoClient()
        self.db = self.connection['金鸡奖提名电影']
        self.collection = self.db['1978年到2018年']
        self.id = 1

    def process_item(self, item, spider):
        document = dict(item)
        if document['movie'] == '':
            return item
        document['_id'] = self.id
        self.collection.insert(document)
        self.id += 1
        return item
