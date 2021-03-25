# -*- coding: utf-8 -*-

import os, sys

root_dir = os.path.dirname(sys.argv[0])
libs_dir = os.path.join(root_dir, 'libs')
ssv_file = os.path.join(libs_dir, 'soupsieve.whl')
bs4_file = os.path.join(libs_dir, 'beautifulsoup.whl')

sys.path.append(root_dir)
sys.path.append(libs_dir)
sys.path.insert(0, ssv_file)
sys.path.insert(0, bs4_file)

import utils
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self):
        self.source = 'Sweet'
        self.site = 'http://sweet-tv.net'
        self.link = 'ext:{0}:{1}'.format(self.source, self.site)
        self.listURL = '{}/dlya-vzroslykh.html'.format(self.site)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Referer': self.site}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]

        group = 'Общие'
        http = utils.getURL(self.site, referer=self.site)
        soup = BeautifulSoup(http, "html.parser")

        for tag in soup.find_all('td', {'style': 'text-align: center; padding: 10px;'}):
            try:
                # url = 'ext:Sweet:http://sweet-tv.net/istoriya.html'
                url = self.link + tag.find('a').get('href')
                img = self.site + tag.find('img').get('src')
                title = tag.find('a').text
                title = title.strip()
                # ids = chID
                ids = utils.title_to_crc32(title)
                # LL = ( (0-chID, 1-chTitle, 2-chGroup, 3-chUrl, 4-chLogo), ...)
                LL.append((ids, title, group, url, img))
            except: pass

        group = 'Эротика'
        http = utils.getURL(self.listURL, referer=self.site)
        soup = BeautifulSoup(http, "html.parser")

        for tag in soup.find_all('td', {'style': 'text-align: center; padding: 10px;'}):
            try:
                url = self.link + tag.find('a').get('href')
                img = self.site + tag.find('img').get('src')
                title = tag.find('a').text
                title = title.strip()
                ids = utils.title_to_crc32(title)
                LL.append((ids, title, group, url, img))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def getLink(self, lnk):
        http = utils.getURL(lnk, referer=self.site)
        soup = BeautifulSoup(http, "html.parser")
        php_lnk = soup.find('iframe').get('src')
        http = utils.getURL(php_lnk, referer=lnk)
        url = utils.mfind(http, '?file=', '" type')
        # url = 'http://50.7.222.90:8081/istoriya/index.m3u8?wmsAuthSign=e5adc493539c70c64ec9b3c0b6c3b73e-1616704350-89i84i08i212'
        return url
