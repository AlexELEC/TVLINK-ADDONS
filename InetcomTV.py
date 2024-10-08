# -*- coding: utf-8 -*-

import os, sys, json

root_dir = os.path.dirname(sys.argv[0])
sys.path.append(root_dir)

import utils

class Scraper:
    def __init__(self):
        self.source = 'InetcomTV'
        self.plist = 'http://api4.inetcom.tv/channel/all'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.140 Mobile Safari/537.36',
                        'X-Client-Info': 'AndroidPhone 50327582',
                        'X-Client-Model': 'OnePlus A5010',
                        'X-Device': '4',
                        'Referer': 'http://iptv.inetcom.ru/phone_app_v2/index.html?platform=AndroidPhone&serial=50327582',
                        'X-Requested-With': 'tv.inetcom.phone2',
                       }

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        RET_STATUS = False
        http = utils.getURL(self.plist, headers=self.headers)
        L = json.loads(http)

        for cnLine in L:
            try:
                ch_id = cnLine["id"]
                title = cnLine["caption"]
                logo = cnLine["logoUrl"]
                ids = utils.title_to_crc32(title)
                url = f"{self.link}http://{ch_id}"
                LL.append((ids, title, self.source, url, logo))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        chURL = ''
        chID = lnk.replace('http://', '')
        http = utils.getURL(self.plist, headers=self.headers)
        L = json.loads(http)

        for cnLine in L:
            try:
                ch_id = cnLine["id"]
                if int(ch_id) == int(chID):
                    chURL = cnLine["streams"]["hls"]
                    break
            except: pass

        return chURL
