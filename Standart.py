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
        self.source = 'Standart'
        self.site = 'http://standart.tv'
        self.link = 'ext:{0}:'.format(self.source)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Referer': self.site}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        group = self.source
        http = utils.getURL(self.site, referer=self.site)
        soup = BeautifulSoup(http, "html.parser")

        for tag in soup.find_all('a', {'class': 'channel-item channel-item--small'}):
            try:
                url_org = tag.get('href')
                # url = 'ext:Standart:http://standart.tv/channel-1-inter-ua'
                url = self.link + url_org
                img_org = tag.find('img').get('data-lazy')
                if not img_org == '': img = self.site + img_org
                else: img = ''
                title = tag.find('div', {'href': url_org}).text
                title = title.strip()
                # ids = chID
                ids = utils.title_to_crc32(title)
                # LL = ( (0-chID, 1-chTitle, 2-chGroup, 3-chUrl, 4-chLogo), ...)
                LL.append((ids, title, group, url, img))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def getLink(self, lnk):
        http = utils.getURL(lnk, referer=self.site)
        if not 'file: "' in http: return ''
        url = utils.mfind(http, 'file: "', '"')
        if ']' in url:
            url = url[url.find(']')+1:]
        # url = 'http://51.68.141.106:8081/tv/inter/playlist.m3u8?wmsAuthSign=c2VydmVyX3RpbWU9My8yNi8yMDIxIDExOjAyOjUzIEFNJmhhc2hfdmFsdWU9VENDdkdyN2FMa1NQUHlyM0VPcXozQT09JnZhbGlkbWludXRlcz03MjA='
        return url
