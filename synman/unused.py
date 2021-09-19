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