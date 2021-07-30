#!python3

import requests
import argparse
import datetime
import json
from tabulate import tabulate

def convert_ts(user):
    user[2] = str(datetime.datetime.fromtimestamp(user[2]))
    return user

def list_users(token, print_json=False):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = 'Content-Type: application/json'
    headers["Authorization"] = "Bearer {}".format(token)

    r = requests.get('http://localhost:8008/_synapse/admin/v2/users?from=0&guests=false', headers=headers)
    users = r.json()
    userList = []
    print("List of users")
    for user in users["users"]:
        r2 = requests.get('http://localhost:8008/_synapse/admin/v2/users/{}'.format(user["name"]), headers=headers)
        user_account = r2.json()
        user_email = ""
        for threepid in user_account["threepids"]:
            if threepid["medium"] == "email":
                if user_email == "":
                    user_email = threepid["address"]
                else:
                    user_email = user_email+" "+threepid["address"]

        userList.append([user["name"], user_email, user_account["creation_ts"]])

    userList = sorted(userList, key=lambda user: user[2], reverse=False)
    userList = list(map(convert_ts, userList))

    if (print_json):
        print(json.dumps(userList))
    else:
        print(tabulate(userList, headers=["Name", "E-Mail", "Creation date"], tablefmt="presto"))

def inform_user(user, token):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = 'Content-Type: application/json'
    headers["Authorization"] = "Bearer {}".format(token)

    deadline = datetime.datetime.now() + datetime.timedelta(days=30)
    deadline = deadline.strftime('%d.%m.%Y')

    message = "Hallo {},\nleider kommt es im Matrix Universum verstärkt zu Spam Angriffen, \
daher möchten wir Dich bitten deinen Account mit einer E-Mail-Adresse zu verknüpfen.\n\
https://freifunk-suedholstein.de/freitrix-account-validieren/\n\
Wenn du Fragen hast kannst du unserem info Raum beitreten: #info:freitrix.de\n\
Du hast dafür 30 Tage Zeit, solltest Du bis dahin keine E-Mail mit Deinem Account verknüpft haben, \
müssen wir Deinen Account leider löschen, da wir davon ausgehen müssen, dass es sich um einen Spam-Account handelt.\n\
Die Frist endet am: {}\n".format(user, deadline)

    body = {
    "user_id": user,
    "content": {
        "msgtype": "m.text",
        "body": message
        }
    }

    r = requests.post('http://localhost:8008/_synapse/admin/v1/send_server_notice', headers=headers, data=json.dumps(body))
    print("Server says: {}".format(r))
    print("User: {}, deadline: {}".format(user, deadline))








# def deactivate_user(token, id):
#     headers = requests.structures.CaseInsensitiveDict()
#     headers["Accept"] = "application/json"
#     headers["Content-Type"] = 'Content-Type: application/json'
#     headers["Authorization"] = "Bearer {}".format(token)

#     r = requests.get('http://localhost:8008/_synapse/admin/v2/users?from=0&guests=false', headers=headers)
#     users = r.json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='List users')
    parser.add_argument('--token', help='token for authentication')
    parser.add_argument('--list', help='list user', action='store_true')
    parser.add_argument('--json', help='print as json', action='store_true')
    parser.add_argument('--inform', help='room stats', action='store', dest="user", type=str)
    args = parser.parse_args()
    if args.list:
        list_users(args.token, args.json)
    elif args.user != None:
        inform_user(args.user, args.token)
    else:
        parser.print_usage()