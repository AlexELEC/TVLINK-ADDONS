# -*- coding: utf-8 -*-

import os, sys, json
import requests
from pathlib import Path

root_dir = os.path.dirname(sys.argv[0])
cache_dir = os.path.join(root_dir, 'cache')
if not root_dir in sys.path: sys.path.append(root_dir)
if not os.path.isdir(cache_dir): os.makedirs(cache_dir)

import utils
from utils import DEF_BROWSER


class Scraper:
    def __init__(self):
        self.source = Path(__file__).stem
        self.link = f'ext:{self.source}:'
        self.site = 'https://24htv.platform24.tv/v2'
        self.headers = {'User-Agent': DEF_BROWSER}
        self.TOKEN = self.getToken()

    def getHeaders(self):
        return self.headers

    def getToken(self, refresh=False):
        token_patch = os.path.join(cache_dir, f"{self.source}.tkn")
        if not refresh and os.path.isfile(token_patch):
            with open(token_patch, 'r') as f:
                access_token = f.readline()
        else:
            if os.path.isfile(token_patch):
                os.remove(token_patch)
            try:
                req = requests.get(f"{self.site}/users/self/network", headers=self.headers)
                req.raise_for_status()
            except:
                return None

            from uuid import uuid4
            from base64 import b64encode
            user_login = str(uuid4()).upper()
            user_passw = b64encode(user_login.encode('utf-8')).decode('utf-8')[:32]
            headers = self.headers.copy()
            headers.update({'Content-Type': 'application/json'})
            data = {"username": user_login, "password": user_passw, "is_guest": True, "app_version": "v30"}
            try:
                req = requests.post(f"{self.site}/users", json=data, headers=headers)
                req.raise_for_status()
            except:
                return None

            data = {"login": user_login, "password": user_passw, "app_version": "v30"}
            try:
                req = requests.post(f"{self.site}/auth/login", json=data, headers=headers)
                req.raise_for_status()
            except:
                return None
            access_token = json.loads(req.text)["access_token"]

            serial = str(uuid4()).upper()
            data = {
                'device_type': 'pc',
                'vendor': 'PC',
                'model': 'Firefox 148',
                'version': '166',
                'os_name': 'Windows',
                'os_version': '10',
                'application_type': 'web',
                'serial': serial
            }
            try:
                req = requests.post(f"{self.site}/users/self/devices?access_token={access_token}", json=data, headers=headers)
                req.raise_for_status()
            except:
                return None
            device_id = json.loads(req.text)["id"]

            data = {"device_id": device_id}
            try:
                req = requests.post(f"{self.site}/auth/device", json=data, headers=headers)
                req.raise_for_status()
            except:
                return None
            access_token = json.loads(req.text)["access_token"]

            with open(token_patch, 'w') as f:
                f.write(f"{access_token}")

        return str(access_token)

    def Channels(self):
        LL=[]
        RET_STATUS = False

        if not self.TOKEN:
            return RET_STATUS

        try:
            http = requests.get(f"{self.site}/channels/channel_list?access_token={self.TOKEN}&channels_version=2&format=json&includes=current_schedules", headers=self.headers)
            http.raise_for_status()
        except:
            self.TOKEN = self.getToken(True)
            try:
                http = requests.get(f"{self.site}/channels/channel_list?access_token={self.TOKEN}&channels_version=2&format=json&includes=current_schedules", headers=self.headers)
                http.raise_for_status()
            except:
                return RET_STATUS
        parsed = json.loads(http.text)

        # get channels
        for cnLine in parsed:
            try:
                if cnLine["is_free"]:
                    chID = cnLine["id"]
                    title = cnLine["name"]
                    logo = cnLine["cover"]["full"]
                    ids = utils.title_to_crc32(title)
                    url = f"{self.link}http://{chID}"
                    LL.append((ids, title, self.source, url, logo))
            except:
                continue

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        if not self.TOKEN:
            return ''

        chID = lnk.replace('http://', '')
        try:
            http = requests.get(f"{self.site}/channels/{chID}/stream?access_token={self.TOKEN}&format=json&history=false", headers=self.headers)
            http.raise_for_status()
        except:
            self.TOKEN = self.getToken(True)
            try:
                http = requests.get(f"{self.site}/channels/{chID}stream?access_token={self.TOKEN}&format=json&history=false", headers=self.headers)
                http.raise_for_status()
            except:
                return ''

        url = json.loads(http.text)["stream_info"]
        if '/data.json' in url:
            return url.replace('/data.json', '/index.m3u8')
        else:
            return ''
