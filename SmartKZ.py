# -*- coding: utf-8 -*-

import os, sys, json
import requests

root_dir = os.path.dirname(sys.argv[0])
sys.path.append(root_dir)

import utils

class Scraper:
    def __init__(self):
        self.source = 'SmartKZ'
        self.plist = 'https://smart-tv.id-tv.kz/rest/channels?authToken=02bf8e460fbff76b&fwVersion=pcplayer.m3u'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': 'SmartLabs/1.51652.472 (sml723x, SML-482) SmartSDK/1.5.63-rt-25 Qt/4.7.3 API/20121210'}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        http = requests.get(self.plist, headers=self.headers, verify=False)
        L = json.loads(http.text)['channels']

        for cnLine in L:
            try:
                title = cnLine['name']
                lnk = cnLine['url']
                if title and 'http' in lnk:
                    title = title.replace('.', '').strip()
                    ids = utils.title_to_crc32(title)
                    url = f'{self.link}{lnk}.m3u8'
                    if cnLine['posters']: logo = cnLine['posters']['default']['url']
                    else: logo = ''
                    LL.append((ids, title, self.source, url, logo))
                else: continue  
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def getLink(self, lnk):
        return lnk
