# -*- coding: utf-8 -*-

import os, sys
import requests, time
from pathlib import Path
from base64 import b64decode

root_dir = os.path.dirname(sys.argv[0])
libs_dir = os.path.join(root_dir, 'libs')
ssv_file = os.path.join(libs_dir, 'soupsieve.whl')
bs4_file = os.path.join(libs_dir, 'beautifulsoup.whl')

if not root_dir in sys.path: sys.path.append(root_dir)
if not libs_dir in sys.path: sys.path.append(libs_dir)
if not ssv_file in sys.path: sys.path.insert(0, ssv_file)
if not bs4_file in sys.path: sys.path.insert(0, bs4_file)

import utils
from utils import logger, DEF_BROWSER
from bs4 import BeautifulSoup

SOURCE = Path(__file__).stem
API_URL = 'https://ukrainske.tv/'

HEADERS = {'User-Agent': DEF_BROWSER,
           'Accept': '*/*',
           'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
           'Connection': 'keep-alive',
           'Referer': API_URL,
           }

def getDATA(bData=False):
    http = requests.get(f"{API_URL}tv", headers=HEADERS)
    token = utils.mfind(http.text, "'access_token': '", "',")
    access_cut = token.split('.')
    access_part = ''
    for i in range( len(access_cut) - 1 ):
        access_part += access_cut[i]
    access_part = access_part + '=' * (4 - len(access_part) % 4) if len(access_part) % 4 != 0 else access_part
    time_exp = b64decode(access_part).decode('utf-8')
    time_exp = utils.mfind(time_exp, '"exp":', ',"device"')
    if bData:
        return token, int(time_exp), http.text
    else:
        return token, int(time_exp)

TOKEN, TOKEN_TIME = getDATA()

class Scraper:
    def getHeaders(self):
        return HEADERS

    def Channels(self):
        global TOKEN
        global TOKEN_TIME
        LL=[]
        RET_STATUS = False
        TOKEN, TOKEN_TIME, http = getDATA(bData=True)
        soup = BeautifulSoup(http, "html.parser")

        for tag in soup.find_all('div', attrs={"class": "channel", "data-islocked": ""}):
            try:
                if "radio" in tag.get('data-group'):
                    continue
                title = tag.find('img').get('alt')
                ids = utils.title_to_crc32(title)
                img = tag.find('img').get('src')
                data_ch = tag.get('data-channel')
                url = f"ext:{SOURCE}:https://uk.ukrainske.tv/{data_ch}/index.m3u8"
                LL.append((ids, title, 'Украина', url, img))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(SOURCE, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        global TOKEN
        global TOKEN_TIME
        if int(time.time()) > TOKEN_TIME - 600:
            timeOLD = time.ctime(TOKEN_TIME)
            print(f"[{SOURCE}] token expired: [{timeOLD}]")
            logger.info(f"[{SOURCE}] token expired: [{timeOLD}]")
            TOKEN, TOKEN_TIME = getDATA()
            timeNEW = time.ctime(TOKEN_TIME)
            print(f"[{SOURCE}] token updated: [{timeNEW}]")
            logger.info(f"[{SOURCE}] token updated: [{timeNEW}]")
        return f"{lnk}?token={TOKEN}"
