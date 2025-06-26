# -*- coding: utf-8 -*-

import os, sys, json, time
import requests
from pathlib import Path
from uuid import uuid1
from base64 import b64decode

root_dir = os.path.dirname(sys.argv[0])
cache_dir = os.path.join(root_dir, 'cache')
if not root_dir in sys.path: sys.path.append(root_dir)

import utils
from utils import logger, DEF_BROWSER

if not os.path.isdir(cache_dir): os.makedirs(cache_dir)

SOURCE = Path(__file__).stem
TOKEN_PATCH = os.path.join(cache_dir, SOURCE)

API_URL = 'https://api.vivat.live/stable'

HEADERS = {'User-Agent': DEF_BROWSER,
           'Accept': '*/*',
           'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
           'Connection': 'keep-alive',
           'Referer': 'https://vivat.live/',
          }

def getTime_token(token):
    access_cut = token.split('.')
    access_part = ''
    for i in range( len(access_cut) - 1 ):
        access_part += access_cut[i]
    access_part = access_part + '=' * (4 - len(access_part) % 4) if len(access_part) % 4 != 0 else access_part
    time_exp = b64decode(access_part).decode('utf-8')
    time_exp = utils.mfind(time_exp, '"exp":', ',"type"')
    return int(time_exp)

def checkToken(access_token, refresh_token, times_token, dev_id):
    if int( time.time() ) > times_token - 600:
        global ACCESS_TOKEN
        global REFRESH_TOKEN
        global TIMES_TOKEN
        timeOLD = time.ctime(times_token)
        print(f"[{SOURCE}] token expired: [{timeOLD}]")
        logger.info(f"[{SOURCE}] token expired: [{timeOLD}]")
        headers = HEADERS.copy()
        headers.update({'Accept': 'application/json, text/plain, */*'})
        headers.update({'Authorization': f"Bearer {access_token}"})
        lnk = f"{API_URL}/sign?deviceId={dev_id}&deviceType=2&language=uk&profileId=1&refreshToken={refresh_token}"
        req = requests.get(lnk, headers=headers)
        access_token = json.loads(req.text)["accessToken"]
        refresh_token = json.loads(req.text)["refreshToken"]
        times_token = getTime_token(access_token)
        timeNEW = time.ctime(times_token)
        print(f"[{SOURCE}] token updated: [{timeNEW}]")
        logger.info(f"[{SOURCE}] token updated: [{timeNEW}]")
        with open(TOKEN_PATCH, 'w') as f:
            f.write(f"{access_token}\n{refresh_token}\n{times_token}\n{dev_id}")
        ACCESS_TOKEN = access_token
        REFRESH_TOKEN = refresh_token
        TIMES_TOKEN = times_token
    return access_token, refresh_token, times_token, dev_id

def getToken():
    if os.path.isfile(TOKEN_PATCH):
        with open(TOKEN_PATCH, 'r') as f:
            token_line = f.readlines()
        access_token = token_line[0].strip()
        refresh_token = token_line[1].strip()
        times_token = int(token_line[2].strip())
        dev_id = token_line[3].strip()
    else:
        access_token='unknown'
        refresh_token=''
        times_token=0
        dev_id = str(uuid1().hex[:21])

    return checkToken(access_token, refresh_token, times_token, dev_id)

ACCESS_TOKEN, REFRESH_TOKEN, TIMES_TOKEN, DEV_ID = getToken()


class Scraper:
    def getHeaders(self):
        return HEADERS

    def Channels(self):
        LL=[]
        RET_STATUS = False
        TOKEN, _at, _tt, _id = checkToken(ACCESS_TOKEN, REFRESH_TOKEN, TIMES_TOKEN, DEV_ID)
        headers = HEADERS.copy()
        headers.update({'Accept': 'application/json, text/plain, */*'})
        headers.update({'Authorization': f"Bearer {TOKEN}"})
        lnk = f"{API_URL}/content?contentTypes=1&favorite=0&genreIds=0&limit=1000&deviceId={DEV_ID}&deviceType=2&language=ru&profileId=1"
        http = requests.get(lnk, headers=headers).json()

        for cnLine in http:
            try:
                if not cnLine["isAvailable"]: continue
                chID = cnLine["urls"]
                title = cnLine["title"]
                img = cnLine["images"]
                logo = f"https://api.hmara.tv/images/saved/{img}"
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
        TOKEN, _at, _tt, _id = checkToken(ACCESS_TOKEN, REFRESH_TOKEN, TIMES_TOKEN, DEV_ID)
        chID = lnk.replace('http://', '')
        headers = HEADERS.copy()
        headers.update({'Accept': 'application/json, text/plain, */*'})
        headers.update({'Authorization': f"Bearer {TOKEN}"})
        lnk = f"{API_URL}/content2/play?urlId={chID}&deviceId={DEV_ID}&deviceType=2&language=ru&profileId=1"
        http = requests.get(lnk, headers=headers).text
        try:
            return requests.get(lnk, headers=headers).text
        except:
            print(f"[{SOURCE}] Error: {http}")
            logger.info(f"[{SOURCE}] Error: {http}")
            return ''
