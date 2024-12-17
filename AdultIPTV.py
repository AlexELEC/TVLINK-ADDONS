# -*- coding: utf-8 -*-

import os, sys
from pathlib import Path

root_dir = os.path.dirname(sys.argv[0])
sys.path.append(root_dir)

import utils
from utils import DEF_BROWSER

class Scraper:
    def __init__(self):
        self.source = Path(__file__).stem
        self.plist = 'http://adultiptv.net/chs.m3u'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': DEF_BROWSER}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        RET_STATUS = False
        logo = 'https://media.info/l/o/6/6261.1471157192.png'
        group = "Эротика"
        http = utils.getURL(self.plist, headers=self.headers)
        http = utils.clean_m3u(http)
        L = http.splitlines()

        for cnLine in L:
            try:
                tail = cnLine.partition(',')[2]
                if 'http' in tail:
                    head,sep,tail = tail.partition('http')
                    title = head.replace("AdultIPTV.net", "").strip()
                    ids = utils.title_to_crc32(title)
                    url = self.link + (sep+tail).strip()
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
