# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

class BookPipeline(object):
    def process_item(self, item, spider):
        with open('jdbook.txt','a') as f:
            json.dump(item, f, ensure_ascii=False, indent=2)
            f.write('\n')
        return item

class DangPipeline(object):
    def process_item(self, item, spider):
        with open('dangbook.txt','a') as f:
            json.dump(item, f, ensure_ascii=False, indent=2)
            f.write('\n')
        return item

class AmazonPipeline(object):
    def process_item(self, item, spider):
        with open('amazonbook.txt', 'a') as f:
            json.dump(item, f, ensure_ascii=False, indent=2)
            f.write('\n')
        return item