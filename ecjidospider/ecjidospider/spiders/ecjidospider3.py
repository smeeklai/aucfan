#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup, Comment, element
import re
from difflib import SequenceMatcher
from collections import OrderedDict
from urlparse import urlparse
import operator
from ecjidospider.items import *
import nkf

class GreedySearch(scrapy.Spider):
    name = 'greedySearch'

    def __init__(self, url=None, *args, **kwargs):
        super(GreedySearch, self).__init__(*args, **kwargs)
        self.start_urls = [str(url)]

    # start_urls = ["http://www.ksdenki.com/ec/commodity/00000000/4549077459336/",
    # "http://www.biccamera.com/bc/disp/CSfGoodsPage_001.jsp?GOODS_NO=3117781",
    # "http://www.yodobashi.com/%E3%83%AD%E3%83%AC%E3%83%83%E3%82%AF%E3%82%B9-ROLEX-214270-%E3%82%A8%E3%82%AF%E3%82%B9%E3%83%97%E3%83%AD%E3%83%BC%E3%83%A9%E3%83%BC/pd/100000001001319012/",
    # "http://www.askul.co.jp/p/374127/",
    # "http://www.suruga-ya.jp/kaitori_detail/133056143"]

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def stripString(self, text):
        return ''.join(text.split())

    def get_element(self, tag):
        if 'class' in tag.attrs:
            result = '%s.%s' % (tag.name, tag['class'])
            return result.replace("u'", '').replace("'", '')
        else:
            if len(tag.find_previous_siblings(tag.name)) > 0 or len(tag.find_next_siblings(tag.name)) > 0:
                return '%s:nth-of-type(%d)' % (tag.name, len(tag.find_previous_siblings(tag.name)) + 1)
            else:
                return '%s' % (tag.name)
            # return '%s:nth-of-type(1)' % (tag.name)

    def get_css_selector(self, tag, responseUnicode, key, response):
        if not isinstance(tag, basestring):
            soup2 = BeautifulSoup(responseUnicode.decode('utf-8'), 'html5lib')
            for elem in soup2.findAll(['script', 'style']):
                elem.extract()
            comments = soup2.findAll(text=lambda text:isinstance(text, Comment))
            [comment.extract() for comment in comments]
            tList = soup2.find_all(tag.name)
            tagIndex = tList.index(tag)

            if tag.attrs.has_key('id'): #Check in case id is like '0.23214234'
                if not (tag['id'].replace('.', '9').isdigit()):
                    selector = '#%s' % (tag['id'])
                    selector = selector.replace('[', '').replace(']', '')
                    print "%s css selector: %s" % (key, selector)
                    selector_result = response.css(selector.encode('utf-8')).extract()
                    if len(selector_result) > 1:
                        selector_output = "There're %d results in list, please check" % (len(selector_result))
                        print selector_output
                        for i in range(0, len(selector_result)):
                            print "%s result[%d]: %s" % (key, i+1, selector_result[i])
                    elif len(selector_result) != 0:
                        selector_output = selector_result[0]
                        print "%s result: %s" % (key, selector_output)
                    else:
                        selector_output = "Can't find CSS result (Probably css result might have errors)"
                        print selector_output
                    return selector, selector_output
                else:
                    selector = ''
                    for parent in tList[tagIndex].parents:
                        if parent.attrs.has_key('id'):
                            if not (parent['id'].replace('.', '9').isdigit()):
                                selector = '#' + parent['id'] + ' > ' + selector
                                break
                            else:
                                # if parent.name != "tbody":
                                if parent.name != "[document]" and parent.name != "html":
                                    selector = self.get_element(parent) + ' > ' + selector
                        else:
                            # if parent.name != "tbody":
                            if parent.name != "[document]" and parent.name != "html":
                                selector = self.get_element(parent) + ' > ' + selector
            else:
                selector = ''
                for parent in tList[tagIndex].parents:
                    if parent.attrs.has_key('id'):
                        if not (parent['id'].replace('.', '9').isdigit()):
                            selector = '#' + parent['id'] + ' > ' + selector
                            break
                        else:
                            # if parent.name != "tbody":
                            if parent.name != "[document]" and parent.name != "html":
                                selector = self.get_element(parent) + ' > ' + selector
                    else:
                        # if parent.name != "tbody":
                        if parent.name != "[document]" and parent.name != "html":
                            selector = self.get_element(parent) + ' > ' + selector

                selector = selector + ' ' + self.get_element(tList[tagIndex])
                selector = selector.replace('[', '').replace(']', '')
                print "%s css selector: %s" % (key, selector)
                selector_result = response.css(selector.encode('utf-8')).extract()
                if len(selector_result) > 1:
                    selector_output = "There're %d results in list, please check" % (len(selector_result))
                    print selector_output
                    for i in range(0, len(selector_result)):
                        print "%s result[%d]: %s" % (key, i+1, selector_result[i])
                elif len(selector_result) != 0:
                    selector_output = selector_result[0]
                    print "%s result: %s" % (key, selector_output)
                else:
                    selector_output = "Can't find CSS result (Probably css result might have errors)"
                    print selector_output
                return selector, selector_output
        else:
            print "%s css selector: %s" % (key, tag)
            selector_output = '-'
            return tag, selector_output

    def getTitleTypeScore(self, title_type):
        if title_type == 'h1':
            score = 0.1
        elif title_type == 'h2':
            score = 0.07
        elif title_type == 'h3':
            score = 0.05
        else:
            score = 0
        return score


    def findTitle(self, soup):
        result = {}
        title_candidate_list = soup.find_all('h1') + soup.find_all('h2') + soup.find_all('h3')
        if len(title_candidate_list) != 0:
            for candidate in title_candidate_list:
                currentSimilarScore = self.similar(soup.title.text, candidate.text.strip())
                currentSimilarScore += self.getTitleTypeScore(candidate.name)
                if currentSimilarScore != 1:
                    result[candidate] = currentSimilarScore
        return result

    def getJANCode(self, soup):
        jan = re.findall(r"\d{12,13}", soup.text)
        try:
            if len(jan) != 0:
                return soup.find(string=re.compile(jan[0])).parent
            else:
                return "-"
        except:
            return "-"

    def findPrice(self, priceList, isTag):
        result = []
        for elem in priceList:
            price_stripedText = self.stripString(elem.text)
            price_candidates = re.findall(u"￥(\d*,?\d+)", price_stripedText.replace(u'¥', u'￥'))
            if len(price_candidates) == 0:
                    price_candidates = re.findall(u"(\d*,?\d+)円", price_stripedText)
            if len(price_candidates) != 0:
                for price in price_candidates:
                    priceTag = elem.find(string=re.compile(u'￥' + price)) if elem.find(string=re.compile(u'￥' + price)) is not None else elem.find(string=re.compile(price + u'円?'))
                    if (priceTag is not None):
                        result.append(priceTag.parent)
                if isTag:
                    break;
        return list(OrderedDict.fromkeys(result))

    def getMega(self, manufacturerCandidates):
        result = {}
        if len(manufacturerCandidates) != 0:
            for candidate in manufacturerCandidates:
                manufacturer = ""
                try:
                    manufacturerSibling = [sib for sib in candidate.parent.next_siblings if not isinstance(sib, basestring) and sib.text.strip()]
                except:
                    manufacturerSibling = [];
                if len(manufacturerSibling) != 0:
                    manufacturer = manufacturerSibling[0]
                    if manufacturer.text.strip():
                        striped_candidate_text = candidate.strip()
                        if u'メーカー' in striped_candidate_text:
                            currentSimilarScore = self.similar(u'メーカー', striped_candidate_text)
                            result[manufacturer] = currentSimilarScore
                        elif u'ブランド' in striped_candidate_text:
                            currentSimilarScore = self.similar(u'ブランド', striped_candidate_text)
                            result[manufacturer] = currentSimilarScore
                # currentSimilarScore = self.similar(soup.title.text, candidate.text.strip())
                # currentSimilarScore += self.getTitleTypeScore(candidate.name)
                # if currentSimilarScore != 1:
                #     result[candidate] = currentSimilarScore
        return result

    def getSellDate(self, sellDateCandidates):
        sellDate = "-"

        # if len(sellDateCandidates) == 1:
        sellDateSibling = [sib for sib in sellDateCandidates.parent.next_siblings if sib.string is not None and sib.string.strip()]
        if len(sellDateSibling) != 0:
            sellDate = sellDateSibling[0]
        else:
            parentString = self.stripString(sellDateCandidates[0].parent.text)
            # parentString = parentString.replace(u'年', '/').replace(u'月', '/').replace(u'日', ' ')
            try:
                sellDate = re.search(u'\d{4}\D\d{2}\D\d{2}', parentString).group()
                sellDate = sellDate.replace(u'年', '/').replace(u'月', '/').replace(u'日', ' ')
            except:
                sellDate = "-"
            # sellDate = sellDateCandidates[0].parent
        # elif len(sellDateCandidates) > 1:
        #     bestCandidate = ""
        #     bestCandidateScore = 0
        #     for sellDateCandidate in sellDateCandidates:
        #         # if (urlparse(response.url).netloc == 'www.yodobashi.com'):
        #         #     currentScore = self.similar(sellDateCandidate, u'販売開始日')
        #         # else:
        #         currentScore = self.similar(sellDateCandidate, u'発売日')
        #         if currentScore > bestCandidateScore:
        #             bestCandidateScore = currentScore
        #             bestCandidate = sellDateCandidate
        #     if (bestCandidateScore >= 0.6):
        #         bestCandidateSibling = [sib.string for sib in bestCandidate.parent.next_siblings if sib.string != '\n' and sib.string is not None]
        #         if len(bestCandidateSibling) != 0:
        #             sellDate = bestCandidateSibling[0].parent
        #             # print sellDate.parent
        #         else:
        #             parentString = self.stripString(bestCandidate.parent.text)
        #             parentString = parentString.replace(u'年', '/').replace(u'月', '/').replace(u'日', ' ')
        #             # sellDate = re.search(u'\d{4}/\d{2}/\d{2}', parentString).group()
        #             sellDate = sellDateCandidates[0].parent
        return sellDate

    def getPriceLowAccuracy(self, responseUnicode):
        soup2 = BeautifulSoup(responseUnicode.decode('utf-8'), 'html5lib')
        for elem in soup2.findAll(['script', 'style']):
            elem.extract()
        comments = soup2.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]

        filteredData = self.removeFooter(soup2)
        return self.findPrice(filteredData, False)

    def removeFooter(self, soup):
        divList = soup.find_all('div')
        list3 = []
        parentFilterRound = 0

        if soup.find('footer'):
            #remove <footer>
            list2 = [div for div in divList if not u'footer' in [parent.name for parent in div.parents]]
        elif soup.find(id='footer'):
            #remove div id'footer'
            for elem in soup.findAll(id='footer'):
                elem.extract()
            list2 = soup.find_all('div')
        else:
            list2 = divList

        #delete all child div in each div
        # for div in list2:
        #     for elem in div.find_all('div'):
        #         elem.extract()

        # for i in range (0, len(list2)):
        #     links = len(list2[i].find_all('a'))
        #     chars = len(self.stripString(list2[i].text))
        #     parents = len([parent.name for parent in list2[i].parents if parent.name == u'div'])
        #     contents = len([child.name for child in list2[i].contents if child != '\n' and child.name is not None])
        #     pics = len(list2[i].find_all('img'))
        #     if chars == 0 or contents == 0 or links > 10:
        #         list3.append(list2[i])
        #     # print ('list %d has %d links\t %d chars\t %d div parents\t %d childs %d pics' % (i+1, links, chars, parents, contents, pics))
        #
        # for aList in list3:
        #     list2.remove(aList)

        return list2

    def parse(self, response):
        #Item for handling json export
        item = Ecjido2Item()

        #Convert response body into Unicode
        responseUnicode = nkf.nkf(nkf.guess(response.body), response.body)
        responseUnicode = nkf.nkf('-Ew', responseUnicode)

        #Create a BeautifulSoup of the website
        soup = BeautifulSoup(responseUnicode.decode('utf-8'), 'html5lib')
        #Remove <script> and comment tags
        for elem in soup.findAll(['script', 'style']):
            elem.extract()
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]

        #Rearrange received html tags
        soup.prettify().strip()

        #Get title
        title_tag = self.findTitle(soup)
        resultList = []
        sorted_title = sorted(title_tag.items(), key=operator.itemgetter(1), reverse=True)
        best_title_candidate = sorted_title[0][0]
        for title_candidate in sorted_title:
            selector, result = self.get_css_selector(title_candidate[0], responseUnicode, 'title', response)
            resultList.append({'selector' : selector, 'result' : result})
        item['title'] = resultList

        #Get Price
        if not isinstance(best_title_candidate, basestring):
            #Get price (Higher accuracy because the area of finding is narrowed down)
            div_parents = [div_parent for div_parent in best_title_candidate.parents if div_parent.name == 'div']
            product_prices = self.findPrice(div_parents, True)
            if len(product_prices) == 0:
                product_prices = self.getPriceLowAccuracy(responseUnicode)
        else:
            #Get price (Lower accuracy because searching strings for entire page)
            product_prices = self.getPriceLowAccuracy(responseUnicode)

        resultList = []
        for elem in product_prices:
            selector, result = self.get_css_selector(elem, responseUnicode, 'price', response)
            resultList.append({'selector' : selector, 'result' : result})
        item['price'] = resultList

        # # Get Spec
        # selector, result = self.get_css_selector(self.getSpec(soup), response, 'specs')
        # item['specs'] = {'selector' : selector, 'result' : result}

        #Get JAN
        selector, result = self.get_css_selector(self.getJANCode(soup), responseUnicode, 'jan_code', response)
        item['jan_code'] = {'selector' : selector, 'result' : result}

        soup2 = BeautifulSoup(responseUnicode.decode('utf-8'), 'html5lib')
        for elem in soup2.findAll(['script', 'style']):
            elem.extract()
        comments = soup2.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]

        filteredData = self.removeFooter(soup2)
        sellDateCandidates = []
        manufacturerCandidates = []

        for aList in filteredData:
            manufacturerCandidate = aList.find_all(string=re.compile(u'メーカー'))
            brandCandidate = aList.find_all(string=re.compile(u'ブランド'))
            sellDateCandidate = aList.find_all(string=re.compile(u'発売日'))
            if manufacturerCandidate:
                manufacturerCandidates.extend(manufacturerCandidate)
            if brandCandidate:
                manufacturerCandidates.extend(brandCandidate)
            if sellDateCandidate:
                sellDateCandidates.extend(sellDateCandidate)

        #Get manufacturer
        manufacturerCandidates = list(OrderedDict.fromkeys(manufacturerCandidates))
        manufacturer = self.getMega(manufacturerCandidates)
        sorted_manufacturer = sorted(manufacturer.items(), key=operator.itemgetter(1), reverse=True)
        if len(manufacturerCandidates) != 0:
            resultList = []
            for manufacturer_candidate in sorted_manufacturer:
                selector, result = self.get_css_selector(manufacturer_candidate[0], responseUnicode, 'manufacturer', response)
                resultList.append({'selector' : selector, 'result' : result})
            item['manufacturer'] = resultList
        else:
            selector, result = self.get_css_selector("-", responseUnicode, 'manufacturer', response)
            item['manufacturer'] = {'selector' : selector, 'result' : result}

        #For yodobashi (Yodobashi use '販売開始日' instead)
        # if len(sellDateCandidates) == 0:
        #     for aList in filteredData:
        #         sellDateCandidate = aList.find_all(string=re.compile(u'販売開始日'))
        #         if sellDateCandidate:
        #             sellDateCandidates.extend(sellDateCandidate)

        #Get 発売日
        sellDateCandidates = list(OrderedDict.fromkeys(sellDateCandidates))
        if len(sellDateCandidates) != 0:
            resultList = []
            for sellDateCandidate in sellDateCandidates:
                selector, result = self.get_css_selector(self.getSellDate(sellDateCandidate), responseUnicode, 'date_of_issue', response)
                resultList.append({'selector' : selector, 'result' : result})
            item['date_of_issue'] = resultList
        else:
            selector, result = self.get_css_selector("-", responseUnicode, 'date_of_issue', response)
            item['date_of_issue'] = {'selector' : selector, 'result' : result}

        yield item
