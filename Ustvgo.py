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
        self.source = 'Ustvgo'
        self.site = 'https://ustvgo.tv'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Referer': self.site}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL = []
        http = utils.getURL(self.site, headers=self.headers)
        soup = BeautifulSoup(http, "html.parser")
        tags = soup.find('div', {'class': "entry-content clearfix"})

        for tag in tags.find_all('a'):
            try:
                title = tag.text.strip()
                ids = utils.title_to_crc32(title)
                url = self.link + tag.get('href')
                LL.append((ids, title, self.source, url, ""))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def getLink(self, lnk):
        http = utils.getURL(lnk, headers=self.headers)
        php_lnk = utils.mfind(http, "iframe src='", "' allowfullscreen")
        http = utils.getURL(f"{self.site}{php_lnk}", headers=self.headers)
        url = utils.mfind(http, "hls_src='", "';")
        if not url.startswith("http"): return ""
        return url
