#!python3
from synman.media import Media
import click

@click.group()
def cli():
    pass

@cli.command()
@click.option("--list" "list_media", default=False, help="list media", is_flag=True)
@click.option("--token", help="Admin Token from Matrix client", required=True)
def media(list_media, token):
    if list_media:
        my_media = Media(token)
        my_media.list_media()