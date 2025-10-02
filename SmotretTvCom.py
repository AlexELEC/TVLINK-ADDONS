# -*- coding: utf-8 -*-

import os, sys
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
        self.site = 'https://smotrettv.com'
        self.headers = {'User-Agent': DEF_BROWSER,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Referer': self.site}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        RET_STATUS = False

        # get groups
        http = utils.getURL(self.site, headers=self.headers)
        soup = BeautifulSoup(http, "html.parser")
        tags = soup.find('ul', {'class': "menu"})
        GROUPS = []

        for tag in tags.find_all('a'):
            try:
                group_url = f"{self.site}{tag.get('href')}"
                if "/tv/" in group_url:
                    group = tag.text.strip()
                    GROUPS.append((group, group_url))
            except:
                pass

        # get additional groups page
        GROUPS_ADD = []
        for grp in GROUPS:
            http = utils.getURL(grp[1], headers=self.headers)
            soup = BeautifulSoup(http, "html.parser")
            tags = soup.find('div', {'class': "pagination__pages d-flex jc-center"})

            if tags:
                for tag in tags.find_all('a'):
                    group_url = f"{tag.get('href')}"
                    GROUPS_ADD.append((grp[0], group_url))

        if GROUPS_ADD:
            GROUPS.extend(GROUPS_ADD)

        # get channels
        for grp in GROUPS:
            http = utils.getURL(grp[1], headers=self.headers)
            soup = BeautifulSoup(http, "html.parser")

            for tag in soup.find_all('a', {'class': "thumb d-flex fd-column grid-item"} ):
                try:
                    url = f"ext:{self.source}:{tag.get('href')}"
                    img = f"{self.site}{tag.find('img').get('src')}"
                    title = tag.find('div', {'class': "thumb__title ws-nowrap"}).text
                    ids = utils.title_to_crc32(title)
                    LL.append((ids, title, grp[0], url, img))
                except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        http = utils.getURL(lnk, headers=self.headers)
        url = utils.mfind(http, 'id:"player", file:"', '"});')

        if url.startswith('http://') or url.startswith('https://'):
            if "&remote=" in url:
                url = url.split("&remote=", 1)[0]
            return url
        else:
            return ''
