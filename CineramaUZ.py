# -*- coding: utf-8 -*-

import os, sys

root_dir = os.path.dirname(sys.argv[0])
sys.path.append(root_dir)

import utils

class Scraper:
    def __init__(self):
        self.source = 'CineramaUZ'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; MB2 Build/MHC19J)'}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        RET_STATUS = False
        http = utils.getURL("https://raw.githubusercontent.com/AlexELEC/TVLINK-ADDONS/main/plist/cinerama", headers=self.headers)

        for cnLine in http.splitlines():
            try:
                chID, sep, title = cnLine.partition(' = ')
                ids = utils.title_to_crc32(title)
                url = f"{self.link}http://{chID}"
                LL.append((ids, title, self.source, url, ''))
            except:
                pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        chID = lnk.replace('http://', '')
        return f"https://stream1.cinerama.uz/{chID}/index.m3u8"
