# -*- coding: utf-8 -*-

import os, sys
from pathlib import Path

root_dir = os.path.dirname(sys.argv[0])
sys.path.append(root_dir)

from utils import StalkerPortal, ch_inputs_DB

# only include Groups: INCLUDE_GROUP = ['UKRAINE', 'USA']
INCLUDE_GROUP = []

class Scraper:
    def __init__(self):
        self.source = Path(__file__).stem
        self.portal = StalkerPortal(self.source, INCLUDE_GROUP)

    def getHeaders(self):
        return self.portal.headers

    def Channels(self):
        RET_STATUS = False
        DATA = self.portal.Channels()
        if DATA:
            ch_inputs_DB(self.source, DATA)
            RET_STATUS = True

        return RET_STATUS

    def getLink(self, lnk):
        return self.portal.getLink(lnk)
