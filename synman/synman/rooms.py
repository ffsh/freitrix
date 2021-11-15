#!python3

import requests
import argparse


class Rooms():
    def __init__(self, token):
        self.headers = requests.structures.CaseInsensitiveDict()
        self.headers["Accept"] = "application/json"
        self.headers["Content-Type"] = 'Content-Type: application/json'
        self.headers["Authorization"] = "Bearer {}".format(token)

    def clean(self):
        body='{"message": "Room is empty therefore it is removed.", "block": false, "purge": true}'

        r = requests.get('http://localhost:8008/_synapse/admin/v1/rooms?limit=800', headers=self.headers)
        rooms = r.json()
        count=0
        for room in rooms["rooms"]:
            if room["joined_local_members"] == 0:
                count+=1
                print("ID: {}, has no local members".format(room["room_id"]))
                print("Name: {}".format(room["name"]))
                print("Alias: {}".format(room["canonical_alias"]))
                r2 = requests.delete('http://localhost:8008/_synapse/admin/v1/rooms/{}'.format(room["room_id"]), headers=self.headers, data=body)
                if r2.status_code == 200:
                    print("deleted")
                print("--------")
        print("{} rooms deleted.".format(count))

    






