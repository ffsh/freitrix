#!python3

import requests
import click
import datetime
import json


class User:
    def __init__(self, token):
        self.headers = requests.structures.CaseInsensitiveDict()
        self.headers["Accept"] = "application/json"
        self.headers["Content-Type"] = 'Content-Type: application/json'
        self.headers["Authorization"] = "Bearer {}".format(token)

    def __convert_ts(self, user):
        user[3] = str(datetime.datetime.fromtimestamp(user[3]))
        return user

    """
    Determine most important status
    """

    def __user_status(self, user):
        user_status = "normal"
        if user["admin"] == 1:
            user_status = "admin"
        if user["shadow_banned"] == 1:
            user_status = "shadow banned"
        if user["deactivated"] == 1:
            user_status = "deactivated"
        return user_status

    """
    Calculates the last login of a user, if no data is found the date will be 1970...
    """
    def get_last_login(self, user):
        r = requests.get(
            'http://localhost:8008/_synapse/admin/v1/whois/{}'.format(user), headers=self.headers)

        biggest_timestamp = 0

        if r.status_code == 200:
            user_sessions = r.json()
            for session in user_sessions["devices"][""]["sessions"]:
                for connection in session["connections"]:
                    if connection["last_seen"] > biggest_timestamp:
                        biggest_timestamp = connection["last_seen"]
            return datetime.datetime.fromtimestamp(biggest_timestamp//1000)
        else:
            return ""

    """
    Retuns list of users
    """

    def get_users(self, deactivated=False):
        if deactivated:
            include_deactivated = "true"
        else:
            include_deactivated = "false"

        r = requests.get('http://localhost:8008/_synapse/admin/v2/users?from=0&limit=200&guests=false&deactivated={}'.format(
            include_deactivated), headers=self.headers)
        users = r.json()
        userList = []
        for user in users["users"]:
            r2 = requests.get(
                'http://localhost:8008/_synapse/admin/v2/users/{}'.format(user["name"]), headers=self.headers)
            user_account = r2.json()
            user_email = ""
            for threepid in user_account["threepids"]:
                if threepid["medium"] == "email":
                    if user_email == "":
                        user_email = threepid["address"]
                    else:
                        user_email = user_email+" "+threepid["address"]

            userList.append([user["name"],
                            self.__user_status(user),
                            user_email,
                            user_account["creation_ts"],
                            self.get_last_login(user["name"])
                             ])

        userList = sorted(userList, key=lambda user: user[3], reverse=False)
        userList = list(map(self.__convert_ts, userList))

        return userList

    
    def deactivate_user(self, user):
        """ Delete a single user """
        body = {
            "erase": True
        }
        r = requests.post('http://localhost:8008/_synapse/admin/v1/deactivate/{}'.format(
            user), headers=self.headers, data=json.dumps(body))
        return r.status_code, r.content
