#!python3

import requests
import click
import datetime
import json
from tabulate import tabulate

@click.group()
def cli():
    pass

def convert_ts(user):
    user[3] = str(datetime.datetime.fromtimestamp(user[3]))
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

"""
Return last login by user in terminal
"""
@cli.command("last-login")
@click.option("--token", help="Admin Token from Matrix client", required=True)
@click.argument("user", required=True)
def last_login(token, user):
    print(get_last_login(token ,user))

"""
Determine most important status
"""
def get_user_status(user):
    user_status = "normal"
    if user["admin"] == 1:
        user_status = "admin"
    if user["shadow_banned"] == 1:
        user_status = "shadow banned"
    if user["deactivated"] == 1:
        user_status = "deactivated"
    return user_status

"""
Retuns list of users
"""
def get_users(token, deactivated=False):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = 'Content-Type: application/json'
    headers["Authorization"] = "Bearer {}".format(token)

    if deactivated:
        include_deactivated = "true"
    else:
        include_deactivated = "false"

    r = requests.get('http://localhost:8008/_synapse/admin/v2/users?from=0&limit=200&guests=false&deactivated={}'.format(include_deactivated), headers=headers)
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
        
        userList.append([user["name"], 
                        get_user_status(user), 
                        user_email,
                        user_account["creation_ts"],
                        get_last_login(token, user["name"])
                        ])

    userList = sorted(userList, key=lambda user: user[3], reverse=False)
    userList = list(map(convert_ts, userList))

    return userList

"""
List users in terminal as table or as json
"""
@cli.command("list")
@click.option("--token", help="Admin Token from Matrix client", required=True)
@click.option("--json", "print_json", default=False, help="Print in json format instead of table.", is_flag=True)
@click.option("--all", default=False, help="Will also print deactivated users", is_flag=True)
def list_users(token, print_json=False, all=False):
    print("List of users...")
    userList = get_users(token, deactivated=all)

    if (print_json):
        print(json.dumps(userList))
    else:
        print(tabulate(userList, headers=["Name", "User Status", "E-Mail", "Creation date", "Last login"], tablefmt="presto"))

"""
Delete a single user
"""
@cli.command("delete")
@click.argument("user", required=True)
@click.option("--token", help="Admin Token from Matrix client", required=True)
def deactivate_user(user, token):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = 'Content-Type: application/json'
    headers["Authorization"] = "Bearer {}".format(token)

    body = {
    "erase": True
    }

    continue_delete = input("Are you sure you want to delete the user {}, if yes please type \"Yes\": ".format(user))
    if continue_delete == "Yes":
        r = requests.post('http://localhost:8008/_synapse/admin/v1/deactivate/{}'.format(user), headers=headers, data=json.dumps(body))
        print("Server says: {}".format(r))
        print("User: {} was GDPR erased".format(user))
        pass
    else:
        print("Deletion of user {} was canceled".format(user))

if __name__ == "__main__":
    cli()
