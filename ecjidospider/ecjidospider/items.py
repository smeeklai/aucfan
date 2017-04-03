# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EcjidospiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field();
    price = scrapy.Field();
    jan_code = scrapy.Field();
    date_of_issue = scrapy.Field();
    manufacturer = scrapy.Field();
    specs = scrapy.Field();

class Ecjido2Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field();
    price = scrapy.Field();
    jan_code = scrapy.Field();
    date_of_issue = scrapy.Field();
    manufacturer = scrapy.Field();
    status = scrapy.Field();
    message = scrapy.Field();
