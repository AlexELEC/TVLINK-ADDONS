# -*- coding: utf-8 -*-

import os, sys

root_dir = os.path.dirname(sys.argv[0])
sys.path.append(root_dir)

import utils

class Scraper:
    def __init__(self):
        self.source = 'AdultIPTV'
        self.plist = 'http://adultiptv.net/chs.m3u'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        logo = 'https://www.logolynx.com/images/logolynx/80/8029be5f3fb7e3859600ae770aae95fc.png'
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

    def getLink(self, lnk):
        return lnk
