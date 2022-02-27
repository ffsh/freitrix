#!python3

import requests
import json
from tabulate import tabulate


class Reports():
    def __init__(self, token):
        self.headers = requests.structures.CaseInsensitiveDict()
        self.headers["Accept"] = "application/json"
        self.headers["Content-Type"] = 'Content-Type: application/json'
        self.headers["Authorization"] = "Bearer {}".format(token)

    def read(self):
        r = requests.get('http://localhost:8008/_synapse/admin/v1/event_reports?from=0&limit=20', headers=self.headers)
        rooms = r.json()
        print(json.dumps(rooms, indent=4))

    def detail(self, event_id):
        r = requests.get('http://localhost:8008/_synapse/admin/v1/event_reports/{}'.format(event_id), headers=self.headers)
        rooms = r.json()
        print(json.dumps(rooms, indent=4))


