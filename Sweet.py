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
from utils import DEF_BROWSER
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self):
        self.source = 'Sweet'
        self.site = 'http://sweet-tv.net'
        self.link = f'ext:{self.source}:{self.site}'
        self.listURL = f'{self.site}/dlya-vzroslykh.html'
        self.headers = {'User-Agent': DEF_BROWSER,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Referer': self.site}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        RET_STATUS = False
        group = 'Общие'
        http = utils.getURL(self.site, referer=self.site)
        soup = BeautifulSoup(http, "html.parser")

        for tag in soup.find_all('td', {'style': 'text-align: center; padding: 10px;'}):
            try:
                url = self.link + tag.find('a').get('href')
                img = self.site + tag.find('img').get('src')
                title = tag.find('img').get('title')
                title = title.replace("Смотреть", '').replace("онлайн", '').strip()
                ids = utils.title_to_crc32(title)
                LL.append((ids, title, group, url, img))
            except: pass

        group = 'Эротика'
        http = utils.getURL(self.listURL, referer=self.site)
        soup = BeautifulSoup(http, "html.parser")

        for tag in soup.find_all('td', {'style': 'text-align: center; padding: 10px;'}):
            try:
                url = self.link + tag.find('a').get('href')
                img = self.site + tag.find('img').get('src')
                title = tag.find('img').get('title')
                title = title.replace("Смотреть", '').replace("онлайн", '').strip()
                ids = utils.title_to_crc32(title)
                LL.append((ids, title, group, url, img))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        http = utils.getURL(lnk, referer=self.site)
        soup = BeautifulSoup(http, "html.parser")
        php_lnk = soup.find('iframe').get('src')
        if "ok.ru" in php_lnk: return ''
        http = utils.getURL(php_lnk, referer=lnk)
        url = utils.mfind(http, '?file=', '" type')
        if url.startswith('http'):
            if ' or ' in url:
                head,sep,tail = url.partition(' or ')
                url = head
            return url
        else:
            return ''
