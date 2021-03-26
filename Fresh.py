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
        self.source = 'Fresh'
        self.site = 'http://tv-fresh.org'
        self.link = 'ext:{0}:'.format(self.source)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Referer': self.site}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL = []
        LLL = []
        group = self.source
        http = ''
        for p in range(1,7):
            http = http + utils.getURL(self.site + '/page/' + str(p), referer = self.site)
        soup = BeautifulSoup(http, "html.parser")

        for tag in soup.find_all('a', {'class': 'dremmkol'}):
            try:
                # url = 'ext:Fresh:http://tv-fresh.org/39-24-tehno.html'
                url = self.link + tag.get('href')
                if url not in LLL:
                    LLL.append(url)
                    img = self.site + tag.find('img').get('src')
                    title = tag.get('title')
                    title = title.replace('смотреть онлайн','').strip()
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
        soup = BeautifulSoup(http, "html.parser")
        iframe, = soup.find_all('div', {'class': 'hfdhncvnnnnn'})
        php_lnk = iframe.find('iframe').get('src')
        http = utils.getURL(php_lnk, referer=lnk)
        url = utils.mfind(http, '?file=', '" type')
        # url = 'http://50.7.220.130:8081/24techno/index.m3u8?wmsAuthSign=527278d4d09ca92492d4d5878d79b7a6-1616762350-89i84i08i212'
        return url
