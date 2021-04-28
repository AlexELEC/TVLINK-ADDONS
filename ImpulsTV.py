# -*- coding: utf-8 -*-

import os, sys

root_dir = os.path.dirname(sys.argv[0])
libs_dir = os.path.join(root_dir, 'libs')
ssv_file = os.path.join(libs_dir, 'soupsieve.whl')
bs4_file = os.path.join(libs_dir, 'beautifulsoup.whl')

sys.path.append(root_dir)
sys.path.append(libs_dir)
sys.path.insert(0, ssv_file)
sys.path.insert(0, bs4_file)

import utils
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self):
        self.source = 'ImpulsTV'
        self.link = 'ext:{0}:'.format(self.source)
        self.headers = {'User-Agent': 'mag'}

        ### set proxy list for register account ###
        self.proxy_list = None

        # sample proxy list
        '''
        self.proxy_list = [
                          'http://185.234.244.30:8080',
                          'http://85.15.152.39:3128',
                          'http://109.170.97.146:8085',
                          'http://195.133.153.186:8080',
                          'http://83.166.112.14:8080',
                          'http://178.159.40.19:8080',
                          'http://185.110.211.101:8080',
                          'http://85.143.254.20:8080',
                          ]
        '''

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        try:
            http = utils.get_ImpulsTV(proxy_list=self.proxy_list)
            soup = BeautifulSoup(http, 'lxml')
            icons = soup.find_all('icon')
            names = soup.find_all('name')
            urls = soup.find_all('url')
            for n, name in enumerate(names):
                title = name.text
                url = urls[n].text
                logo = icons[n].text
                ids = utils.title_to_crc32(title)
                LL.append((ids, title, self.source, url, logo))
        except: pass
        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def getLink(self, lnk):
        return lnk
