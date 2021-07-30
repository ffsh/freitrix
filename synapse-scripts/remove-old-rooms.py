#!python3

import requests
import argparse

def main(token):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = 'Content-Type: application/json'
    headers["Authorization"] = "Bearer {}".format(token)
    body='{"message": "Room is empty therefore it is removed.", "block": false, "purge": true}'

    r = requests.get('http://localhost:8008/_synapse/admin/v1/rooms?limit=800', headers=headers)
    rooms = r.json()
    count=0
    for room in rooms["rooms"]:
        if room["joined_local_members"] == 0:
            count+=1
            print(room["room_id"])
            print(room["name"])
            #print(room[""])
            r2 = requests.delete('http://localhost:8008/_synapse/admin/v1/rooms/{}'.format(room["room_id"]), headers=headers, data=body)
            if r2.status_code == 200:
                print("deleted")
            print("--------")
    print("{} rooms deleted.".format(count))

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Remove old rooms')
    parser.add_argument('--token', help='token for authentication')
    args = parser.parse_args()
    main(args.token)




