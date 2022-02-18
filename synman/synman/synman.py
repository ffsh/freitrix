#!python3
from synman.media import Media
from synman.user import User
from synman.rooms import Rooms
import click
import json
from tabulate import tabulate

@click.group()
def cli():
    pass

@cli.command()
@click.option("--list", "list_media", default=False, help="list media", is_flag=True)
@click.option("--clean", "clean_media", default=False, help="clean media", is_flag=True)
@click.option("--token", help="Admin Token from Matrix client", required=True)
def media(list_media, token):
    """Manage media files"""
    if list_media:
        my_media = Media(token)
        my_media.list_media()
    elif clean_media:
        my_media = Media(token)
        my_media.clean_media()

@cli.command()
@click.option("--clean", "clean", default=False, help="Removes empty rooms", is_flag=True)
@click.option("--token", help="Admin Token from Matrix client", required=True)
def rooms(clean, token):
    """Manage rooms"""
    if clean:
        my_room = Rooms(token)
        my_room.clean()

@cli.command()
@click.argument("user", required=True)
@click.option("--last-login", "last_login", help="Display last login of user.", required=True, is_flag=True)
@click.option("--delete", help="Delete the user based on GDPR standard.", required=True, is_flag=True)
@click.option("--token", help="Admin Token from Matrix client", required=True)
def user(user, last_login, delete, token):
    """Manage users"""
    my_user = User(token)
    if last_login:
        output = "Last login of {} was {}".format(user, my_user.get_last_login(user))
        print(output)
    elif delete:
        continue_delete = input(
            "Are you sure you want to delete the user {}, if yes please type \"Yes\": ".format(user))
        if continue_delete == "Yes":
            status, message = my_user.deactivate_user(user)

            if status == 200:
                print("User: {} was GDPR erased".format(user))
            else:
                message = json.loads(message)
                
                print("ERROR: Server responded with HTTP: {}".format(status))
                print("Type: {}\nMessage: {}".format(message["errcode"], message["error"]))
        else:
            print("Deletion of user {} was canceled".format(user))

@cli.command("list")
@click.option("--token", help="Admin Token from Matrix client", required=True)
@click.option("--json", "print_json", default=False, help="Print in json format instead of table.", is_flag=True)
@click.option("--all", default=False, help="Will also print deactivated users", is_flag=True)
def list_users(token, print_json=False, all=False):
    """List users"""
    my_user = User(token)

    print("List of users...")
    userList = my_user.get_users(deactivated=all)

    if (print_json):
        print(json.dumps(userList))
    else:
        print(tabulate(userList, headers=[
              "Name", "User Status", "E-Mail", "Creation date", "Last login"], tablefmt="presto"))
