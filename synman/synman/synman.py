#!python3
from synman.media import Media
from synman.user import User
from synman.rooms import Rooms
from synman.reports import Reports
import click
import json
from tabulate import tabulate
from datetime import (datetime, timedelta)

@click.group()
def cli():
    pass

@cli.command()
@click.argument("event_id", required=False)
@click.option("--read", "read", default=False, help="Read reports", is_flag=True)
@click.option("--detail", "detail", default=False, help="Detail reports", is_flag=True)
@click.option("--token", help="Admin Token from Matrix client", required=True)
def report(read, event_id, detail, token):
    """Manage reports"""
    my_report = Reports(token)
    if read:
        my_report.read()
    elif detail:
        if event_id is not None:
            my_report.detail(event_id)

@cli.command()
@click.option("--list", "list_media", default=False, help="list media", is_flag=True)
@click.option("--clean", "clean_media", default=False, help="clean media", is_flag=True)
@click.option("--delete", "delete_date", default=False, help="delete old media", is_flag=True)
@click.option("--token", help="Admin Token from Matrix client", required=True)
def media(list_media, clean_media, delete_date, token):
    """Manage media files"""
    my_media = Media(token)
    if list_media:
        my_media.list_media()
    elif clean_media:
        my_media.clean_media()
    elif delete_date:
        timestamp = int((datetime.now() - timedelta(days=356)).timestamp() * 1000)
        timestamp2 = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
        my_media.delete_local_date(timestamp)
        my_media.delete_cache_date(timestamp2)

@cli.command()
@click.argument("room", required=False)
@click.option("--clean", "clean", default=False, help="Removes empty rooms", is_flag=True)
@click.option("--delete-status", "delete_status", help="Returns deletion status, --delete-status DELETION_ID")
@click.option("--purge-history", "purge_history", help="purge history up to 1 year of a given room by room id, --purge-history ROOM_ID")
@click.option("--short", "short", default=False, help="purge history of room up to 30 days ago instead of 1 year", is_flag=True)
@click.option("--purge-status", "purge_status", help="Returns purge status, --purge-status PURGE_ID")
@click.option("--list", "list_rooms", default=False, help="List rooms", is_flag=True)
@click.option("--info", "info", default=False, help="Info about room", is_flag=True)
@click.option("--token", help="Admin Token from Matrix client", required=True)
def rooms(clean, list_rooms, info, room, token, delete_status, purge_history, purge_status, short):
    """Manage rooms"""
    my_room = Rooms(token)
    if clean:
        my_room.clean()
    elif list_rooms:
        my_room.list_rooms()
    elif info:
        if room is not None:
            my_room.info(room)
    elif delete_status:
        my_room.del_status(delete_status)
    elif purge_history:
        one_month_ago = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
        one_year_ago = int((datetime.now() - timedelta(days=356)).timestamp() * 1000)
        #print(purge_history[0], purge_history[1])
        if short:
            my_room.purge_history(purge_history, one_month_ago)
        else:
            my_room.purge_history(purge_history, one_year_ago)
    elif purge_status:
        my_room.purge_status(purge_status)

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
