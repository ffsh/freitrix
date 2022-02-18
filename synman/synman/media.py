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
        hoarder[4] = humanize.naturalsize(hoarder[4])
        return hoarder

    def list_media(self):
        r = requests.get('http://localhost:8008/_synapse/admin/v1/statistics/users/media?limit=100&order_by=media_length', headers=self.headers)
        medias = r.json()
        datahoarders = []
        print("Media Users sorted by size")

        for media in medias["users"]:
            r2 = requests.get('http://localhost:8008/_synapse/admin/v2/users/{}'.format(media["user_id"]), headers=self.headers)
            user = r2.json()

            if r2.status_code == 200:
                datahoarders.append([media["user_id"], user["deactivated"], media["displayname"], media["media_count"], media["media_length"]])
            else:
                datahoarders.append([media["user_id"], "N/A", media["displayname"], media["media_count"], media["media_length"]])

        datahoarders = sorted(datahoarders, key=lambda datahorder: datahorder[4], reverse=True)
        datahoarders = list(map(self.__convert_bytes, datahoarders))

        print(tabulate(datahoarders, headers=["userid", "deactivated", "displayname", "media_count", "media_length"]))

    def clean_media(self):
        r = requests.get('http://localhost:8008/_synapse/admin/v2/users?from=0&limit=200&guests=false&deactivated=true', headers=self.headers)
        users = r.json()

        for user in users["users"]:
            if user["deactivated"] == 1:
                print(user["name"], user["displayname"])