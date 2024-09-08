# -*- coding: utf-8 -*-

import os, sys, json

root_dir = os.path.dirname(sys.argv[0])
sys.path.append(root_dir)

import utils
from utils import DEF_BROWSER

class Scraper:
    def __init__(self):
        self.source = 'UzdplusUZ'
        self.link = f'ext:{self.source}:'
        self.chlist_url = 'https://api.spec.uzd.udevs.io/v1/tv/channel'
        self.headers = {'User-Agent': DEF_BROWSER}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        RET_STATUS = False
        http = utils.getURL(f"{self.chlist_url}?status=true", headers=self.headers)
        L = json.loads(http)["tv_channels"]

        for cnLine in L:
            try:
                chid = cnLine["id"]
                title = cnLine["title_ru"].replace('(Ru)', '').strip()
                logo = cnLine["image"]
                ids = utils.title_to_crc32(title)
                url = f"{self.link}http://{chid}"
                LL.append((ids, title, self.source, url, logo))
            except:
                pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        chID = lnk.replace('http://', '')
        chl_url = ''
        try:
            http = utils.getURL(f"{self.chlist_url}/{chID}", headers=self.headers)
            chl_url = json.loads(http)["channel_stream_all"]
        except: pass
        return chl_url
