# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LazadaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    rating = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    pic = scrapy.Field()
    detail = scrapy.Field()
    spec = scrapy.Field()
    url = scrapy.Field()
    date = scrapy.Field()
    category = scrapy.Field()
    seller_name = scrapy.Field()

class LazadaItem2(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    current_price = scrapy.Field()
    original_price = scrapy.Field()
    currency = scrapy.Field()
    date = scrapy.Field()
    category = scrapy.Field()
    seller_name = scrapy.Field()
