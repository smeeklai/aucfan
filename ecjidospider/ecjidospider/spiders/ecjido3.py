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

class Ecjido3(scrapy.Spider):
    name = 'ecjido3'

    def __init__(self, url=None, *args, **kwargs):
        super(Ecjido3, self).__init__(*args, **kwargs)
        self.start_urls = [str(url)]

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def stripString(self, text):
        # regex = re.compile(r'[\r\t]')
        # return regex.sub('', text).strip()
        return ''.join(text.split())

    def get_element(self, tag):
        if len(tag.find_previous_siblings(tag.name)) > 0 or len(tag.find_next_siblings(tag.name)) > 0:
            # if 'class' in tag.attrs:
            #     if (tag['class'][0].strip() != ""):
            #         result = '%s.%s' % (tag.name, tag['class'][0])
            #     else:
            #         result = '%s' % (tag.name)
            #     return result.replace("u'", '').replace("'", '')
            # else:
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

    def findTitles(self, soup):
        result = {}
        title_candidate_list = soup.find_all('h1') + soup.find_all('h2') + soup.find_all('h3')
        if len(title_candidate_list) != 0:
            for candidate in title_candidate_list:
                currentSimilarScore = self.similar(soup.title.text, self.stripString(candidate.text))
                currentSimilarScore += self.getTitleTypeScore(candidate.name)
                if currentSimilarScore != 1:
                    result[candidate] = currentSimilarScore
        return result

    def getJANCode(self, soup):
        jan = re.findall(r"\d{12,13}", soup.text)
        try:
            if len(jan) != 0:
                print soup.find(string=re.compile(jan[0])).parent
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
                    manufacturerSibling = [sib for sib in candidate.parent.next_siblings if not isinstance(sib, basestring) and self.stripString(sib.text)]
                except:
                    manufacturerSibling = [];
                if len(manufacturerSibling) != 0:
                    manufacturer = manufacturerSibling[0]
                    if self.stripString(manufacturer.text):
                        result[manufacturer] = self.calculateMegaCandidateScore(candidate)
                # else:
                #     manufacturerFirstParent = [firstParent for firstParent in candidate.parents if not isinstance(firstParent, basestring) and self.stripString(firstParent.text)][0]
                #     manufacturer = manufacturerFirstParent
                #     if self.stripString(manufacturer.text):
                #         result[manufacturer] = self.calculateMegaCandidateScore(candidate)
        return result

    def getSellDate(self, sellDateCandidates):
        sellDate = "-"

        # if len(sellDateCandidates) == 1:
        sellDateSibling = [sib for sib in sellDateCandidates.parent.next_siblings if sib.string is not None and sib.string.strip()]
        if len(sellDateSibling) != 0:
            sellDate = sellDateSibling[0]
        else:
            if not isinstance(sellDateCandidates[0], basestring):
                sellDate = self.stripString(sellDateCandidates[0].parent.text)
            else:
                sellDate = sellDateCandidates[0]
            # parentString = parentString.replace(u'年', '/').replace(u'月', '/').replace(u'日', ' ')
            try:
                sellDate = re.search(u'\d{4}\D\d{1,2}\D\d{1,2}', parentString.decode("utf-8")).group()
                sellDate = sellDate.replace(u'年', '/').replace(u'月', '/').replace(u'日', ' ')
            except:
                sellDate = "-"
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

        return list2

    #Return the score of a mega candidates for ranking purpose
    def calculateMegaCandidateScore(self, candidate):
        self.candidate = candidate
        striped_candidate_text = self.stripString(candidate)
        if u'メーカー' in striped_candidate_text:
            score = self.similar(u'メーカー', striped_candidate_text)
        elif u'ブランド' in striped_candidate_text:
            score = self.similar(u'ブランド', striped_candidate_text)
        return score

    def findMainContentDiv(self, title):
        self.title = title
        # print title
        priceKeywords = [u'¥', u'円', u'税抜', u'税込']
        megaKeywords = [u'メーカ', u'ブランド']
        janKeywords = [u'商品コード', u'JAN']
        sellDateKeywords = [u'発売日']
        allKeywords = [priceKeywords, megaKeywords, janKeywords, sellDateKeywords]
        titleParentDivs = [parent for parent in title.parents if parent.name == 'div']
        priceDiv = ""
        bestCandidate = ""
        keywordsFounds = []
        bestCandidateLength = 1;
        #Find keywords in each parent divs of title
        for parentDiv in titleParentDivs:
            priceKeywordsFound, megaKeywordsFound, janKeywordsFound, sellDateKeywordsFound = False, False, False, False
            parentDivText = self.stripString(parentDiv.text)
            # if value of "found" of each type of keywords more than threshold, set the the its keywordsFound == true
            for keyword in allKeywords:
                found = 0
                for key in keyword:
                    if (parentDivText.find(key) != -1):
                        found = found + 1
                if (keyword is priceKeywords):
                    if (found >= 2):
                        priceKeywordsFound = True
                elif (keyword is megaKeywords):
                    if (found >= 1):
                        megaKeywordsFound = True
                elif (keyword is janKeywords):
                    if (found >= 1):
                        janKeywordsFound = True
                else:
                    if (found == 1):
                        sellDateKeywordsFound = True
            #Evaluate keywordsFounds to tell whether this is the right content div or not
            keywordsFounds = [priceKeywordsFound, megaKeywordsFound, janKeywordsFound, sellDateKeywordsFound]
            trueOnly = [trueKeywordFound for trueKeywordFound in keywordsFounds if trueKeywordFound == True]
            #if current length of trueOnly is bestCandidateLength, replace bestCandidate
            if (len(trueOnly) > bestCandidateLength):
                bestCandidate = parentDiv
                bestCandidateLength = len(trueOnly)
            #In some cases, we need to separate main content div and price div because
            #sometime main content div also includes advertisement div which make it hard to search for the item's price
            if not priceDiv and priceKeywordsFound is True:
                # print keywordsFounds
                priceDiv = parentDiv
                print "Price div: " + str(priceDiv.attrs)
        # print keywordsFounds
        return bestCandidate, priceDiv

    def findBestTitle(self, best_three_titles):
        self.best_three_titles = list(best_three_titles)
        result = ""
        for title in best_three_titles:
            #Delete all element except div, form and body (dfb = div, form, body)
            dfb = [parent for parent in title[0].parents if parent.name == 'div' or parent.name == 'body' or parent.name == 'form']
            #Currently, I assume that if the <body> is within the range of 4 from the title,
            #it's not supposed to be the right title because it's too close to the <body>
            dfbElements = [ele.name for ele in dfb]
            if (dfbElements.index('body') <= 4):
                if (self.isDfbContainHeaderAttrs(dfb)):
                    continue
                else:
                    result = title[0]
            else:
                result = title[0]
                break
        return result

    #Check whether dfb contains attrs that has "header" as substring or not
    def isDfbContainHeaderAttrs(self, dfb):
        keyword = "header"
        divs = [div for div in dfb if div.name == 'div']  #get only div
        for div in divs:
            for attrValue in div.attrs.values():
                #Attribute values might be either list or string
                if isinstance(attrValue, basestring):
                    if (attrValue.find(keyword) != -1):
                        return True
                else:
                    for val in attrValue:
                        if (str(val).find(keyword) != -1):
                            return True
        return False
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
        title_tag = self.findTitles(soup)
        resultList = []
        sorted_title = sorted(title_tag.items(), key=operator.itemgetter(1), reverse=True)
        best_three_titles = sorted_title[ : 3];
        best_title = self.findBestTitle(best_three_titles)
        if best_title:
            #Finding main conent and price divs from best title
            mainContent, priceDiv = self.findMainContentDiv(best_title)
            if (mainContent and priceDiv):
                #Define that the using method of important info extraction does work
                item['status'] = "successful"
                print "Main content div: " + str(mainContent.attrs)
                selector, result = self.get_css_selector(best_title, responseUnicode, 'title', response)
                # resultList.append({'selector' : selector, 'result' : result})
                # resultList.append(selector)
                item['title'] = selector

                #Get price (Higher accuracy because the area of finding is narrowed down)
                product_prices = self.findPrice([priceDiv], True)
                if len(product_prices) == 0:
                    product_prices = self.getPriceLowAccuracy(responseUnicode)
                resultList = []
                for elem in product_prices:
                    selector, result = self.get_css_selector(elem, responseUnicode, 'price', response)
                    # resultList.append({'selector' : selector, 'result' : result})
                    resultList.append(selector)
                item['price'] = resultList

                #Get JAN
                selector, result = self.get_css_selector(self.getJANCode(mainContent), responseUnicode, 'jan_code', response)
                item['jan_code'] = selector

                sellDateCandidates = []
                manufacturerCandidates = []

                for aList in [mainContent]:
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
                        # resultList.append({'selector' : selector, 'result' : result})
                        resultList.append(selector)
                    item['manufacturer'] = resultList
                else:
                    selector, result = self.get_css_selector("-", responseUnicode, 'manufacturer', response)
                    item['manufacturer'] = selector
            else:
                #Define that the method of webpage's important info extraction doesn't work
                item['status'] = "error"
                item['message'] = "cannot find the main content"
        else:
            #Define that the method of webpage's important info extraction doesn't work
            item['status'] = "error"
            item['message'] = "cannot find the best title"

        # #Get Price
        # # if not isinstance(best_title_candidate, basestring):
        # #     #Get price (Higher accuracy because the area of finding is narrowed down)
        # #     div_parents = [div_parent for div_parent in best_title_candidate.parents if div_parent.name == 'div']
        # #     product_prices = self.findPrice(div_parents, True)
        # #     if len(product_prices) == 0:
        # #         product_prices = self.getPriceLowAccuracy(responseUnicode)
        # # else:
        #     #Get price (Lower accuracy because searching strings for entire page)
        # product_prices = self.getPriceLowAccuracy(responseUnicode)
        #
        # resultList = []
        # for elem in product_prices:
        #     selector, result = self.get_css_selector(elem, responseUnicode, 'price', response)
        #     resultList.append({'selector' : selector, 'result' : result})
        # item['price'] = resultList
        #
        # # # Get Spec
        # # selector, result = self.get_css_selector(self.getSpec(soup), response, 'specs')
        # # item['specs'] = {'selector' : selector, 'result' : result}
        #
        # soup2 = BeautifulSoup(responseUnicode.decode('utf-8'), 'html5lib')
        # for elem in soup2.findAll(['script', 'style']):
        #     elem.extract()
        # comments = soup2.findAll(text=lambda text:isinstance(text, Comment))
        # [comment.extract() for comment in comments]
        #
        # filteredData = self.removeFooter(soup2)
        # sellDateCandidates = []
        # manufacturerCandidates = []
        #
        # for aList in filteredData:
        #     manufacturerCandidate = aList.find_all(string=re.compile(u'メーカー'))
        #     brandCandidate = aList.find_all(string=re.compile(u'ブランド'))
        #     sellDateCandidate = aList.find_all(string=re.compile(u'発売日'))
        #     if manufacturerCandidate:
        #         manufacturerCandidates.extend(manufacturerCandidate)
        #     if brandCandidate:
        #         manufacturerCandidates.extend(brandCandidate)
        #     if sellDateCandidate:
        #         sellDateCandidates.extend(sellDateCandidate)
        #
        # #Get manufacturer
        # manufacturerCandidates = list(OrderedDict.fromkeys(manufacturerCandidates))
        # manufacturer = self.getMega(manufacturerCandidates)
        # sorted_manufacturer = sorted(manufacturer.items(), key=operator.itemgetter(1), reverse=True)
        # if len(manufacturerCandidates) != 0:
        #     resultList = []
        #     for manufacturer_candidate in sorted_manufacturer:
        #         selector, result = self.get_css_selector(manufacturer_candidate[0], responseUnicode, 'manufacturer', response)
        #         resultList.append({'selector' : selector, 'result' : result})
        #     item['manufacturer'] = resultList
        # else:
        #     selector, result = self.get_css_selector("-", responseUnicode, 'manufacturer', response)
        #     item['manufacturer'] = {'selector' : selector, 'result' : result}
        #
        # #For yodobashi (Yodobashi use '販売開始日' instead)
        # # if len(sellDateCandidates) == 0:
        # #     for aList in filteredData:
        # #         sellDateCandidate = aList.find_all(string=re.compile(u'販売開始日'))
        # #         if sellDateCandidate:
        # #             sellDateCandidates.extend(sellDateCandidate)
        #
        # #Get 発売日
        # sellDateCandidates = list(OrderedDict.fromkeys(sellDateCandidates))
        # if len(sellDateCandidates) != 0:
        #     resultList = []
        #     for sellDateCandidate in sellDateCandidates:
        #         selector, result = self.get_css_selector(self.getSellDate(sellDateCandidate), responseUnicode, 'date_of_issue', response)
        #         resultList.append({'selector' : selector, 'result' : result})
        #     item['date_of_issue'] = resultList
        # else:
        #     selector, result = self.get_css_selector("-", responseUnicode, 'date_of_issue', response)
        #     item['date_of_issue'] = {'selector' : selector, 'result' : result}
        #
        yield item
