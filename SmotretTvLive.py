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
        self.site = 'http://smotret-tv.live'
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
        tags = soup.find('ul', {'class': "nav-child unstyled small"})
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

            for tag in soup.find_all('td', attrs={"style": "text-align: center;"} ):
                href = None
                try: href = f"{self.site}{tag.find('a').get('href')}"
                except: continue
                if not href: continue

                http = utils.getURL(href, headers=self.headers)
                if not '<iframe allowfullscreen="" name="frame" src="' in http: continue
                iframe = utils.mfind(http, '<iframe allowfullscreen="" name="frame" src="', '.php"')
                if not "cdntvmedia.com" in iframe: continue

                url = f"ext:{self.source}:{iframe}.php"
                try:
                    img = f"{self.site}{tag.find('img').get('src')}"
                    title = tag.find('img').get('title')
                    title = title.replace('прямой эфир', '').replace('онлайн', '').strip()
                    ids = utils.title_to_crc32(title)
                    LL.append((ids, title, grp[0], url, img))
                except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)
            RET_STATUS = True

        return RET_STATUS

    def checkLinks(self, chDist):
        for lnk in chDist:
            try:
                ret = requests.get(lnk, verify=False, timeout=3)
                ret.raise_for_status()
                return lnk
            except:
                pass

        return ''

    def getLink(self, lnk):
        http = utils.getURL(lnk, headers=self.headers)
        url = utils.mfind(http, 'id:"player", file:"', '"});')

        if not url.startswith('http://') or not url.startswith('https://'):
            soup = BeautifulSoup(http, "html.parser")
            url = soup.find('iframe').get('src')
            if '?file=' in url:
                _, url = url.split('?file=')

        if url.startswith('http://') or url.startswith('https://'):
            if ' or ' in url:
                chDist = url.split(' or ')
                url = self.checkLinks(chDist)
            return url
        else:
            return ''
