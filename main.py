from typing import List
import time
from util import *
from scraper import *
from twitter import *

# TODO: Implement limit for number of DM's per hour
# TODO: Implement logging (status/action performed, warning/error, limit reached, etc.)

PAUSE_TIME = 15 # in minutes


def poll_all_topics() -> List[str]:
    # Retrieve tweets from each topic and filter out duplicates
    records = []
    for topic in get_topics():
        print(f"Retrieving tweets from topic: {topic}")
        for tweet in get_tweets(topic):
            if not tweet in records:
                records.append(tweet)
    
    # Convert records into list of User ID's
    print("Finding User IDs from Tweets.")
    users = []
    for record in records:
        users.append(get_userid(record[0]))

    return users


def filter_through_database(user_ids: List[str], file: str=DATABASE_FILE) -> List[str]:
    # Retrieve history from database
    print("Filtering User IDs through previously messaged user database.")
    try:
        conn = sqlite3.connect(file)
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM history;")
        history = cur.fetchall()
        conn.close()
    except:
        history = []

    # Compare users to history and filter
    filtered_users = []
    for user in user_ids:
        if not user in history:
            filtered_users.append(user)
    
    return filtered_users


# TODO: this did not work first try. Figure this out
def append_to_database(user_ids: List[str], file: str=DATABASE_FILE) -> bool:
    try:
        conn = sqlite3.connect(file)
        cur = conn.cursor()
        cur.executemany("INSERT INTO history VALUES ?", user_ids)
        conn.close()
        return True
    except:
        return False


def send_all_dms(user_ids: List[str]):
    for id in user_ids:
        try:
            msg = get_random_message()
            print(f"Sending direct message to: {id} - \"{msg}\"")
            send_directmessage(id, msg)
        except:
            continue


def main():
    users = poll_all_topics()
    filtered = filter_through_database(users)
    append_to_database(filtered)
    send_all_dms(filtered)

if __name__ == '__main__':
    while True:
        main()
        print(f"Pausing for {PAUSE_TIME} minutes...\n")
        time.sleep(PAUSE_TIME * 60)
