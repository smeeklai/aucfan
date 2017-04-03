#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapy
import re
import time
from lazada.items import *

class LazadaCrawler(scrapy.Spider):
    name = "lazadaCrawler"
    allowed_domains = ["lazada.co.th"]
    start_urls = [
        "http://www.lazada.co.th/mistine/?setLang=en",
        "http://www.lazada.co.th/kose/?setLang=en",
        "http://www.lazada.co.th/shiseido/?setLang=en"
    ]

    def strip_text(self, text):
        return ''.join(text.split())

    def parse(self, response):
        for href in response.css('.product-image-url::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, self.parse_products)

        next_page_url = response.css('.page-link--next a::attr(href)')
        if next_page_url.extract():
            full_url = response.urljoin(next_page_url.extract()[0])
            yield scrapy.Request(full_url, self.parse)

        # filename = response.url.split("/")[-2] + '.html'
        # with open(filename, 'wb') as f:
        #     f.write(response.body)

    def parse_products(self, response):
        item = LazadaItem()
        item['title'] = response.css('.product-info-name::text').extract()[0].strip()
        item['price'] = int(self.strip_text(response.css('.product-price::text').extract()[0]).replace(u'฿', "").replace(u',', ""))

        subDetail1 = [self.strip_text(i) for i in response.css('.description-details-full-text b::text').extract() if self.strip_text(i) != '']
        subDetail2 = [self.strip_text(i) for i in response.css('.description-details-full-text::text').extract() if self.strip_text(i) != '']
        detailList = subDetail1 + subDetail2
        detail = ""
        for elem in detailList:
            detail += elem + " "
        item['detail'] = detail

        spec_keys = [self.strip_text(i) for i in response.css('.simpleList li::text').extract() if self.strip_text(i) != '']
        spec_values = response.css('.simpleList li span::text').extract()
        item['brand'] = spec_keys[0].replace(u'Brand:', "")
        specs = ""
        for i in range(0, len(spec_values)):
            specs += '%s %s ' % (spec_keys[i+1], spec_values[i])
        item['spec'] = specs

        rating_result = re.search(u'"avgRating":(\d?.?\d*),', response.body)
        if rating_result.group(1) is not '':
            item['rating'] = rating_result.group(1)
        else:
            item['rating'] = "-"

        item['url'] = response.url
        item['date'] = time.strftime("%Y/%m/%d")
        item['seller_name'] = response.css('.supplier::text').extract()[0]
        try:
            list_len = len(response.xpath('//*[@id="content"]/div[1]/ul/li').extract())
            path = '//*[@id="content"]/div[1]/ul/li[%d]/a/text()' % (list_len - 1)
            item['category'] = response.xpath(path).extract()[0]
        except IndexError:
            item['category'] = '-'
        try:
            item['pic'] = response.css('.product-image-container img::attr(src)').extract()[0]
        except IndexError:
            item['pic'] = '-'
        yield item
