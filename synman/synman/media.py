#!python3

import requests
import argparse
from tabulate import tabulate
import humanize

class Media:
    def __init__(self, token):
        self.headers = requests.structures.CaseInsensitiveDict()
        self.headers["Accept"] = "application/json"
        self.headers["Content-Type"] = 'Content-Type: application/json'
        self.headers["Authorization"] = "Bearer {}".format(token)

    def __convert_bytes(self, hoarder):
        hoarder[3] = humanize.naturalsize(hoarder[3])
        return hoarder

    def list_media(self):
        r = requests.get('http://localhost:8008/_synapse/admin/v1/statistics/users/media?limit=100&order_by=media_length', headers=self.headers)
        media = r.json()
        datahoarders = []
        print("Media Users sorted by size")
        for room in media["users"]:
            datahoarders.append([room["user_id"], room["displayname"], room["media_count"], room["media_length"]])
        datahoarders = sorted(datahoarders, key=lambda datahorder: datahorder[3], reverse=True)
        datahoarders = list(map(self.__convert_bytes, datahoarders))
        print(tabulate(datahoarders, headers=["userid", "displayname", "media_count", "media_length"]))