# -*- coding: utf-8 -*-

import os, sys, json
import requests
from pathlib import Path

root_dir = os.path.dirname(sys.argv[0])
cache_dir = os.path.join(root_dir, 'cache')
if not root_dir in sys.path: sys.path.append(root_dir)

import utils

SOURCE = Path(__file__).stem

if not os.path.isdir(cache_dir): os.makedirs(cache_dir)
devid_patch = os.path.join(cache_dir, f"{SOURCE}.dev")

def getDevID():
    if os.path.isfile(devid_patch):
        with open(devid_patch, 'r') as f:
            dev_id = f.readline()
    else:
        import uuid
        dev_id = uuid.uuid4().int
        with open(devid_patch, 'w') as f:
            f.write(f"{dev_id}")
    return str(dev_id)

DEV_ID = getDevID()


class Scraper:
    def __init__(self):
        self.link = f'ext:{SOURCE}:'
        self.api_url = 'https://api.youtv.com.ua'
        self.headers = {'user-agent': 'youtv/3.23.13+8004 (Samsung MB2; Android; 6.0.1; Mobile; null; MHC19J.20170619.091635 test-keys; 1920x1008)',
                        'accept': 'application/vnd.youtv.v9+json',
                        'device-uuid': DEV_ID,
                        'applicationid': 'ua.youtv.youtv',
                        'device': 'mobile',
                        'restriction': 'uhd:true;4k:true;8k:true;hdr:false;adult:true;children:false'}

    def getHeaders(self):
        return self.headers

    def Channels(self):
        LL=[]
        RET_STATUS = False
        http = requests.post(f"{self.api_url}/playlist", headers=self.headers)
        L = json.loads(http.text)["data"]

        for cnLine in L:
            try:
                if not cnLine["source"]["free"]:
                    continue
                group = SOURCE
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
            utils.ch_inputs_DB(SOURCE, LL)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        http = requests.get(lnk, headers=self.headers)
        url = json.loads(http.text)["p"]
        return url
