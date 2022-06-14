#!python3

import requests
import json
import time
from tabulate import tabulate


class Rooms():
    def __init__(self, token):
        self.headers = requests.structures.CaseInsensitiveDict()
        self.headers["Accept"] = "application/json"
        self.headers["Content-Type"] = 'Content-Type: application/json'
        self.headers["Authorization"] = "Bearer {}".format(token)

    def clean_helper(self, room_id):
        body='{"message": "Room is empty therefore it is removed.", "block": false, "purge": true}'
        deleted = False

        r = requests.delete('http://localhost:8008/_synapse/admin/v2/rooms/{}'.format(room_id), headers=self.headers, data=body)
        if r.status_code == 200:
            deletion_id = r.json()["delete_id"]
            while not deleted:
                deletion_status = self.del_status_helper(deletion_id)
                if deletion_status == "complete":
                    deleted = True
                else:
                    time.sleep(5)
            return "Room was deleted."
        else:
            return r.json()

    def clean(self):
        r = requests.get('http://localhost:8008/_synapse/admin/v1/rooms?limit=800', headers=self.headers)
        rooms = r.json()
        count=0
        for room in rooms["rooms"]:
            if room["joined_local_members"] == 0:
                count+=1
                print("ID: {}, has no local members".format(room["room_id"]))
                print("Name: {}".format(room["name"]))
                print("Alias: {}".format(room["canonical_alias"]))
                self.clean_helper(room["room_id"])
                print("--------")
        print("{} rooms were deleted.".format(count))

    def del_status_helper(self, deletion_id):
        r = requests.get('http://localhost:8008/_synapse/admin/v2/rooms/delete_status/{}'.format(deletion_id), headers=self.headers)
        
        status = r.json()

        if status['status'] == "complete":
            return "complete"
        elif status['status'] == "purging":
            return "purging"
        elif status['status'] == "shutting_down":
            return "shutting_down"
        elif status['status'] == "failed":
            return "failed: {}".format(status["error"])

    def del_status(self, deletion_id):
        print(self.del_status_helper(deletion_id))

    def purge_history(self, room_id, timestamp):
        body = {
            "purge_up_to_ts": timestamp
        }
        r = requests.post('http://localhost:8008/_synapse/admin/v1/purge_history/{}'.format(room_id), 
            headers=self.headers, data=json.dumps(body))
        if r.status_code == 200:
            print("Purge ID:", r.json()["purge_id"])
        else:
            print("ERROR:")
            print(r.json())
    
    def purge_status_helper(self, purge_id):
        r = requests.get('http://localhost:8008/_synapse/admin/v1/purge_history_status/{}'.format(purge_id), headers=self.headers)
        status = r.json()

        if status['status'] == "complete":
            return "complete"
        elif status['status'] == "active":
            return "active"
        elif status['status'] == "failed":
            return "failed: {}".format(status["error"])

    def purge_status(self, purge_id):
        print(self.purge_status_helper(purge_id))

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

        r = requests.get('http://localhost:8008/_synapse/admin/v1/rooms?limit=10&order_by=state_events', headers=self.headers)
        rooms = r.json()
        biggestRooms = []
        print("\nBiggest rooms sorted by state events")
        for room in rooms["rooms"]:
            biggestRooms.append([room["room_id"], room["name"], room["joined_members"], room["joined_local_members"], room["version"], room["state_events"]])
        print(tabulate(biggestRooms, headers=["ID", "Name", "Members", "Local Members", "Version", "Events"]))
    
    def info(self, room):
        r = requests.get('http://localhost:8008/_synapse/admin/v1/rooms/{}'.format(room), headers=self.headers)
        rooms = r.json()
        print(json.dumps(rooms, indent=4))




