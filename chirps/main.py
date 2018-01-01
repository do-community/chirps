#!/usr/bin/env python3
"""
Main Twitter bot script which glues everything together and starts the managers.
"""
import os
import argparse
from urllib import parse
import psycopg2
from twitter import Twitter, OAuth, TwitterStream
# Useful boilerplate functions for the overall Twitter bot.
import chirps.functions as functions
# Useful classes for streaming and account handling.
import chirps.managers as managers

# A different idea - use cookies to visit shortened links via visitors' devices.
# Maybe we can utilize 'RT to win' stuff by this same script.
# Use the below link for image search.
# https://www.google.co.in/search?site=imghp&tbm=isch&source=hp&biw=1280&bih=647&q=sample+query
# Also post images in replies.

parser = argparse.ArgumentParser()
# Add more argumets to choose follows, retweets and more...
parser.add_argument("-r", "--rate", default=60,
    help="rate at which tweets are sent", type=int)
parser.add_argument("--fav", help="flag to enable favoriting tweets",
    type=bool, default=True)
parser.add_argument("--retweet", help="flag to enable retweeting",
    type=bool, default=True)
parser.add_argument("--follow", help="flag to enable following people",
    type=bool, default=True)
parser.add_argument("--scrape", help="flag to enable content scraping",
    type=bool, default=True)
args = parser.parse_args()

try:
    from chirps.credentials import *
except ModuleNotFoundError:
    ACCESS_TOKEN = os.environ['ACCESS_TOKEN'],
    ACCESS_SECRET = os.environ['ACCESS_SECRET'],
    CONSUMER_KEY = os.environ['CONSUMER_KEY'],
    CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
    
    SHORTE_ST_TOKEN = os.environ['SHORTE_ST_TOKEN']
    DATABASE_URL = os.environ["DATABASE_URL"]

url = parse.urlparse(DATABASE_URL)

OAUTH = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
ACCOUNT_HANDLER = Twitter(auth=OAUTH)
UPLOAD_HANDLER = Twitter(auth=OAUTH, domain="upload.twitter.com")
STREAM_HANDLER = TwitterStream(auth=OAUTH)
ADMIN_HANDLER = TwitterStream(auth=OAUTH)


def main():
    """Main function to handle different activites of the account."""

    streamer = managers.StreamThread("Streamer",
        STREAM_HANDLER, ACCOUNT_HANDLER, url,
        functions.reply_with_shortened_url)  # For the troubling part.
    # For retweets, likes, follows.
    account_manager = managers.AccountThread(
        ACCOUNT_HANDLER, UPLOAD_HANDLER, url, args.rate, fav, retweet, follow, scrape)
    admin = managers.StreamThread(
        "Admin", ADMIN_HANDLER, ACCESS_SECRET, url, functions.admin_action)
    streamer.start()
    account_manager.start()
    admin.start()
    for thread in [streamer, account_manager, admin]:
        thread.join()


# Execute the main() function only if script is executed directly.
if __name__ == "__main__":
    print("Starting the bot...")
    main()
