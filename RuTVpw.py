# -*- coding: utf-8 -*-

import os, sys, json

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
        self.source = 'RuTVpw'
        self.link = f'ext:{self.source}:'
        self.site = 'http://rutv.pw'
        self.headers = {'User-Agent': DEF_BROWSER}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        RET_STATUS = False
        http = utils.getURL(self.site, headers=self.headers)
        soup = BeautifulSoup(http, "html.parser")

        for tag in soup.find_all('li'):
            try:
                href = tag.find('a').get('href')
                title = tag.find('h3').text.strip()
                ids = utils.title_to_crc32(title)
                url = f"{self.link}{self.site}{href}"
                img = f"{self.site}/imgs{href}.jpg"
                LL.append((ids, title, self.source, url, img))
            except:
                pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        http = utils.getURL(lnk, headers=self.headers)
        url = utils.mfind(http, 'id:"player", file:"', '", autoplay:')
        if url.startswith('http'):
            if ' or ' in url:
                head,sep,tail = url.partition(' or ')
                url = head
            return url
        else:
            return ''
