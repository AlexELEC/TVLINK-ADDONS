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
        self.source = 'TelikLive'
        self.site = 'http://telik.live'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': DEF_BROWSER,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Referer': 'http://telik.live/'}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        RET_STATUS = False
        http = utils.getURL(self.site, headers=self.headers)
        soup = BeautifulSoup(http, "html.parser")

        for tag in soup.find_all('td', attrs={"style": "text-align: center;"} ):
            href = None
            try: href = self.site + tag.find('a').get('href')
            except: continue
            if not href: continue

            http = utils.getURL(href, headers=self.headers)
            if not '<iframe allowfullscreen="" name="frame" src="' in http: continue
            iframe = utils.mfind(http, '<iframe allowfullscreen="" name="frame" src="', '.php"')
            if not "cdntvmedia.com" in iframe: continue

            url = f"{self.link}{iframe}.php"
            try:
                img = self.site + tag.find('img').get('src')
                title = tag.find('img').get('title')
                title = title.replace('прямой эфир', '').strip()
                ids = utils.title_to_crc32(title)
                LL.append((ids, title, self.source, url, img))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        http = utils.getURL(lnk, headers=self.headers)
        url = utils.mfind(http, 'id:"player", file:"', '"});')
        if url.startswith('http'):
            if ' or ' in url:
                head,sep,tail = url.partition(' or ')
                url = head
            return url
        else:
            return ''



