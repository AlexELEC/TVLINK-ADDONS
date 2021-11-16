# -*- coding: utf-8 -*-

import os, sys
from random import choice

root_dir = os.path.dirname(sys.argv[0])
sys.path.append(root_dir)

import utils

hex_characters = '0123456789ABCDEF'
rnd_mac = [choice(hex_characters) for _ in range(4)]
MAC = 'E4:27:71:FF:{0}{1}:{2}{3}'.format(rnd_mac[0], rnd_mac[1], rnd_mac[2], rnd_mac[3])

class Scraper:
    def __init__(self):
        self.source = 'FregatUA'
        self.plist = 'https://raw.githubusercontent.com/AlexELEC/TVLINK-ADDONS/main/plist/fregat'
        self.link = 'ext:{0}:'.format(self.source)
        self.headers = {'User-Agent': 'SmartLabs/1.51652.472 (sml723x, SML-482) SmartSDK/1.5.63-rt-25 Qt/4.7.3 API/20121210', 'x-smartlabs-mac-address': MAC}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        group = self.source
        http = utils.getURL(self.plist)
        http = utils.clean_m3u(http)
        L = http.splitlines()

        for cnLine in L:
            try:
                data, group, logo = utils.group_logo_m3u(cnLine)
                tail = data.partition(',')[2]
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
