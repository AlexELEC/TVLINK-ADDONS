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
        self.source = 'OntiviNet'
        self.site = 'http://vip.ontivi.net'
        self.link = f'ext:{self.source}:'
        self.listURL = f'{self.site}/chanel'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Referer': self.site}

    def getHeaders(self):
        return self.headers

    def renameGrp(self, grp):
        if grp == '': return self.source
        gr = grp
        if 'Общенациональные'   in grp: gr='Общие'
        if 'Фильмовые'          in grp: gr='Кино'
        if 'Спортивные'         in grp: gr='Спорт'
        if 'Информационные'     in grp: gr='Новости'
        return gr

    def getGroups(self):
        GRP = []
        http = utils.getURL(f"{self.listURL}?catidd=0", headers=self.headers)
        soup = BeautifulSoup(http, "html.parser")
        tags = soup.find('ul', {'class': "none"})

        for tag in tags.find_all('li'):
            grp_ID = tag.get('data-id')
            if grp_ID == "0": continue
            grp_Name = tag.getText()
            if grp_ID and grp_Name:
                grp_Name = self.renameGrp(grp_Name)
                GRP.append([grp_ID, grp_Name])
        return GRP

    def Channels(self):
        LL = []
        for gpID, gpName in self.getGroups():
            http = utils.getURL(f"{self.listURL}?catidd={gpID}", headers=self.headers)
            soup = BeautifulSoup(http, "html.parser")
            tags = soup.find('ul', {'id': 'all-channel-menu-scroller'})
            for tag in tags.find_all('div', {'class': "all-channel-item"}):
                href = tag.find('a').get('href')
                title = tag.find('div', {'class': 'name'}).getText()
                if title and href:
                    ids = utils.title_to_crc32(title)
                    url = f"{self.link}{self.site}{href}"
                    LL.append((ids, title, gpName, url, ''))
        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def getLink(self, lnk):
        url = ''
        http = utils.getURL(lnk, headers=self.headers)
        soup = BeautifulSoup(http, "html.parser")
        tags = soup.find('div', {'id': 'player'})
        urls = utils.mfind(str(tags), 'get("open",{', '},function(data)')
        urls = urls.split(':', 1)
        if 'silka' in urls:
            url = urls[1][1:-1]
        elif 'kes' in urls:
            kes = urls[1][1:-1]
            http = utils.getURL(f"{self.site}/open?kes={kes}", headers=self.headers)
            url = utils.mfind(http, "file:'", "', id:")
        return url
