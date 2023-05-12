# -*- coding: utf-8 -*-

import os, sys, re
import requests

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
        self.source = 'SmotriOnly'
        self.site = 'http://smotrite.only-tv.org'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109) Gecko/20100101 Firefox/112.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Referer': self.site}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        http = requests.get(self.site, headers=self.headers)
        soup = BeautifulSoup(http.text, "html.parser")

        for tag in soup.find_all('td', attrs={"style": "text-align: center; position: relative;"} ):
            href = None
            try: href = self.site + tag.find('a').get('href')
            except: continue
            if not href: continue

            http = utils.getURL(href, headers=self.headers, timeout=5)
            iframe = re.search(r'http://cdntvpotok\.com/.*\.php', http)
            if not iframe: continue
            iframe = iframe.group(0)

            url = f"{self.link}{iframe}"
            try:
                img = self.site + tag.find('img').get('src')
                title = tag.find('img').get('title')
                title = title.replace('смотреть онлайн', '').strip()
                ids = utils.title_to_crc32(title)
                LL.append((ids, title, self.source, url, img))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

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
