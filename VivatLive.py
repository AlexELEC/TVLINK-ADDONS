# -*- coding: utf-8 -*-

### import core, scrapers.VivatLive; tv=scrapers.VivatLive.Scraper(); tv.readToken()

import os, sys, json, time
import requests, re
from uuid import uuid1
from copy import copy
from base64 import b64decode

root_dir = os.path.dirname(sys.argv[0])
cache_dir = os.path.join(root_dir, 'cache')
sys.path.append(root_dir)

import utils
from utils import logger, DEF_BROWSER

if not os.path.isdir(cache_dir): os.makedirs(cache_dir)

class Scraper:
    def __init__(self):
        self.source = 'VivatLive'
        self.link = f'ext:{self.source}:'
        self.api_url = 'https://api.vivat.live/stable'
        self.api_logo = 'https://api.hmara.tv/images/saved'
        self.token_patch = os.path.join(cache_dir, self.source)
        self.access_token = None
        self.refresh_token = None
        self.times_token = 0
        self.dev_id = self.getDevID()
        self.headers = {'User-Agent': DEF_BROWSER,
                        'Accept': '*/*',
                        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Connection': 'keep-alive',
                        'Referer': 'https://vivat.live/'}

    def getHeaders(self):
        return self.headers

    def getDevID(self):
        devid_patch = os.path.join(cache_dir, f"{self.source}.dev")
        if os.path.isfile(devid_patch):
            with open(devid_patch, 'r') as f:
                dev_id = f.readline()
        else:
            dev_id = uuid1().hex[:21]
            with open(devid_patch, 'w') as f:
                f.write(f"{dev_id}")
        return str(dev_id)

    def getTime_token(self, token):
        access_cut = token.split('.')
        access_part = ''
        for i in range( len(access_cut) - 1 ):
            access_part += access_cut[i]
        access_part = access_part + '=' * (4 - len(access_part) % 4) if len(access_part) % 4 != 0 else access_part
        time_exp = b64decode(access_part).decode('utf-8')
        time_exp = utils.mfind(time_exp, '"exp":', ',"type"')
        return int(time_exp)

    def refreshToken(self):
        headers = copy(self.headers)
        headers.update({'Accept': 'application/json, text/plain, */*'})
        if self.access_token:
            headers.update({'Authorization': f"Bearer {self.access_token}"})
        else:
            headers.update({'Authorization': 'Bearer unknown'})

        if self.refresh_token:
            lnk = f"{self.api_url}/sign?deviceId={self.dev_id}&deviceType=2&language=uk&profileId=1&refreshToken={self.refresh_token}"
        else:
            lnk = f"{self.api_url}/sign?deviceId={self.dev_id}&deviceType=2&language=uk&profileId=1&refreshToken="

        req = requests.get(lnk, headers=headers)
        self.access_token = json.loads(req.text)["accessToken"]
        self.refresh_token = json.loads(req.text)["refreshToken"]
        self.times_token = self.getTime_token(self.access_token)
        with open(self.token_patch, 'w') as f:
            f.write(f"{self.access_token}\n{self.refresh_token}\n{self.times_token}")

    def readToken(self):
        if os.path.isfile(self.token_patch):
            with open(self.token_patch, 'r') as f:
                token_line = f.readlines()
            self.access_token = token_line[0].strip()
            self.refresh_token = token_line[1].strip()
            self.times_token = int( token_line[2].strip() )
        else:
            self.refreshToken()

    def getToken(self):
        if not self.access_token or not self.times_token:
            self.readToken()
        if int( time.time() ) > self.times_token - 600:
            timeToken = time.ctime(self.times_token)
            print(f"[{self.source}] token is expired: [{timeToken}]")
            logger.info(f"[{self.source}] token is expired: [{timeToken}]")
            self.refreshToken()

    def Channels(self):
        LL=[]
        self.getToken()
        headers = copy(self.headers)
        headers.update({'Accept': 'application/json, text/plain, */*'})
        headers.update({'Authorization': f"Bearer {self.access_token}"})
        lnk = f"{self.api_url}/content?contentTypes=1&favorite=0&genreIds=0&limit=1000&deviceId={self.dev_id}&deviceType=2&language=ru&profileId=1"
        http = requests.get(lnk, headers=headers).json()

        for cnLine in http:
            try:
                if not cnLine["isAvailable"]: continue
                chID = cnLine["urls"]
                title = cnLine["title"]
                img = cnLine["images"]
                logo = f"{self.api_logo}/{img}"
                ids = utils.title_to_crc32(title)
                url = f"{self.link}http://{chID}"
                LL.append((ids, title, self.source, url, logo))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def getLink(self, lnk):
        self.getToken()
        chID = lnk.replace('http://', '')
        headers = copy(self.headers)
        headers.update({'Accept': 'application/json, text/plain, */*'})
        headers.update({'Authorization': f"Bearer {self.access_token}"})
        lnk = f"{self.api_url}/content2/play?urlId={chID}&deviceId={self.dev_id}&deviceType=2&language=ru&profileId=1"
        http = requests.get(lnk, headers=headers).text
        try:
            return requests.get(lnk, headers=headers).text
        except:
            print(f"[{self.source}] Error: {http}")
            logger.info(f"[{self.source}] Error: {http}")
            return ''
