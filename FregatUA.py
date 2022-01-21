# -*- coding: utf-8 -*-

import os, sys
from random import choice

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

hex_characters = '0123456789ABCDEF'
rnd_mac = [choice(hex_characters) for _ in range(4)]
MAC = 'E4:27:71:FF:{0}{1}:{2}{3}'.format(rnd_mac[0], rnd_mac[1], rnd_mac[2], rnd_mac[3])

class Scraper:
    def __init__(self):
        self.source = 'FregatUA'
        self.plist = 'http://fe.ott.fregat.net/CacheClient/ncdxml/ChannelPackage/list_channels?channelPackageId=20813412&locationId=1000050&from=0&to=2147483647&lang=ru'
        self.link = f'ext:{self.source}:'
        self.headers = {'User-Agent': 'SmartLabs/1.51652.472 (sml723x, SML-482) SmartSDK/1.5.63-rt-25 Qt/4.7.3 API/20121210', 'x-smartlabs-mac-address': MAC}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        group = self.source
        http = utils.getURL(self.plist, headers=self.headers)
        soup = BeautifulSoup(http, "html.parser")
        titles = soup.find_all('bcname')
        links = soup.find_all('url')
        logos = soup.find_all('logo')

        for i in range(0, len(titles)):
            try:
                title = titles[i].get_text()
                lnk = links[i].get_text()
                img = logos[i].get_text()
                if title and 'http' in lnk:
                    ids = utils.title_to_crc32(title)
                    url = f'{self.link}{lnk}'
                    if img: logo = f"http://212.115.255.109/images/c90x90/{img}"
                    else: logo = ''
                    LL.append((ids, title, group, url, logo))
                else: continue  
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def getLink(self, lnk):
        return lnk
