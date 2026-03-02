# -*- coding: utf-8 -*-

import os, sys, json
import requests
import random
import string
from pathlib import Path

root_dir = os.path.dirname(sys.argv[0])
if not root_dir in sys.path: sys.path.append(root_dir)

import utils
from utils import DEF_BROWSER


class Scraper:
    def __init__(self):
        self.source = Path(__file__).stem
        self.site = 'https://api.bolshoe.tv'
        self.headers = {'User-Agent': DEF_BROWSER,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Referer': 'https://bolshoe.tv/',
                        'x-app-build': '105',
                        'x-app-mode': 'WEB',
                        'x-app-platform': 'WEB',
                        'x-dev-platform': 'PC_WEB'}

    def getHeaders(self):
        return {'User-Agent': DEF_BROWSER, 'Referer': 'https://bolshoe.tv/'}

    def get_token(self):
        characters = string.ascii_letters + string.digits
        auth_id = ''.join(random.choice(characters) for _ in range(16))

        http = requests.get(f"{self.site}/web/1/auth/web/web_{auth_id}", headers=self.headers)
        access_token = json.loads(http.text)["response"]["access_token"]
        return access_token

    def Channels(self):
        LL=[]
        RET_STATUS = False

        access_token = self.get_token()
        if not access_token:
            return RET_STATUS

        self.headers.update({'x-app-access-token': access_token})
        http = requests.get(f"{self.site}/web/1/collections?tab_id=tv_channels_tab&RB_queue_count=100&RB_teaser_count=100", headers=self.headers)
        parsed = json.loads(http.text)["response"]

        # get channels
        CH_IDS = []
        for cnGrps in parsed:
            group = cnGrps["RB_title"]
            for cnLine in cnGrps["EKs"]:
                try:
                    chID = cnLine["stream_id"]
                    title = cnLine["chan_name"].strip()
                    logo = cnLine["chan_poster_url"]
                except:
                    continue

                ids = utils.title_to_crc32(title)
                url = f"ext:{self.source}:http://{chID}"
                if not ids in CH_IDS:
                    CH_IDS.append(ids)
                    LL.append((ids, title, group, url, logo))

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        chID = lnk.replace('http://', '')
        access_token = self.get_token()
        if not access_token:
            return ''

        self.headers.update({'x-app-access-token': access_token})
        data = {"stream_id": chID, "dev_model": "ANDROID_TV"}
        http = requests.post(f"{self.site}/v1/agregator/getReleaseChannel", json=data, headers=self.headers).json()
        try:
            url = http["response"]["stream_url"]
            return f"https:{url}"
        except: pass
        return ''
