#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup, Comment, element
import re
from difflib import SequenceMatcher
from collections import OrderedDict
from ecjidospider.items import *

class Ecjido2(scrapy.Spider):
    name = 'ecjido2'

    def __init__(self, url=None, *args, **kwargs):
        super(Ecjido2, self).__init__(*args, **kwargs)
        self.start_urls = [str(url)]

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def stripString(self, text):
        return ''.join(text.split())

    def get_element(self, tag):
        if len(tag.find_previous_siblings(tag.name)) > 0 or len(tag.find_next_siblings(tag.name)) > 0:
            return '%s:nth-of-type(%d)' % (tag.name, len(tag.find_previous_siblings(tag.name)) + 1)
        else:
            return '%s:nth-of-type(1)' % (tag.name)

    def get_css_selector(self, tag, response, key):
        if not isinstance(tag, basestring):
            soup2 = BeautifulSoup(response.body, 'html5lib')
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
                                selector = '#' + parent['id'] + ' ' + selector
                                break
                            else:
                                selector = self.get_element(parent) + ' ' + selector
                        else:
                            selector = self.get_element(parent) + ' ' + selector
            else:
                selector = ''
                for parent in tList[tagIndex].parents:
                    if parent.attrs.has_key('id'):
                        if not (parent['id'].replace('.', '9').isdigit()):
                            selector = '#' + parent['id'] + ' ' + selector
                            break
                        else:
                            selector = self.get_element(parent) + ' ' + selector
                    else:
                        selector = self.get_element(parent) + ' ' + selector

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
        mostSimilarTitle = '-'
        bestSimilarScore = 0
        title_candidate_list = soup.find_all('h1') + soup.find_all('h2') + soup.find_all('h3')
        if len(title_candidate_list) != 0:
            for candidate in title_candidate_list:
                currentSimilarScore = self.similar(soup.title.text, candidate.text.strip())
                currentSimilarScore += self.getTitleTypeScore(candidate.name)
                if currentSimilarScore > 0.5 and currentSimilarScore != 1:
                    if currentSimilarScore > bestSimilarScore:
                        bestSimilarScore = currentSimilarScore
                        mostSimilarTitle = candidate
        return mostSimilarTitle

    def getJANCode(self, soup):
        striped_text = self.stripString(soup.text)
        jan = re.findall(r"\D(\d{13})\D", " "+striped_text+" ")
        if len(jan) != 0:
            return soup.find(string=re.compile(jan[0])).parent
        else:
            return "-"

    def getSpec(self, soup):
        spec_list = soup.find_all(string=re.compile(u'スペック'))
        if len(spec_list) == 0:
            spec_list = soup.find_all(string=re.compile(u'仕様'))
        if len(spec_list) == 0:
            spec_list = soup.find_all(string=re.compile(u'詳細'))

        specs = '-'
        if len(spec_list) != 0:
            #Check spec candidates
            # if len(spec_list) > 1:
            #     print "a"
            # else:
            #lv2_parent = spec_list[0].find_parents()[2]
            for parent in spec_list[0].find_parents():
                if len(parent.find_all('tr')) != 0:
                    specs = parent
                    break
                if len(parent.find_all('dl')) != 0:
                    specs = parent
                    break
        if isinstance(specs, element.Tag):
            if specs.name == '[document]':
                specs = '-'
        return specs

    def getPrice(self, priceList, isTag):
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
        manufacturer = "-"

        if len(manufacturerCandidates) == 1:
            if (self.similar(u'メーカー', self.stripString(manufacturerCandidates[0])) >= 0.8):
                #If manufacturer is at the next sibling element
                manufacturerSibling = [sib for sib in manufacturerCandidates[0].parent.next_siblings if sib.string != '\n']
                if len(manufacturerSibling) != 0:
                    manufacturer = manufacturerSibling[0]
                # else:
                #     print manufacturerCandidates[0]
        elif len(manufacturerCandidates) > 1:
            bestCandidate = ""
            bestCandidateScore = 0
            for manufacturerCandidate in manufacturerCandidates:
                currentScore = self.similar(manufacturerCandidate, u'メーカー')
                if currentScore > bestCandidateScore:
                    bestCandidateScore = currentScore
                    bestCandidate = manufacturerCandidate
            if (bestCandidateScore >= 0.8):
                if len([sib.text.strip() for sib in bestCandidate.parent.next_siblings if sib.string != '\n']) != 0:
                    manufacturer = [sib for sib in bestCandidate.parent.next_siblings if sib.string != '\n'][0]

        return manufacturer

    def getSellDate(self, sellDateCandidates):
        sellDate = "-"

        if len(sellDateCandidates) == 1:
            sellDateSibling = [sib.string for sib in sellDateCandidates[0].parent.next_siblings if sib.string != '\n' and sib.string is not None]
            if len(sellDateSibling) != 0:
                sellDate = sellDateSibling[0].parent
            else:
                parentString = self.stripString(sellDateCandidates[0].parent.text)
                parentString = parentString.replace(u'年', '/').replace(u'月', '/').replace(u'日', ' ')
                # sellDate = re.search(u'\d{4}/\d{2}/\d{2}', parentString).group()
                sellDate = sellDateCandidates[0].parent
        elif len(sellDateCandidates) > 1:
            bestCandidate = ""
            bestCandidateScore = 0
            for sellDateCandidate in sellDateCandidates:
                if (urlparse(response.url).netloc == 'www.yodobashi.com'):
                    currentScore = self.similar(sellDateCandidate, u'販売開始日')
                else:
                    currentScore = self.similar(sellDateCandidate, u'発売日')
                if currentScore > bestCandidateScore:
                    bestCandidateScore = currentScore
                    bestCandidate = sellDateCandidate
            if (bestCandidateScore >= 0.6):
                bestCandidateSibling = [sib.string for sib in bestCandidate.parent.next_siblings if sib.string != '\n' and sib.string is not None]
                if len(bestCandidateSibling) != 0:
                    sellDate = bestCandidateSibling[0].parent
                    # print sellDate.parent
                else:
                    parentString = self.stripString(bestCandidate.parent.text)
                    parentString = parentString.replace(u'年', '/').replace(u'月', '/').replace(u'日', ' ')
                    # sellDate = re.search(u'\d{4}/\d{2}/\d{2}', parentString).group()
                    sellDate = sellDateCandidates[0].parent
        return sellDate

    def dataFilter(self, soup):
        divList = soup.find_all('div')
        list3 = []
        parentFilterRound = 0

        if soup.find('footer'):
            #remove <footer>
            list2 = [div for div in divList if not u'footer' in [parent.name for parent in div.parents]]
        elif soup.find(id='footer'):
            #remove div id'footer'
            list2 = [div for div in divList if not u'footer' in [parent.attrs['id'] for parent in div.parents if u'id' in parent.attrs.keys()]]
            list2.remove(soup.find(id='footer'))
        else:
            list2 = divList

        #delete all child div in each div
        for div in list2:
            for elem in div.find_all('div'):
                elem.extract()

        for i in range (0, len(list2)):
            links = len(list2[i].find_all('a'))
            chars = len(self.stripString(list2[i].text))
            parents = len([parent.name for parent in list2[i].parents if parent.name == u'div'])
            contents = len([child.name for child in list2[i].contents if child != '\n' and child.name is not None])
            pics = len(list2[i].find_all('img'))
            if chars == 0 or contents == 0 or links > 10:
                list3.append(list2[i])
            # print ('list %d has %d links\t %d chars\t %d div parents\t %d childs %d pics' % (i+1, links, chars, parents, contents, pics))

        for aList in list3:
            list2.remove(aList)

        return list2

    def parse(self, response):
        #Item for handling json export
        item = Ecjido2Item()
        item['price'] = []

        #Create a BeautifulSoup of the website
        soup = BeautifulSoup(response.body, 'html5lib')
        #Remove <script> and comment tags
        for elem in soup.findAll(['script', 'style']):
            elem.extract()
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]

        #Rearrange received html tags
        soup.prettify().strip()

        #Get title
        title_tag = self.findTitle(soup)
        selector, result = self.get_css_selector(title_tag, response, 'title')
        item['title'] = {'selector' : selector, 'result' : result}

        #Get Price
        product_prices = []
        if not isinstance(title_tag, basestring):
            #Get price (Higher accuracy because the area of finding is narrowed down)
            div_parents = [div_parent for div_parent in title_tag.parents if div_parent.name == 'div']
            product_prices = self.getPrice(div_parents, True)
        else:
            #Get price (Lower accuracy because searching strings for entire page)
            soup2 = BeautifulSoup(response.body, 'html5lib')
            for elem in soup2.findAll(['script', 'style']):
                elem.extract()
            comments = soup2.findAll(text=lambda text:isinstance(text, Comment))
            [comment.extract() for comment in comments]

            filteredData = self.dataFilter(soup2)
            product_prices = self.getPrice(filteredData, False)

        for elem in product_prices:
            selector, result = self.get_css_selector(elem, response, 'price')
            item['price'].append({'selector' : selector, 'result' : result})

        #Get Spec
        # selector, result = self.get_css_selector(self.getSpec(soup), response, 'specs')
        # item['specs'] = {'selector' : selector, 'result' : result}

        #Get JAN
        selector, result = self.get_css_selector(self.getJANCode(soup), response, 'jan_code')
        item['jan_code'] = {'selector' : selector, 'result' : result}

        filteredData = self.dataFilter(soup)
        sellDateCandidates = []
        manufacturerCandidates = []

        for aList in filteredData:
            manufacturerCandidate = aList.find_all(string=re.compile(u'メーカー'))
            sellDateCandidate = aList.find_all(string=re.compile(u'発売日'))
            if manufacturerCandidate:
                manufacturerCandidates.extend(manufacturerCandidate)
            if sellDateCandidate:
                sellDateCandidates.extend(sellDateCandidate)

        #Get manufacturer
        selector, result = self.get_css_selector(self.getMega(manufacturerCandidates), response, 'manufacturer')
        item['manufacturer'] = {'selector' : selector, 'result' : result}

        #For yodobashi (Yodobashi use '販売開始日' instead)
        if len(sellDateCandidates) == 0:
            for aList in filteredData:
                sellDateCandidate = aList.find_all(string=re.compile(u'販売開始日'))
                if sellDateCandidate:
                    sellDateCandidates.extend(sellDateCandidate)

        #Get 発売日
        selector, result = self.get_css_selector(self.getSellDate(sellDateCandidates), response, 'date_of_issue')
        item['date_of_issue'] = {'selector' : selector, 'result' : result}

        # yield item
