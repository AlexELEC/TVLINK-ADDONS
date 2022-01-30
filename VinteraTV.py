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
        self.source = 'VinteraTV'
        self.site = 'http://xml.vintera.tv'
        self.link = f'ext:{self.source}:'
        self.listURL = f'{self.site}/android_v1117/premium/packages_ru.xml'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.98 Mobile Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Referer': self.site}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        http = utils.getURL(self.listURL, headers=self.headers)
        soup = BeautifulSoup(http, "html.parser")

        for tag in soup.find_all("tracklist"):
            try:
                titles = tag.find_all('title')
                links = tag.find_all('location')
                groups = tag.find_all('category')

                for i in range(0, len(titles)):
                    title = titles[i].get_text()
                    lnk = links[i].get_text()
                    group = groups[i].get_text()
                    if title and 'http' in lnk:
                        ids = utils.title_to_crc32(title)
                        url = f'{self.link}{lnk}'
                        LL.append((ids, title, group, url, ''))
                    else: continue
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def getLink(self, lnk):
        return lnk
