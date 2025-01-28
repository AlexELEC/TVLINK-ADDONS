# -*- coding: utf-8 -*-

import os, sys, json
import requests
from pathlib import Path

root_dir = os.path.dirname(sys.argv[0])
cache_dir = os.path.join(root_dir, 'cache')
sys.path.append(root_dir)

import utils
from utils import logger, DEF_BROWSER

if not os.path.isdir(cache_dir): os.makedirs(cache_dir)

SOURCE = Path(__file__).stem
TOKEN_PATCH = os.path.join(cache_dir, SOURCE)

API_URL = 'https://clients.production.vidmind.com/vidmind-stb-ws'

HEADERS = {'User-Agent': DEF_BROWSER,
           'Accept': 'application/json, text/plain, */*',
           'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
           'Connection': 'keep-alive',
           'Referer': 'https://tv.kyivstar.ua/',
           'x-vidmind-locale': 'ru_RU',
           'x-vidmind-device-type': 'web',
           'x-vidmind-app-version': 'default',
           'x-vidmind-ivi-support': 'true',
           }

def getAuth():
    device_id = None
    session_id = None
    ver_num = None
    if os.path.isfile(TOKEN_PATCH):
        with open(TOKEN_PATCH, 'r') as f:
            token_line = f.readlines()
        device_id = token_line[0].strip()
        session_id = token_line[1].strip()
        ver_num = token_line[2].strip()
        HEADERS.update({'x-vidmind-device-id': device_id})
    else:
        from random import randint
        ver_num = "v4"
        device_id = str(randint(1000000000, 9000000000))
        HEADERS.update({'x-vidmind-device-id': device_id})
        tmp_headers = HEADERS.copy()
        tmp_headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        data = {"username": '557455cfe4b04ad886a6ae41\\anonymous', "password": 'anonymous'}
        req = requests.post(f"{API_URL}/authentication/login", data=data, headers=tmp_headers)
        try:
            session_id = json.loads(req.text)["sessionId"]
            with open(TOKEN_PATCH, 'w') as f:
                f.write(f"{device_id}\n{session_id}\n{ver_num}")
        except: pass
    return device_id, session_id, ver_num

DEVICE_ID, SESSION_ID, VER_NUM = getAuth()

class Scraper:
    def getHeaders(self):
        return HEADERS

    def getGroups(self):
        groups = {}
        http = requests.get(f"{API_URL}/v1/contentareas/LIVE_CHANNELS;jsessionid={SESSION_ID}?includeRestricted=true&limit=100", headers=HEADERS)
        L = json.loads(http.text)
        for grp in L:
            grp_name = grp["name"]
            if grp_name in ["Все", "КС ТВ", "Избранное ТВ", "Радио"]:
                continue
            grp_assetId = grp["assetId"]
            groups[grp_assetId] = grp_name
        return dict(reversed(groups.items()))

    def Channels(self):
        LL=[]
        TMP_IDS = []
        RET_STATUS = False
        groups = self.getGroups()
        for grp_key in groups.keys():
            chGroup = groups[grp_key]
            url = f"{API_URL}/gallery/contentgroups/{grp_key};jsessionid={SESSION_ID}?offset=0&limit=999"
            http = requests.get(url, headers=HEADERS)
            L = json.loads(http.text)

            for cnLine in L:
                try:
                    if not cnLine["purchased"]: continue
                    title = cnLine["name"]
                    if "КС ТВ" in title or "КБ ТВ" in title or " FM" in title: continue
                    ids = utils.title_to_crc32(title)
                    if ids in TMP_IDS: continue
                    TMP_IDS.append(ids)
                    chID = cnLine["assetId"]
                    logo = cnLine["images"][0]["url"]
                    url = f"ext:{SOURCE}:http://{chID}"
                    LL.append((ids, title, chGroup, url, logo))
                except:
                    pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(SOURCE, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        chID = lnk.replace('http://', '')
        chUrl = f"{API_URL}/play/{VER_NUM};jsessionid={SESSION_ID}?assetId={chID}"
        http = requests.get(chUrl, headers=HEADERS)

        try:
            req = json.loads(http.text)
        except:
            print(f"[{SOURCE}] Error: {http.text}")
            logger.info(f"[{SOURCE}] Error: {http.text}")
            return ''

        try: url_url = req["liveChannelUrl"]
        except:
            try:
                url_url = req["media"][0]["url"]
            except:
                print(f"[{SOURCE}] Error: get link")
                logger.info(f"[{SOURCE}] Error: get link")
                return ''
                
        if not '.m3u8' in url_url:
            url_url = f"{url_url}.m3u8-del"
        return url_url
