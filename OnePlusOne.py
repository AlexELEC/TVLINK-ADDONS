# -*- coding: utf-8 -*-

import os, sys, re
import requests
from pathlib import Path

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
        self.source = Path(__file__).stem
        self.site = 'https://1plus1.video/tvguide'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': DEF_BROWSER}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        RET_STATUS = False
        http = requests.get(self.site, headers=self.headers)
        soup = BeautifulSoup(http.text, "html.parser")

        for tag in soup.find_all('div', attrs={"class": "tvguide-channel-logo"} ):
            try:
                url = f"{self.link}{tag.find('a').get('href')}"
                img = tag.find('img').get('src')
                title = tag.find('img').get('title')
                ids = utils.title_to_crc32(title)
                LL.append((ids, title, 'Украина', url, img))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        return lnk
