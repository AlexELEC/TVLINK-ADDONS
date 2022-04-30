# -*- coding: utf-8 -*-

import os, sys, json, time
import requests, uuid, re
from base64 import b64decode

root_dir = os.path.dirname(sys.argv[0])
cache_dir = os.path.join(root_dir, 'cache')
sys.path.append(root_dir)
import utils

EMAIL = "mail@email.com"
PASSW = "password"

# only free channels: True or False
ONLY_FREE = True

if not os.path.isdir(cache_dir): os.makedirs(cache_dir)

def getDevID():
    devid_patch = os.path.join(cache_dir, "YouTV.dev")
    if os.path.isfile(devid_patch):
        with open(devid_patch, 'r') as f:
            dev_id = f.readline()
    else:
        dev_id = uuid.uuid1().int
        with open(devid_patch, 'w') as f:
            f.write(f"{dev_id}")
    return str(dev_id)

DEV_ID = getDevID()

API_URL = 'https://api.youtv.com.ua'

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
           'Accept': 'application/vnd.youtv.v8+json',
           'Referer': 'https://youtv.ua/',
           'Device-Uuid': DEV_ID}

TOKEN_PATCH = os.path.join(cache_dir, "YouTV")

def refreshToken():
    data = {'email': EMAIL, 'password': PASSW}
    req = requests.post(f"{API_URL}/auth/login", data=data, headers=HEADERS)
    token = json.loads(req.text)["token"]
    with open(TOKEN_PATCH, 'w') as f:
        f.write(f"{token}")
    return token

def getToken():
    if os.path.isfile(TOKEN_PATCH):
        with open(TOKEN_PATCH, 'r') as f:
            token = f.readline()
        token.strip()
        token_cut = token.split('.')
        token_part = ''
        for i in range( len(token_cut) - 1 ):
            token_part += token_cut[i]
        token_part = token_part + '=' * (4 - len(token_part) % 4) if len(token_part) % 4 != 0 else token_part
        time_exp = b64decode(token_part).decode('utf-8')
        time_exp = re.search('"exp":(.*?),"', time_exp, re.IGNORECASE).group(1)
        if int( time.time() ) < int(time_exp) - 10000:
            return token
        else:
            return refreshToken()
    else:
        return refreshToken()

TOKEN = getToken()


class Scraper:
    def __init__(self):
        self.source = 'YouTV'
        self.link = f'ext:{self.source}:'
        self.headers = HEADERS

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        global TOKEN
        TOKEN = getToken()
        self.headers.update({'Content-Type': 'text/plain; charset=UTF-8'})
        self.headers.update({'Authorization': f"Bearer {TOKEN}"})
        http = requests.post(f"{API_URL}/playlist", headers=self.headers)
        L = json.loads(http.text)["data"]

        for cnLine in L:
            try:
                if ONLY_FREE and not cnLine["source"]["free"]:
                    continue
                group = self.source
                groups = cnLine["categories"]
                try:
                    for grpLine in groups:
                        group = grpLine['name']
                        break
                except: pass
                if group == "Радио": continue
                title = cnLine["name"]
                lnk = cnLine["source"]["stream"]["url"]
                ids = utils.title_to_crc32(title)
                logo = cnLine["image"]
                url = f"{self.link}{lnk}"
                LL.append((ids, title, group, url, logo))
            except: pass

        if LL:
            # Loading a Tuple into a Database (source, Tuple)
            utils.ch_inputs_DB(self.source, LL)

    def getLink(self, lnk):
        self.headers.update({'Authorization': f"Bearer {TOKEN}"})
        http = requests.get(lnk, headers=self.headers)
        url = 'https:' + json.loads(http.text)["p"]
        return url
