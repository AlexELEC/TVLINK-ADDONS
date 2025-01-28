# -*- coding: utf-8 -*-

import os, sys, json
import requests, time
from pathlib import Path
from base64 import b64decode

root_dir = os.path.dirname(sys.argv[0])
cache_dir = os.path.join(root_dir, 'cache')
sys.path.append(root_dir)

import utils
from utils import logger, DEF_BROWSER

if not os.path.isdir(cache_dir): os.makedirs(cache_dir)

SOURCE = Path(__file__).stem
TOKEN_PATCH = os.path.join(cache_dir, SOURCE)

API_URL = 'https://api.sweet.tv'

HEADERS = {'User-Agent': DEF_BROWSER,
           'Accept': '*/*',
           'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
           'Connection': 'keep-alive',
           'Referer': 'https://sweet.tv/',
           }

def getTime_token(token):
    access_cut = token.split('.')
    access_part = ''
    for i in range( len(access_cut) - 1 ):
        access_part += access_cut[i]
    access_part = access_part + '=' * (4 - len(access_part) % 4) if len(access_part) % 4 != 0 else access_part
    time_exp = b64decode(access_part).decode('utf-8')
    time_exp = utils.mfind(time_exp, '"exp":', ',"iat"')
    return int(time_exp)

def checkToken(refresh_token, access_token, times_token):
    if int( time.time() ) > times_token - 600:
        global ACCESS_TOKEN
        global TIMES_TOKEN
        timeOLD = time.ctime(times_token)
        print(f"[{SOURCE}] token expired: [{timeOLD}]")
        logger.info(f"[{SOURCE}] token expired: [{timeOLD}]")
        headers = HEADERS.copy()
        headers.update({'Content-Type': 'application/json'})
        headers.update({'X-Device': '1;22;0;12;1.0.00'})
        data = {"refresh_token": refresh_token}
        req = requests.post(f"{API_URL}/AuthenticationService/Token.json", json=data, headers=headers)
        access_token = json.loads(req.text)["access_token"]
        times_token = getTime_token(access_token)
        timeNEW = time.ctime(times_token)
        print(f"[{SOURCE}] token updated: [{timeNEW}]")
        logger.info(f"[{SOURCE}] token updated: [{timeNEW}]")
        with open(TOKEN_PATCH, 'w') as f:
            f.write(f"{refresh_token}\n{access_token}\n{times_token}")
        ACCESS_TOKEN = access_token
        TIMES_TOKEN = times_token
    return access_token, times_token

def getToken():
    if not os.path.isfile(TOKEN_PATCH):
        print(f"[{SOURCE}] not found token file: [{TOKEN_PATCH}]")
        logger.info(f"[{SOURCE}] not found token file: [{TOKEN_PATCH}]")
        return False
    with open(TOKEN_PATCH, 'r') as f:
        token_line = f.readlines()
    refresh_token = token_line[0].strip()
    access_token = token_line[1].strip()
    times_token = int( token_line[2].strip() )
    access_token, times_token = checkToken(refresh_token, access_token, times_token)
    return refresh_token, access_token, times_token

REFRESH_TOKEN, ACCESS_TOKEN, TIMES_TOKEN  = getToken()

class Scraper:
    def getHeaders(self):
        return HEADERS

    def Channels(self):
        LL=[]
        RET_STATUS = False
        TOKEN, _ = checkToken(REFRESH_TOKEN, ACCESS_TOKEN, TIMES_TOKEN)
        headers = HEADERS.copy()
        headers.update({'Content-Type': 'application/json'})
        headers.update({'Authorization': f"Bearer {TOKEN}"})
        data = {"epg_current_time":0,
                "need_epg":False,
                "need_list":True,
                "need_categories":False,
                "need_offsets":False,
                "need_hash":False,
                "need_icons":False,
                "need_big_icons":False}
        http = requests.post(f"{API_URL}/TvService/GetChannels.json", json=data, headers=headers).json()

        for cnLine in http["list"]:
            try:
                if not cnLine["available"]: continue
                chID = cnLine["id"]
                title = cnLine["name"]
                logo = cnLine["icon_url"]
                ids = utils.title_to_crc32(title)
                url = f"ext:{SOURCE}:http://{chID}"
                LL.append((ids, title, SOURCE, url, logo))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(SOURCE, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        TOKEN, _ = checkToken(REFRESH_TOKEN, ACCESS_TOKEN, TIMES_TOKEN)
        chID = lnk.replace('http://', '')
        data = {"without_auth": True, "channel_id": chID, "accept_scheme": ["HTTP_HLS"], "multistream": True}
        headers = HEADERS.copy()
        headers.update({'Content-Type': 'application/json'})
        headers.update({'Authorization': f"Bearer {TOKEN}"})
        headers.update({'X-Accept-Language': 'ru'})
        headers.update({'X-Device': '1;22;0;12;1.0.00'})
        http = requests.post(f"{API_URL}/TvService/OpenStream.json", json=data, headers=headers).json()
        try:
            if http["result"] == "OK":
                url_url = http["url"]
                if '.m3u8' in url_url:
                    return url_url
                return f"{url_url}.m3u8-del"
            else:
                print(f"[{SOURCE}] Error result: {http['result']}")
                logger.info(f"[{SOURCE}] Error result: {http['result']}")
                return ''
        except Exception as e:
            s_error = str(e).replace('<', '').replace('>', '')
            print(f"[{SOURCE}]: {s_error}")
            logger.info(f"[{SOURCE}]: {s_error}")
            return ''
