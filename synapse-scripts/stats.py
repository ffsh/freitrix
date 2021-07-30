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

def rooms(token):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = 'Content-Type: application/json'
    headers["Authorization"] = "Bearer {}".format(token)

    r = requests.get('http://localhost:8008/_synapse/admin/v1/rooms?limit=10&order_by=joined_members', headers=headers)
    rooms = r.json()
    biggestRooms = []
    print("Biggest rooms sorted by members")
    for room in rooms["rooms"]:
        biggestRooms.append([room["name"], room["joined_members"], room["joined_local_members"], room["version"]])
    print(tabulate(biggestRooms, headers=["Name", "Members", "Local Members", "Version"]))

    r = requests.get('http://localhost:8008/_synapse/admin/v1/rooms?limit=10&order_by=joined_local_members', headers=headers)
    rooms = r.json()
    biggestRooms = []
    print("\nBiggest rooms sorted by local members")
    for room in rooms["rooms"]:
        biggestRooms.append([room["name"], room["joined_members"], room["joined_local_members"], room["version"]])
    print(tabulate(biggestRooms, headers=["Name", "Members", "Local Members", "Version"]))
  

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
