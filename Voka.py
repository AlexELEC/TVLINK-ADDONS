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
        self.source = 'Voka'
        self.link = 'ext:{0}:'.format(self.source)
        self.api_url = 'https://api.voka.tv/v1'
        self.client_id = '69c2949f-d568-4d7f-8068-5cf2f6295e56'
        self.listURL = self.api_url + '/collection_items.json?client_version=0.0.1&expand[channel]=genres,genres.images,images,live_preview,language,live_stream,catchup_availability,timeshift_availability,certification_ratings&filter[collection_id_eq]=9fc67851-41a1-429d-b7ca-4b8f49c53659&locale=ru-RU&page[limit]=300&page[offset]=0&sort=relevance&timezone=10800&client_id=' + self.client_id
        self.headers = {'User-Agent': 'Mozilla/5.0 (SMART-TV; Linux; Tizen 4.0.0.2) AppleWebkit/605.1.15 (KHTML, like Gecko) SamsungBrowser/9.2 TV Safari/605.1.15',
                        'Accept': 'text/html, application/xml, application/xhtml+xml, */*',
                        'Accept-Language': 'ru,en;q=0.9'}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        http = utils.getURL(self.listURL, headers=self.headers)
        L = json.loads(http)['data']

        for cnLine in L:
            try:
                title = cnLine['name']
                title = title.replace('ДомашнийI', 'Домашний Int').replace('ТВ-3', 'ТВ-3 Беларусь').replace('ПерецI', 'Перец Int').replace('Cinema HD', 'Cinema Космос ТВ')
                chID = cnLine['id']
                ids = utils.title_to_crc32(title)
            except: continue
            url = self.link + self.api_url + '/channels/' + chID
            try:
                images = cnLine['images']
                for k in images:
                    img = k['url_template']
                    width = k['original_width']
                    height = k['original_height']
                    logo = img.replace("{width}", str(width)).replace("{height}", str(height)).replace("{crop}", "")
            except: logo = ''
            LL.append((ids, title, self.source, url, logo))

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def getLink(self, lnk):
        global ttm, token
        if token == '' or time.time() - ttm > 3600:
            token_url = self.api_url + '/devices.json?client_version=1.7.0.253&timezone=10800&locale=ru-RU&device_id=ddde0352-7595-3c08-b1c1-6d501d4a2d61&type=browser&model=Unknown&os_name=Linux&os_version=&client_id='+self.client_id
            http = urlopen(token_url, ''.encode("utf-8"))
            token = json.loads(http.read())['data']['device_token']
            ttm = time.time()
        stream_url = lnk+'/stream.json?client_version=1.7.0.246&timezone=10800&locale=ru-RU&protocol=hls&video_codec=h264&audio_codec=mp4a&drm=spbtvcas&screen_width=3840&screen_height=2160&device_token='+token+'&client_id='+self.client_id
        resp = utils.getURL(stream_url, headers=self.headers)
        url = json.loads(resp)['data']['url']
        url = url.replace("https://", "http://")
        return url
