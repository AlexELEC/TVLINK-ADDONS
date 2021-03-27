# -*- coding: utf-8 -*-

import os, sys

root_dir = os.path.dirname(sys.argv[0])
sys.path.append(root_dir)

import utils

class Scraper:
    def __init__(self):
        self.source = 'FregatUA'
        self.plist = 'https://raw.githubusercontent.com/AlexELEC/TVLINK-ADDONS/main/plist/fregat'
        self.link = 'ext:{0}:'.format(self.source)
        self.headers = {'User-Agent': 'SmartSDK', 'x-smartlabs-mac-address': 'E4:27:71:FF:00:FF'}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        logo = ''
        group = self.source
        http = utils.getURL(self.plist)
        http = utils.clean_m3u(http)
        L = http.splitlines()

        for cnLine in L:
            try:
                tail = cnLine.partition(',')[2]
                if 'http' in tail:
                    head,sep,tail = tail.partition('http')
                    title = head.strip()
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
