from typing import List
import time
from util import *
from scraper import *
from twitter import *

PAUSE_TIME = 10 # in minutes (must be at least 1, and no more than 60)
DM_PER_HOUR_LIMIT = 500
LIMIT_DELAY_TIME = 20 # in minutes


def poll_all_topics() -> List[str]:
    # Retrieve tweets from each topic and filter out duplicates
    records = []
    for topic in get_topics():
        log(f"Retrieving tweets from topic: {topic}")
        for tweet in get_tweets(topic):
            if not tweet in records:
                records.append(tweet)
    log(f"Found {len(records)} tweets in topic {topic}")
    
    # Convert records into list of User ID's
    log("Finding User IDs from retrieved tweets")
    users = []
    for record in records:
        users.append(get_userid(record[0]))

    log(f"Found {len(users)} total User IDs.")
    return users


def filter_through_database(user_ids: List[str], file: str=DATABASE_FILE) -> List[str]:
    # Retrieve history from database
    log("Filtering User IDs through previously messaged user database.")
    try:
        conn = sqlite3.connect(file)
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM history;")
        history = [entry[0] for entry in cur.fetchall()]
        conn.close()
    except:
        log("E3: Failed filtering User IDs through database.", "ERROR")
        sys.exit(3) # Exit code 3 - database error

    filtered_users = []
    for user in user_ids:
        if not user in history:
            filtered_users.append(user)
    
    log(f"Found {len(filtered_users)} new User IDs.")
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
    # initialize count to keep record of number of DMs sent within the last hour
    # (this count is implemented using a list with a constant length of the number of periods of pause time within an hour)
    dm_count = []
    for i in range(0, 60//PAUSE_TIME):
        dm_count.append(0)

    while True:
        users = poll_all_topics()
        filtered = filter_through_database(users)
        if len(filtered) > 0:
            append_to_database(filtered)
            send_all_dms(filtered)
        else:
            log("No new User IDs found. Not sending any DMs.")
        dm_count = add_count_entry(len(filtered), dm_count) # add the number of DMs sent this cycle to the count

        log(f"Pausing for {PAUSE_TIME} minutes...\n")
        time.sleep(PAUSE_TIME * 60)

        if sum(dm_count) > DM_PER_HOUR_LIMIT:
            log(f"DMs/Hour Limit reached. Delaying for {LIMIT_DELAY_TIME} minutes...\n", "WARN")

            # Clear the DM count list based on the time of the limit delay
            delayed_cycles = LIMIT_DELAY_TIME // PAUSE_TIME
            if LIMIT_DELAY_TIME > PAUSE_TIME and LIMIT_DELAY_TIME % PAUSE_TIME != 0:
                delayed_cycles += 1
            for i in range(0, delayed_cycles):
                dm_count = add_count_entry(0, dm_count)

            time.sleep(LIMIT_DELAY_TIME * 60)

if __name__ == '__main__':
    main()
