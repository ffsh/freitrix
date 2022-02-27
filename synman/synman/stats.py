#!python3

import requests
import argparse
from tabulate import tabulate
import humanize

def convert_bytes(hoarder):
    hoarder[3] = humanize.naturalsize(hoarder[3])
    return hoarder

def media(token):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = 'Content-Type: application/json'
    headers["Authorization"] = "Bearer {}".format(token)

    r = requests.get('http://localhost:8008/_synapse/admin/v1/statistics/users/media?limit=100&order_by=media_length', headers=headers)
    media = r.json()
    datahoarders = []
    print("Media Users sorted by size")
    for room in media["users"]:
        datahoarders.append([room["user_id"], room["displayname"], room["media_count"], room["media_length"]])
    datahoarders = sorted(datahoarders, key=lambda datahorder: datahorder[3], reverse=True)
    datahoarders = list(map(convert_bytes, datahoarders))
    print(tabulate(datahoarders, headers=["userid", "displayname", "media_count", "media_length"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='different stats')
    parser.add_argument('--token', help='token for authentication')
    parser.add_argument('--media', help='media stats', action='store_true')
    parser.add_argument('--rooms', help='room stats', action='store_true')
    args = parser.parse_args()
    if args.media:
        media(args.token)
    elif args.rooms:
        rooms(args.token)
