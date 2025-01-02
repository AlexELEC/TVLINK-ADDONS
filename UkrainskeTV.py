# -*- coding: utf-8 -*-

import os, sys
import requests, time
from pathlib import Path
from base64 import b64decode

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

TOKEN = None
TOKEN_TIME = 0

def getDATA():
    http = requests.get("https://ukrainske.tv/tv", headers={'User-Agent': DEF_BROWSER})
    token = utils.mfind(http.text, "'access_token': '", "',")
    access_cut = token.split('.')
    access_part = ''
    for i in range( len(access_cut) - 1 ):
        access_part += access_cut[i]
    access_part = access_part + '=' * (4 - len(access_part) % 4) if len(access_part) % 4 != 0 else access_part
    time_exp = b64decode(access_part).decode('utf-8')
    time_exp = utils.mfind(time_exp, '"exp":', ',"device"')
    return token, int(time_exp), http.text


class Scraper:
    def __init__(self):
        self.source = Path(__file__).stem
        self.site = 'https://ukrainske.tv/'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': DEF_BROWSER,
                        'Referer': self.site}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        global TOKEN
        global TOKEN_TIME
        LL=[]
        RET_STATUS = False
        TOKEN, TOKEN_TIME, http = getDATA()
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
        global TOKEN
        global TOKEN_TIME
        if not TOKEN or int(time.time()) > TOKEN_TIME - 600:
            TOKEN, TOKEN_TIME, _ = getDATA()
        return f"{lnk}?token={TOKEN}"
