# -*- coding: utf-8 -*-

import os, sys, json
import requests
from uuid import uuid4

root_dir = os.path.dirname(sys.argv[0])
sys.path.append(root_dir)

import utils
from utils import logger, DEF_BROWSER

# languages: "ta", "kn", "pa", "bn", "en", "ml", "mr", "gu", "te", "hi", "hr", "or", "as", "ru"
# example: LANG = 'en,ru,hi'
LANG = 'en'

GROUPS = ['News', 'Movie', 'Entertainment', 'trendingchannels']


class Scraper:
    def __init__(self):
        self.source = 'Zee5Free'
        self.link = f'ext:{self.source}:'
        self.device_id = str(uuid4())
        self.headers = {'User-Agent': DEF_BROWSER,
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Content-Type': 'application/json',
                        'Referer': 'https://www.zee5.com/'}
        self.country = self.get_country()

    def getHeaders(self):
        return {'User-Agent': DEF_BROWSER,
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.zee5.com/'}

    def get_country(self):
        data = requests.get("https://xtra.zee5.com/country", headers=self.headers).json()
        country_code = data.get('country_code') if data.get('country_code') else 'IN'
        return country_code

    def get_token(self, refresh=False):
        if "x-access-token" in self.headers.keys() and not refresh:
            return
        url='https://useraction.zee5.com/token/platform_tokens.php?platform_name=desktop_web'
        data = requests.get(url, headers=self.headers).json()
        self.headers["x-access-token"] = data['token']

    def Channels(self):
        LL=[]
        IDS = []
        RET_STATUS = False
        self.get_token(refresh=True)
        for group in GROUPS:
            grp = group
            if group == 'trendingchannels':
                grp = 'Trending'
            url = f"https://gwapi.zee5.com/v1/channel/bygenre?genres={group}&languages={LANG}&country={self.country}"
            data = requests.get(url, headers=self.headers).json()
    
            for cnLine in data["items"][0]["items"]:
                try:
                    if cnLine.get("business_type") != "advertisement":
                        continue
                    chID = cnLine["id"]
                    if chID in IDS:
                        continue
                    IDS.append(chID)
                    title = cnLine["title"]
                    title = title.replace('&','').strip()
                    chImg = cnLine["list_image"]
                    ids = utils.title_to_crc32(title)
                    url = f"{self.link}http://{chID}"
                    logo = f"https://akamaividz.zee5.com/resources/{chID}/list/270x152/{chImg}"
                    LL.append((ids, title, grp, url, logo))
                except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        self.get_token()
        chID = lnk.replace('http://', '')
        data = {"X-Z5-Guest-Token": self.device_id, "x-access-token": self.headers.get('x-access-token')}
        url = f"https://spapi.zee5.com/singlePlayback/getDetails/secure?channel_id={chID}&device_id={self.device_id}&platform_name=desktop_web&translation=en&user_language={LANG}&country={self.country}&app_version=2.52.45&user_type=guest&check_parental_control=false&ppid={self.device_id}&version=12"
        http = requests.post(url, json=data, headers=self.headers).json()
        #print (json.dumps(http, indent=2))
        strm_url = ''
        if http.get('error_msg'):
             print (f"[{self.source}] Error: {http.get('error_msg')}")
             logger.info(f"[{self.source}] Error: {http.get('error_msg')}")
             if 'x-access-token' in http.get('error_msg'):
                print (f"[{self.source}]: Refresh Token")
                logger.info(f"[{self.source}]: Refresh Token")
                self.get_token(refresh=True)
        else:
            try: strm_url = http['keyOsDetails'].get('video_token')
            except:
                try: strm_url = http['keyOsDetails'].get('hls_token')
                except: pass
        return strm_url

