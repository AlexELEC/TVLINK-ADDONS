# -*- coding: utf-8 -*-

import os, sys, json

root_dir = os.path.dirname(sys.argv[0])
sys.path.append(root_dir)

import utils

FREE_ONLY = True

class Scraper:
    def __init__(self):
        self.source = 'MoreTV'
        self.link = f'ext:{self.source}:'
        self.api_url = 'https://more.tv/api/web/channels'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
                        'Referer': 'https://player.mediavitrina.ru/'}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        http = utils.getURL(self.api_url, headers=self.headers)
        L = json.loads(http)["data"]

        for cnLine in L:
            try:
                if FREE_ONLY:
                    isAvailable = cnLine["availability"]["isAvailable"]
                    if not isAvailable: continue
                title = cnLine["title"]
                logo = cnLine["logo"]
                player = cnLine["vitrinaAppleTVSDK"]
                ids = utils.title_to_crc32(title)
                url = f"{self.link}{player}"
                LL.append((ids, title, "Общие", url, logo))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def getLink(self, lnk):
        http = utils.getURL(lnk, headers=self.headers)
        streams_api_url = json.loads(http)["result"]["sdk_config"]["streams_api_url"]
        http = utils.getURL(streams_api_url, headers=self.headers)
        url = json.loads(http)["hls"][0]
        return url
