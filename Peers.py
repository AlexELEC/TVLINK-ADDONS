# -*- coding: utf-8 -*-

import os, sys, re
import requests, json
from copy import copy
from time import time

root_dir = os.path.dirname(sys.argv[0])
sys.path.append(root_dir)

import utils
from utils import DEF_BROWSER

class Scraper:
    def __init__(self):
        self.source = 'Peers'
        self.site = 'https://peers.tv/'
        self.link = f'ext:{self.source}:'
        self.api = 'http://api.peers.tv'
        self.access_token = None
        self.time_token = 0
        self.headers = {'User-Agent': DEF_BROWSER,
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Referer': self.site}

    def getHeaders(self):
        return self.headers

    def getToken(self):
        if not self.access_token or time() - self.time_token > 3600:
            data = {"grant_type": "inetra:anonymous", "client_id": "29783051", "client_secret": "b4d4eb438d760da95f0acb5bc6b5c760"}
            http = requests.post(f"{self.api}/auth/2/token", data=data, headers=self.headers)
            http = json.loads(http.text)
            self.access_token = http["access_token"]
            self.time_token = time()

    def Channels(self):
        LL=[]
        LIST_URL = []
        self.getToken()
        hdr_head = copy(self.headers)
        hdr_head.update({'Client-Capabilities': 'paid_content,adult_content'})
        hdr_head.update({'Authorization': f"Bearer {self.access_token}"})
        http = requests.get(f"{self.api}/iptv/2/playlist.m3u", headers=hdr_head)
        http = utils.clean_m3u(http.text, srcName=self.source)
        L = http.splitlines()

        for cnLine in L:
            try:
                data, grp, logo = utils.group_logo_m3u(cnLine)
                grp = utils.replaceGRP(grp, self.source)
                tail = data.partition(',')[2]
                if 'embed:?url=' in tail: continue
                if 'http' in tail:
                    head, sep, tail = tail.partition('http')
                    url = None
                    try:
                        url = re.search('/streaming/(.*?)/playlist.m3u8', tail).group(1)
                        url = url[:url.rfind('/')]
                    except: continue
                    if url and url not in LIST_URL:
                        LIST_URL.append(url)
                        title = head.strip()
                        ids = utils.title_to_crc32(title)
                        url = f"{self.link}{self.api}/timeshift/{url}/playlist.m3u8?offset=1"
                        LL.append((ids, title, grp, url, logo))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def getLink(self, lnk):
        self.getToken()
        url = ''
        if self.access_token:
            url = f'{lnk}&token={self.access_token}'
        return url
