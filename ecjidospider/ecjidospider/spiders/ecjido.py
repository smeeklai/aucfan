#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup, Comment
import re
from difflib import SequenceMatcher
from ecjidospider.items import *

class Ecjido(scrapy.Spider):
    name = "ecjido"
    start_urls = ["http://www.yodobashi.com/%E3%83%AD%E3%83%AC%E3%83%83%E3%82%AF%E3%82%B9-ROLEX-214270-%E3%82%A8%E3%82%AF%E3%82%B9%E3%83%97%E3%83%AD%E3%83%BC%E3%83%A9%E3%83%BC/pd/100000001001319012/"]

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def stripString(self, text):
        return ''.join(text.split())

    def getTitle(self, htmlTitle, strings):
        mostSimilarTitle = ""
        bestSimilarScore = 0
        for string in strings:
            currentSimilarScore = self.similar(htmlTitle, string)
            if currentSimilarScore > 0.3 and currentSimilarScore != 1:
                if currentSimilarScore > bestSimilarScore:
                    bestSimilarScore = currentSimilarScore
                    mostSimilarTitle = string
        self.logger.info('mostSimilarTitle: %s' % mostSimilarTitle)
        title =""
        diff = 0
        try:
            for i in range(0, len(htmlTitle)):
                if mostSimilarTitle[i-diff] == htmlTitle[i]:
                    title += mostSimilarTitle[i-diff]
                else:
                    diff += 1
        except:
            None
        return title

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
            chars = len(list2[i].text.replace(" ", "").replace("\n", ""))
            parents = len([parent.name for parent in list2[i].parents if parent.name == u'div'])
            contents = len([child.name for child in list2[i].contents if child != '\n' and child.name is not None])
            pics = len(list2[i].find_all('img'))
            if chars == 0 or contents == 0 or links > 8:
                list3.append(list2[i])
            # print ('list %d has %d links\t %d chars\t %d div parents\t %d childs %d pics' % (i+1, links, chars, parents, contents, pics))

        for aList in list3:
            list2.remove(aList)

        # while True:
        #     list2 = [a for a in list2 if a.parent.attrs is not list2[list2.index(a)-1].attrs]
        #     if parentFilterRound != 0:
        #         if len(list2) == parentFilterRound:
        #             break
        #     parentFilterRound = len(list2)
        #
        # for i in range (0, len(list2)):
        #     links = len(list2[i].find_all('a'))
        #     chars = len(list2[i].text.replace(" ", "").replace("\n", ""))
        #     parents = len([parent.name for parent in list2[i].parents if parent.name == u'div'])
        #     contents = len([child.name for child in list2[i].contents if child != '\n' and child.name is not None])
        #     pics = len(list2[i].find_all('img'))
        #     # if chars == 0 or parents == 0 or chars <= 30:
        #     #     list3.append(list2[i])
        #     # print ('list %d has %d links\t %d chars\t %d div parents\t %d childs %d pics' % (i+1, links, chars, parents, contents, pics))
        #
        # # print "price: " + ''.join(soup.find(string=re.compile(u'円')).split())
        #
        # return [aList for aList in list2 if len(aList.find_all('a')) != 0 or len(aList.find_all('a')) < 15]
        return list2

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        soup.prettify()
        #Remove all commment in html
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]

        #Remove all <script> in html
        for elem in soup.findAll(['script', 'style']):
            elem.extract()

        soup.prettify().strip()

        #Get title
        title = self.getTitle(soup.title.text, soup.body.stripped_strings)
        self.logger.info(title)

        #Get price
        price = re.search(u"￥\s?(\d+,?\d+)", soup.text)
        if price is not None:
            price = price.group(1)
        else:
            price = re.search(u"\s?(\d+,?\d+)円", soup.text)
            if price is not None:
                price = price.group(1)
            else:
                price = "-"
        print "price: " + price

        #Get specs
        spec_list = soup.find_all(string=re.compile(u'スペック'))
        if len(spec_list) == 0:
            spec_list = soup.find_all(string=re.compile(u'仕様'))
        if len(spec_list) == 0:
            spec_list = soup.find_all(string=re.compile(u'詳細'))

        if len(spec_list) != 0:
            #Check spec candidates
            # if len(spec_list) > 1:
            #     print "a"
            # else:
            #lv2_parent = spec_list[0].find_parents()[2]
            specDataList = []
            for parent in spec_list[0].find_parents():
                if len(parent.find_all('tr')) != 0:
                    specDataList = parent.find_all('tr')
                    break
                if len(parent.find_all('dl')) != 0:
                    specDataList = parent.find_all('dl')
                    break
                if len(specDataList) != 0:
                    break
            specs = ""
            for tr in specDataList:
                for string in tr.strings:
                    if string != '\n' and string is not None:
                        if string != "":
                            specs += string.strip()
                            self.logger.info('sepc: ' + string.strip())
                        else:
                            self.logger.info('spec: ' + '-')
        else:
            self.logger.error('Cannot find spec')

        filteredData = self.dataFilter(soup)
        manufacturerCandidates = []
        janCandidates = []
        sellDateCandidates = []
        manufacturer = "-"
        jan = "-"
        sellDate ="-"

        for aList in filteredData:
            manufacturerCandidate = aList.find_all(string=re.compile(u'メーカー'))
            janCandidate = aList.find_all(string=re.compile(u'JAN'))
            sellDateCandidate = aList.find_all(string=re.compile(u'発売日'))
            if manufacturerCandidate:
                manufacturerCandidates.extend(manufacturerCandidate)
            if janCandidate:
                janCandidates.extend(janCandidate)
            if sellDateCandidate:
                sellDateCandidates.extend(sellDateCandidate)

        #For yodobashi (Yodobashi use '販売開始日' instead)
        if len(sellDateCandidates) == 0:
            for aList in filteredData:
                sellDateCandidate = aList.find_all(string=re.compile(u'販売開始日'))
                if sellDateCandidate:
                    sellDateCandidates.extend(sellDateCandidate)

        if len(manufacturerCandidates) == 1:
            if (self.similar(u'メーカー', ''.join(manufacturerCandidates[0].split())) >= 0.8):
                #If manufacturer is at the next sibling element
                manufacturerSibling = [sib.text.strip() for sib in manufacturerCandidates[0].parent.next_siblings if sib.string != '\n']
                if len(manufacturerSibling) != 0:
                    manufacturer = manufacturerSibling[0]
        else:
            bestCandidate = ""
            bestCandidateScore = 0
            for manufacturerCandidate in manufacturerCandidates:
                currentScore = self.similar(manufacturerCandidate, u'メーカー')
                if currentScore > bestCandidateScore:
                    bestCandidateScore = currentScore
                    bestCandidate = manufacturerCandidate
            if (bestCandidateScore >= 0.8):
                if len([sib.text.strip() for sib in bestCandidate.parent.next_siblings if sib.string != '\n']) != 0:
                    manufacturer = [sib.text.strip() for sib in bestCandidate.parent.next_siblings if sib.string != '\n'][0]

        if len(janCandidates) == 1:
            janSibling = [sib.string for sib in janCandidates[0].parent.next_siblings if sib.string != '\n']
            if len(janSibling) != 0:
                jan = janSibling[0]
            else:
                parentString = ''.join(janCandidates[0].parent.text.split())
                jan = re.findall(u'\D(\d{13})\D', " "+parentString+" ")[0]
        else:
            #Evaluate and get the best candidate
            bestCandidate = ""
            bestCandidateScore = 0
            for janCandidate in janCandidates:
                currentScore = self.similar(janCandidate, u'JAN')
                if currentScore > bestCandidateScore:
                    bestCandidateScore = currentScore
                    bestCandidate = janCandidate
            #Check weather the best candidate is good enough or not
            if (bestCandidateScore >= 0.6):
                bestCandidateSibling = [sib.string for sib in bestCandidate.parent.next_siblings if sib.string != '\n']
                if len(bestCandidateSibling) != 0:
                    jan = bestCandidateSibling[0]
                else:
                    parentString = ''.join(bestCandidate.parent.text.split())
                    parentString = parentString.replace(u'年', '/').replace(u'月', '/').replace(u'日', ' ')
                    sellDate = re.search(u'\d{4}/\d{2}/\d{2}', parentString).group()

        if len(sellDateCandidates) == 1:
            sellDateSibling = [sib.string for sib in sellDateCandidates[0].parent.next_siblings if sib.string != '\n' and sib.string is not None]
            if len(sellDateSibling) != 0:
                sellDate = sellDateSibling[0]
            else:
                parentString = ''.join(sellDateCandidates[0].parent.text.split())
                parentString = parentString.replace(u'年', '/').replace(u'月', '/').replace(u'日', ' ')
                sellDate = re.search(u'\d{4}/\d{2}/\d{2}', parentString).group()
        else:
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
                    sellDate = bestCandidateSibling[0]
                else:
                    parentString = ''.join(bestCandidate.parent.text.split())
                    parentString = parentString.replace(u'年', '/').replace(u'月', '/').replace(u'日', ' ')
                    sellDate = re.search(u'\d{4}/\d{2}/\d{2}', parentString).group()

        self.logger.info('manufacturer: %s Jan: %s sellDate: %s' % (manufacturer, jan, sellDate))
        print type(manufacturer)
        print type(sellDate)

        # Export to JSON data
        # item = EcjidospiderItem()
        # item['title'] = str(title.encode('utf-8'))
        # item['price'] = str(price)
        # item['jan_code'] = str(jan)
        # item['date_of_issue'] = str(sellDate)
        # item['manufacturer'] = str(manufacturer)
        # item['specs'] = str(specs)
        # yield item
