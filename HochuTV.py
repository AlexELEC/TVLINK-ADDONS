# -*- coding: utf-8 -*-

import os, sys

root_dir = os.path.dirname(sys.argv[0])
libs_dir = os.path.join(root_dir, 'libs')
ssv_file = os.path.join(libs_dir, 'soupsieve.whl')
bs4_file = os.path.join(libs_dir, 'beautifulsoup.whl')

if not root_dir in sys.path: sys.path.append(root_dir)
if not libs_dir in sys.path: sys.path.append(libs_dir)
if not ssv_file in sys.path: sys.path.insert(0, ssv_file)
if not bs4_file in sys.path: sys.path.insert(0, bs4_file)

import utils
from utils import DEF_BROWSER
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self):
        self.source = 'HochuTV'
        self.site = 'http://hochu.tv'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': DEF_BROWSER,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Referer': self.site}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL = []
        RET_STATUS = False
        http = utils.getURL(self.site)
        soup = BeautifulSoup(http, "html.parser")

        for tag in soup.find_all('a', {'target': "_blank"}):
            try:
                title = tag.text.strip()
                ids = utils.title_to_crc32(title)
                url = f"{self.link}{self.site}{tag.get('href')}"
                img = f"{self.site}{tag.find('img').get('src')}"
                LL.append((ids, title, "Эротика", url, img))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        http = utils.getURL(lnk)
        soup = BeautifulSoup(http, "html.parser")
        php_lnk = soup.find('iframe').get('src')
        http = utils.getURL(php_lnk, headers=self.headers)
        url = utils.mfind(http, 'file:"', '"});')
        return url
