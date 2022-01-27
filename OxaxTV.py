# -*- coding: utf-8 -*-

import os, sys
from base64 import b64decode

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
        self.source = 'OxaxTV'
        self.site = 'http://oxax.tv'
        self.chlist = f'{self.site}/spisok'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Referer': self.site}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL = []
        http = utils.getURL(self.chlist, headers=self.headers)
        soup = BeautifulSoup(http, "html.parser")

        for tag in soup.find_all('div', {'class': 'tv_sp'}):
            try:
                title = tag.get('title')
                lnk = tag.find('a').get('href')
                url = f"{self.link}{self.site}{lnk}"
                ids = utils.title_to_crc32(title)
                LL.append((ids, title, "Эротика", url, ""))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def decodeLnk(self, code):
        replica = ['//RlZGVkZW',
                   '//UlJSUlJS',
                   '//NTU1U1NT',
                   '//VFRUVFRU',
                   '//RERERERE']
        for rep in replica:
            code = code.replace(rep, '')
        for rep in replica:
            code = code.replace(rep, '')
        return b64decode(code).decode('utf-8')

    def getLink(self, lnk):
        http = utils.getURL(lnk, headers=self.headers)
        kes = utils.mfind(http, "{kes:'", "'},function")
        http = utils.getURL(f"{self.site}/pley?kes={kes}", headers=self.headers)
        code = utils.mfind(http, 'file:"#2', '"});')
        return self.decodeLnk(code)
