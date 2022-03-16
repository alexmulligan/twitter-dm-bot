from TwitterAPI import TwitterAPI
import json
from util import get_creds, log
import sys


def get_userid(username: str) -> str:
    '''Gets User ID from Twitter Username; returns None if unsuccessful'''
    creds = get_creds()
    try:
        api = TwitterAPI(creds["consumer_key"], creds["consumer_secret"], auth_type='oAuth2')
        res = api.request('users/lookup', {'screen_name': username})
        return res.json()[0]['id'] if res.status_code == 200 else None
    except:
        log("E2: Getting UserID Failed", "ERROR")
        sys.exit(2) # Exit code 2 - twitter api/connection error


def follow_user(user_id: str) -> bool:
    '''Follows user if not already following; returns bool for success'''
    creds = get_creds()

    try:
        api = TwitterAPI(creds["consumer_key"], creds["consumer_secret"], creds["access_token"], creds["access_secret"])

        res = api.request('friendships/create', {'user_id': user_id})
        return True if res.status_code == 200 else False
    except:
        log("E2: Following User Failed", "ERROR")
        sys.exit(2) # Exit code 2 - twitter api/connection error


def check_if_follower(user_id: str) -> bool:
    '''Checks if user is following you; Returns True if following'''
    creds = get_creds()
    try:
        api = TwitterAPI(creds["consumer_key"], creds["consumer_secret"], creds["access_token"], creds["access_secret"])

        followers = set(id for id in api.request('followers/ids'))
        return True if user_id in followers else False
    except:
        log("E2: Checking If Follower Failed", "ERROR")
        sys.exit(2) # Exit code 2 - twitter api/connection error


def send_directmessage(user_id: str, message_text: str) -> bool:
    '''Sends direct message to Twitter user; returns bool for success'''
    creds = get_creds()
    try:
        api = TwitterAPI(creds["consumer_key"], creds["consumer_secret"], creds["access_token"], creds["access_secret"])

        event = {
            "event": {
                "type": "message_create",
                "message_create": {
                    "target": {
                        "recipient_id": user_id
                    },
                    "message_data": {
                        "text": message_text
                    }
                }
            }
        }
        res = api.request('direct_messages/events/new', json.dumps(event))
        return True if res.status_code == 200 else False
    except:
        log("E2: Sending Direct Message Failed", "ERROR")
        sys.exit(2) # Exit code 2 - twitter api/connection error
