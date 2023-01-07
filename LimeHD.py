# -*- coding: utf-8 -*-

import os, sys, json

root_dir = os.path.dirname(sys.argv[0])
sys.path.append(root_dir)

import utils

class Scraper:
    def __init__(self):
        self.source = 'LimeHD'
        self.api = 'https://api.iptv2021.com/v1/streams/'
        self.plist = 'https://raw.githubusercontent.com/AlexELEC/TVLINK-ADDONS/main/plist/limeHD'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
                        'X-Access-Key': '10aa09114588a5f750eaed5e9de53704c858e144'}

    def getHeaders(self):
        return {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0'}

    def Channels(self):
        LL=[]
        http = utils.getExtPlist(self.plist, list_name=self.source)
        http = utils.clean_m3u(http, srcName=self.source)
        L = http.splitlines()

        for cnLine in L:
            try:
                data, group, logo = utils.group_logo_m3u(cnLine)
                tail = data.partition(',')[2]
                if 'http' in tail:
                    head,sep,tail = tail.partition('http')
                    title = head.strip()
                    ids = utils.title_to_crc32(title)
                    org_link = (sep+tail).strip()
                    url = f"{self.link}{org_link}"
                    LL.append((ids, title, self.source, url, logo))
                else: continue  
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def getLink(self, lnk):
        chID = lnk.replace('https://limehd.tv/', '')
        http = utils.getURL(f'{self.api}{chID}', headers=self.headers)
        try: chURL = json.loads(http)["data"][0]["attributes"]["playlist_url"]
        except: chURL = ''
        return chURL
