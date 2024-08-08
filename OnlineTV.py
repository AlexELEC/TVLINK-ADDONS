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
from utils import DEF_BROWSER
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self):
        self.source = 'OnlineTV'
        self.site = 'https://online-tv.live'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': DEF_BROWSER,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Referer': self.site}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        http = requests.get(f"{self.site}/kategorii.html", headers=self.headers)
        soup = BeautifulSoup(http.text, "html.parser")
        gr_tags = soup.find('ul', {'class': "nav-child unstyled small"})

        for gr_tag in gr_tags.find_all('a'):
            try:
                gr_title = gr_tag.text.strip()
                gr_url = f"{self.site}{gr_tag.get('href')}"

                http = requests.get(gr_url, headers=self.headers)
                soup = BeautifulSoup(http.text, "html.parser")

                for tag in soup.find_all( 'td', attrs={"style": "text-align: center;"} ):
                    url = f"{self.link}{self.site}{tag.find('a').get('href')}"
                    img = f"{self.site}{tag.find('img').get('src')}"
                    title = tag.find('img').get('title')
                    title = title.replace('смотреть онлайн', '').strip()
                    ids = utils.title_to_crc32(title)
                    LL.append((ids, title, gr_title, url, img))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def getLink(self, lnk):
        http = utils.getURL(lnk, headers=self.headers, timeout=5)
        iframe = re.search(r'https://cdniptvpotok\.com/.*\.php', http)
        if not iframe: return ''
        url = iframe.group(0)

        http = utils.getURL(url, headers=self.headers)
        url = utils.mfind(http, 'id:"player", file:"', '"});')
        if "tvcdnpotok.com" in url:
            if ' or ' in url:
                head,sep,tail = url.partition(' or ')
                if "tvcdnpotok.com" in head:
                    url = head
                else:
                    url = tail
            return url
        else:
            return ''
