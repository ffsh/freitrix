#!python3

import requests
import json
from tabulate import tabulate


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

    def list_rooms(self):
        r = requests.get('http://localhost:8008/_synapse/admin/v1/rooms?limit=10&order_by=joined_members', headers=self.headers)
        rooms = r.json()
        biggestRooms = []
        print("Biggest rooms sorted by members")
        for room in rooms["rooms"]:
            biggestRooms.append([room["name"], room["joined_members"], room["joined_local_members"], room["version"]])
        print(tabulate(biggestRooms, headers=["Name", "Members", "Local Members", "Version"]))

        r = requests.get('http://localhost:8008/_synapse/admin/v1/rooms?limit=10&order_by=joined_local_members', headers=self.headers)
        rooms = r.json()
        biggestRooms = []
        print("\nBiggest rooms sorted by local members")
        for room in rooms["rooms"]:
            biggestRooms.append([room["name"], room["joined_members"], room["joined_local_members"], room["version"]])
        print(tabulate(biggestRooms, headers=["Name", "Members", "Local Members", "Version"]))
    
    def info(self, room):
        r = requests.get('http://localhost:8008/_synapse/admin/v1/rooms/{}'.format(room), headers=self.headers)
        rooms = r.json()
        print(json.dumps(rooms, indent=4))




