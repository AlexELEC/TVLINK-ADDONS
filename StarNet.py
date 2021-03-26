# -*- coding: utf-8 -*-

import os, sys

root_dir = os.path.dirname(sys.argv[0])
sys.path.append(root_dir)

import utils

class Scraper:
    def __init__(self):
        self.source = 'StarNet'
        self.part_url = 'http://starnet-md.'
        self.plist = 'https://raw.githubusercontent.com/Nexterr-origin/simpleTV-Playlists/main/starnet-md'
        self.link = 'ext:{0}:'.format(self.source)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.1.1; POV_TV-HDMI-200BT Build/JRO03H) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30'}

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
        ID = lnk.replace(self.part_url, '').strip()
        token_url = 'http://token.stb.md/api/Flussonic/stream/{}/metadata.json'.format(ID)
        http = utils.getURL(token_url, headers=self.headers)
        url = utils.mfind(http, '"url":"', '"}]}')
        return url
