#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapy
import time
from urlparse import urlparse
from lazada.items import *

class LazadaCrawler2(scrapy.Spider):
    name = "lazadaCrawler2"
    allowed_domains = ["lazada.co.th", "amazon.co.jp"]
    start_urls = [
        "http://www.amazon.co.jp/dp/B00PXJ55T4/ref=sr_1_4?ie=UTF8&qid=1450226633&sr=8-4&keywords=RS530",
        "http://www.amazon.co.jp/dp/B00EK8JUCC/qid=1450227953",
        "http://www.amazon.co.jp/dp/B005FD7SFM/ref=&qid=1450227714",
        "http://www.lazada.co.th/shiseido-maquillage-dramatic-melting-rouge-41g-rs530-992013.html",
        "http://www.lazada.co.th/kanebo-primavista-long-keep-base-spf20-pa-sofina-767368.html",
        "http://www.lazada.co.th/kose-medicated-sekkisei-360ml12oz-892769.html?setLang=th"
    ]

    def strip_text(self, text):
        return ''.join(text.split())

    def extract_digits_from_string(self, text):
        return int(filter(str.isdigit, text.encode('utf-8')))

    def parse(self, response):
        item = LazadaItem2()

        baseUrl = urlparse(response.url).netloc
        if baseUrl == 'www.amazon.co.jp':
            item['title'] = response.css('#productTitle::text').extract()[0].strip()
            try:
                item['original_price'] = self.extract_digits_from_string(response.css('#price table tr:nth-of-type(1) td:nth-of-type(2)::text').extract()[0])
            except:
                item['original_price'] = '-'
            item['current_price'] = self.extract_digits_from_string(response.css('#priceblock_ourprice::text').extract()[0])
            item['currency'] = 'Yen'
            item['date'] = time.strftime("%Y/%m/%d")
        else:
            item['title'] = response.css('.product-info-name::text').extract()[0].strip()
            try:
                item['original_price'] = self.extract_digits_from_string(response.css('#price_box::text').extract()[0])
            except:
                item['original_price'] = '-'
            item['current_price'] = self.extract_digits_from_string(response.css('.product-price::text').extract()[0])
            item['currency'] = 'Baht'
            item['date'] = time.strftime("%Y/%m/%d")

        yield item;
