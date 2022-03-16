from typing import List
import time
from datetime import datetime
from util import *
from scraper import *
from twitter import *

# TODO: Implement limit for number of DM's per hour

PAUSE_TIME = 5 # in minutes (must be at least 5, and no more than 60)
DM_PER_HOUR_LIMIT = 100

dm_counter = 0


def poll_all_topics() -> List[str]:
    # Retrieve tweets from each topic and filter out duplicates
    records = []
    for topic in get_topics():
        log(f"Retrieving tweets from topic: {topic}")
        for tweet in get_tweets(topic):
            if not tweet in records:
                records.append(tweet)
    
    # Convert records into list of User ID's
    log("Finding User IDs from retrieved tweets")
    users = []
    for record in records:
        users.append(get_userid(record[0]))

    return users


def filter_through_database(user_ids: List[str], file: str=DATABASE_FILE) -> List[str]:
    # Retrieve history from database
    log("Filtering User IDs through previously messaged user database.")
    try:
        conn = sqlite3.connect(file)
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM history;")
        history = cur.fetchall()
        conn.close()
    except:
        log("E3: Failed filtering User IDs through database.", "ERROR")
        sys.exit(3) # Exit code 3 - database error

    # TODO: double check this
    # Compare users to history and filter
    filtered_users = []
    for user in user_ids:
        if not user in history:
            filtered_users.append(user)
    
    return filtered_users


def append_to_database(user_ids: List[str], file: str=DATABASE_FILE):
    try:
        log("Adding new User IDs to database.")
        conn = sqlite3.connect(file)
        cur = conn.cursor()
        for id in user_ids:
            cur.execute(f"INSERT INTO history VALUES ('{id}');")
        conn.commit()
        conn.close()
    except:
        log("E3: Failed appending new User IDs to database", "ERROR")
        sys.exit(3) # Exit code 3 - database error


def send_all_dms(user_ids: List[str]):
    for id in user_ids:
        msg = get_random_message()
        log(f"Sending direct message to: {id} - \"{msg}\"")
        send_directmessage(id, msg)


def main():
    users = poll_all_topics()
    filtered = filter_through_database(users)
    append_to_database(filtered)
    send_all_dms(filtered)

if __name__ == '__main__':
    while True:
        main()
        log(f"Pausing for {PAUSE_TIME} minutes...\n")
        time.sleep(PAUSE_TIME * 60)
