#!python3

import requests
import argparse
import datetime
import json
from tabulate import tabulate

def convert_ts(user):
    user[2] = str(datetime.datetime.fromtimestamp(user[2]))
    return user

def get_last_login(token, user):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = 'Content-Type: application/json'
    headers["Authorization"] = "Bearer {}".format(token)

    r = requests.get('http://localhost:8008/_synapse/admin/v1/whois/{}'.format(user), headers=headers)
    
    biggest_timestamp = 0

    if r.status_code == 200:
        user_sessions = r.json()
        #print(user_sessions)
        for session in user_sessions["devices"][""]["sessions"]:
            for connection in session["connections"]:
                if connection["last_seen"] > biggest_timestamp:
                    biggest_timestamp = connection["last_seen"]
        return datetime.datetime.fromtimestamp(biggest_timestamp//1000)
    else:
        return ""

def get_users(token):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = 'Content-Type: application/json'
    headers["Authorization"] = "Bearer {}".format(token)

    r = requests.get('http://localhost:8008/_synapse/admin/v2/users?from=0&guests=false', headers=headers)
    users = r.json()
    userList = []
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

        userList.append([user["name"], user_email, user_account["creation_ts"], get_last_login(token, user["name"])])

    userList = sorted(userList, key=lambda user: user[2], reverse=False)
    userList = list(map(convert_ts, userList))

    return userList

"""
List users in terminal as table or as json
"""
def list_users(token, print_json=False):
    print("List of users...")
    userList = get_users(token)

    if (print_json):
        print(json.dumps(userList))
    else:
        print(tabulate(userList, headers=["Name", "E-Mail", "Creation date", "Last login"], tablefmt="presto"))


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
Wenn du Fragen hast, kannst du unserem info Raum beitreten: #info:freitrix.de\n\
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

def remind_user(user, token):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = 'Content-Type: application/json'
    headers["Authorization"] = "Bearer {}".format(token)

    message = "Hallo {},\nbitte denke daran, Deinen Account vor Ablauf der Frist (10.09) zu verifzieren,\n\
sonst müssen wir Deinen Account leider löschen, die E-Mail-Adresse muss mit deinem Account verknüpft bleiben.\n\
Dein Account hat akutell keine E-Mail-Adresse und ist damit von der Löschung betroffen.\n\
https://freifunk-suedholstein.de/freitrix-account-validieren/\n\
Wenn du Fragen hast, kannst du unserem info Raum beitreten: #info:freitrix.de".format(user)

    body = {
    "user_id": user,
    "content": {
        "msgtype": "m.text",
        "body": message
        }
    }

    r = requests.post('http://localhost:8008/_synapse/admin/v1/send_server_notice', headers=headers, data=json.dumps(body))
    print("Server says: {}".format(r))
    print("User: {} was reminded".format(user))

def unverified(user):
    if user[1] == "":
        return True
    else:
        return False

def find_user(condition, token):
    if condition == "unverified":
        print()
        userList = get_users(token)
        unverified_userList = filter(unverified, userList)
        return unverified_userList

def remind_all(token):
    unverified_userList = find_user("unverified", token)
    for user in unverified_userList:
        remind_user(user[0], token)

def deactivate_user(user, token):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = 'Content-Type: application/json'
    headers["Authorization"] = "Bearer {}".format(token)

    body = {
    "erase": True
    }

    r = requests.post('http://localhost:8008/_synapse/admin/v1/deactivate/{}'.format(user), headers=headers, data=json.dumps(body))
    print("Server says: {}".format(r))
    print("User: {} was GDPR erased".format(user))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='List users')
    parser.add_argument('--token', help='token for authentication')
    parser.add_argument('--list', help='list user', action='store_true')
    parser.add_argument('--json', help='print as json', action='store_true')
    parser.add_argument('--inform', help='inform single user, currently unverified text', action='store', dest="user_inform", type=str)
    parser.add_argument('--remind', help='remind single user', action='store', dest="user_remind", type=str)
    parser.add_argument('--remind_all', help='remind all unverfied users', action='store_true')
    parser.add_argument('--delete', help='delete single user', action='store', dest="user_delete", type=str)
    parser.add_argument('--last_login', help='last login of user', action='store', dest="user_last_login", type=str)
    args = parser.parse_args()
    if args.list:
        list_users(args.token, args.json)
    elif args.user_inform != None:
        inform_user(args.user_inform, args.token)
    elif args.user_remind != None:
        remind_user(args.user_remind, args.token)
    elif args.remind_all:
        remind_all(args.token)
    elif args.user_delete != None:
        continue_delete = input("Are you sure you want to delete the user {}, if yes please type \"Yes\": ".format(args.user_delete))
        if continue_delete == "Yes":
            deactivate_user(args.user_delete, args.token)
        else:
            print("Deletion of user {} was canceled".format(args.user_delete))
    elif args.user_last_login != None:
        print(get_last_login(args.token, args.user_last_login))
    else:
        parser.print_usage()
