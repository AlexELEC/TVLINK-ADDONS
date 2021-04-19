# -*- coding: utf-8 -*-

import os, sys, json, time
from urllib.request import urlopen

root_dir = os.path.dirname(sys.argv[0])
sys.path.append(root_dir)

import utils

ttm = 0
token = ''

class Scraper:
    def __init__(self):
        self.source = 'Vitrina'
        self.site = 'https://vitrina.tv'
        self.link = 'ext:{0}:'.format(self.source)
        self.listURL = 'https://vitrina.tv/configs/config.json'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3'}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        http = utils.getURL(self.listURL, headers=self.headers)
        L = json.loads(http)['result']['channels']

        for cnLine in L:
            try:
                title = cnLine['channel_title']
                title = title.replace('5 Канал', '5 Канал (RU)')
                ids = utils.title_to_crc32(title)
                url = self.link + cnLine['web_player_url'].replace('?isPlay=true', '')
            except: continue
            try:
                img_name = cnLine['channel_slug']
                logo = '{0}/assets/images/logo/{1}.svg'.format(self.site, img_name)
            except: logo = ''
            LL.append((ids, title, self.source, url, logo))

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def getLink(self, lnk):
        http = utils.getURL(lnk, headers=self.headers)
        if 'let sources_url' in http:
            part_url = utils.mfind(http, 'let sources_url', 'as_array.json')
        else:
            part_url = utils.mfind(http, 'sources:', 'as_array.json')
        head, sep, tail = part_url.partition('http')
        url = 'http' + tail + 'as_array.json'

        global ttm, token
        if token == '' or time.time() - ttm > 3600:
            http = utils.getURL('https://media.mediavitrina.ru/get_token', headers=self.headers)
            token = json.loads(http)['result']['token']
            ttm = time.time()
        stream_url = '{0}?token={1}'.format(url, token)
        resp = utils.getURL(stream_url, headers=self.headers)
        url = json.loads(resp)
        url = url.get("hls")[0]
        return url
