# -*- coding: utf-8 -*-

import os, sys
import requests
from pathlib import Path

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
        self.source = Path(__file__).stem
        self.site = 'https://ukrainske.tv/'
        self.link = f'ext:{self.source}:'
        self.token = None
        self.headers = {'User-Agent': DEF_BROWSER,
                        'Referer': self.site}

    def getHeaders(self):
        return self.headers

    def getToken(self):
        http = requests.get(f"{self.site}/tv", headers=self.headers)
        self.token = utils.mfind(http.text, "'access_token': '", "',")
        return http.text

    def Channels(self):
        LL=[]
        RET_STATUS = False
        http = self.getToken()
        soup = BeautifulSoup(http, "html.parser")

        for tag in soup.find_all('div', attrs={"class": "channel", "data-islocked": ""}):
            try:
                if "radio" in tag.get('data-group'):
                    continue
                title = tag.find('img').get('alt')
                ids = utils.title_to_crc32(title)
                img = tag.find('img').get('src')
                data_ch = tag.get('data-channel')
                url = f"{self.link}https://uk.ukrainske.tv/{data_ch}/index.m3u8"
                LL.append((ids, title, 'Украина', url, img))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        if not self.token: self.getToken()
        return f"{lnk}?token={self.token}"
