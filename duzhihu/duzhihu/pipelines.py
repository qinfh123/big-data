# -*- coding: utf-8 -*-
import json
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class DuzhihuPipeline(object):
    def __init__(self):
        self.fp = open("poem.json", 'w', encoding='utf-8')

    def open_spider(self, spider):
        print('start')

    def process_item(self, item, spider):
        print(2)
        print(type(item))
        item_json = json.dumps(item, ensure_ascii=False)
        self.fp.write(item_json + '\n')
        return item

    def close_spider(self, spider):
        self.fp.close()
        print('finish')