# -*- coding: utf-8 -*-

import os, sys
from pathlib import Path
from urllib.parse import urlparse

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
        self.site = 'https://smotret-online.tv'
        self.headers = {'User-Agent': DEF_BROWSER,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Referer': self.site}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        RET_STATUS = False

        http = utils.getURL(self.site, headers=self.headers)
        soup = BeautifulSoup(http, "html.parser")

        # get groups
        tags = soup.find('div', {'class': "dropdown-menu"})
        GROUPS = []

        for tag in tags.find_all('a'):
            try:
                group = tag.text.strip()
                group_url = f"{self.site}{tag.get('href')}"
                GROUPS.append((group, group_url))
            except:
                pass

        # get channels
        for grp in GROUPS:
            http = utils.getURL(grp[1], headers=self.headers)
            soup = BeautifulSoup(http, "html.parser")

            for tag in soup.find_all('div', {'class': "tv-schedule"} ):
                try:
                    title = tag.get('data-channel-id')
                    href = tag.get('data-link')
                    img = tag.get('data-logo')

                    http = utils.getURL(href, headers=self.headers)
                    soup = BeautifulSoup(http, "html.parser")

                    player = soup.find('div', {'class': "player"})
                    src_url = player.find('iframe').get('src')
                    url = f"ext:{self.source}:{self.site}{src_url}"
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
        soup = BeautifulSoup(http, "html.parser")
        src_url = soup.find('iframe').get('src')
        url = urlparse(src_url).query.replace('file=', '')

        if url.startswith('http'):
            return url
        else:
            return ''
