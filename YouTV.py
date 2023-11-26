# -*- coding: utf-8 -*-

import os, sys, json
import requests, uuid

root_dir = os.path.dirname(sys.argv[0])
cache_dir = os.path.join(root_dir, 'cache')
sys.path.append(root_dir)

import utils

if not os.path.isdir(cache_dir): os.makedirs(cache_dir)

class Scraper:
    def __init__(self):
        self.source = 'YouTV'
        self.link = f'ext:{self.source}:'
        self.api_url = 'https://api.youtv.com.ua'
        self.dev_id = self.getDevID()
        self.headers = {'user-agent': 'youtv/3.23.13+8004 (Samsung MB2; Android; 6.0.1; Mobile; null; MHC19J.20170619.091635 test-keys; 1920x1008)',
                        'accept': 'application/vnd.youtv.v9+json',
                        'device-uuid': self.dev_id,
                        'applicationid': 'ua.youtv.youtv',
                        'device': 'mobile',
                        'restriction': 'uhd:true;4k:true;8k:true;hdr:false;adult:true;children:false'}

    def getHeaders(self):
        return self.headers

    def getDevID(self):
        devid_patch = os.path.join(cache_dir, f"{self.source}.dev")
        if os.path.isfile(devid_patch):
            with open(devid_patch, 'r') as f:
                dev_id = f.readline()
        else:
            dev_id = uuid.uuid4().int
            with open(devid_patch, 'w') as f:
                f.write(f"{dev_id}")
        return str(dev_id)

    def Channels(self):
        LL=[]
        http = requests.post(f"{self.api_url}/playlist", headers=self.headers)
        L = json.loads(http.text)["data"]

        for cnLine in L:
            try:
                if not cnLine["source"]["free"]:
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
        http = requests.get(lnk, headers=self.headers)
        url = json.loads(http.text)["p"]
        return url
