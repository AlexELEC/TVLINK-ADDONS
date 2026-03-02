# -*- coding: utf-8 -*-

import os, sys, re
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
from base64 import b64decode


class Scraper:
    def __init__(self):
        self.source = Path(__file__).stem
        self.site = 'http://tv-online.top'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': DEF_BROWSER}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        RET_STATUS = False

        http = requests.get(self.site, headers=self.headers)
        soup = BeautifulSoup(http.text, "html.parser")
        gr_tags = soup.find('div', {'class': "container"})

        for group in gr_tags.select('.container > div'):
            try:
                gr_title = group.get_text(strip=True)
                ul = group.find_next_sibling('ul')
                if ul:
                    for li in ul.find_all('li'):
                        title = li.find('a').get('title')
                        url = f"{self.link}{self.site}{li.find('a').get('href')}"
                        img = f"{self.site}{li.find('img').get('src')}"
                        ids = utils.title_to_crc32(title)
                        LL.append((ids, title, gr_title, url, img))
            except:
                pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        try:
            http = requests.get(lnk, headers=self.headers)
            soup = BeautifulSoup(http.text, "html.parser")
            script_tag = soup.find('script', string=re.compile(r'Playerjs'))
            if script_tag:
                match = re.search(r'file:\s*custom\("([^"]+)"\)', script_tag.string)
                if match:
                    encoded_str = match.group(1)
                    url = b64decode(encoded_str).decode('utf-8')
                    return url
        except:
            pass

        return ''
