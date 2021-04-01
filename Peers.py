# -*- coding: utf-8 -*-

import os, sys, time
from urllib.request import Request, urlopen
from urllib import parse

root_dir = os.path.dirname(sys.argv[0])
sys.path.append(root_dir)

import utils

ttm = 0
token = ''

def postURL(url, data, headers=None):
    request = Request(url, data=data)
    if headers:
        for h in headers.keys(): request.add_header(h, headers[h])
    with urlopen(request) as context:
        response = context.read()
    return response.decode('utf-8')

class Scraper:
    def __init__(self):
        self.source = 'Peers'
        self.site = 'https://peers.tv/'
        self.plist = 'https://raw.githubusercontent.com/AlexELEC/TVLINK-ADDONS/main/plist/peers'
        self.link = 'ext:{0}:'.format(self.source)
        self.headers = {'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 8.0.1;)', 'Referer': self.site}

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
        global ttm, token
        if token == '' or time.time() - ttm > 3600:
            api_url = 'http://api.peers.tv/auth/2/token'
            data = b'grant_type=inetra%3Aanonymous&client_id=29783051&client_secret=b4d4eb438d760da95f0acb5bc6b5c760'
            self.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            http = postURL(api_url, data, headers)
            token = utils.mfind(http, '"access_token":"', '","token_type')
            ttm = time.time()
        url = '{0}&token={1}'.format(lnk, token)
        return url
