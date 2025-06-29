# -*- coding: utf-8 -*-

import os, sys, json

root_dir = os.path.dirname(sys.argv[0])
if not root_dir in sys.path: sys.path.append(root_dir)

import utils
from utils import DEF_BROWSER

class Scraper:
    def __init__(self):
        self.source = 'IPNet'
        self.plist = 'http://api.tv.ipnet.ua/api/v2/site/channels'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': DEF_BROWSER,
                        'Accept': '*/*',
                        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Referer': 'https://tv.ipnet.ua/'
                        }

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        RET_STATUS = False
        group = "Украина"
        http = utils.getURL(self.plist, headers=self.headers)
        L = json.loads(http)["data"]["categories"][0]

        for cnLine in L["channels"]:
            try:
                if not cnLine["can_buy"] == False: continue
                title = cnLine["name"]
                if "Радіо" in title or "радіо" in title: continue
                lnk = cnLine["url"]
                if title and 'http' in lnk:
                    ids = utils.title_to_crc32(title)
                    logo = cnLine["icon_url"]
                    url = f"{self.link}{lnk}"
                    LL.append((ids, title, group, url, logo))
                else: continue
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        return lnk
