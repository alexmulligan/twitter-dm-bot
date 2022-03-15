from typing import Dict, List
from random import randint
import toml
import sqlite3

KEYS_FILE = 'files/keys.toml'
TOPICS_FILE = 'files/topics.txt'
MESSAGES_FILE = 'files/messages.txt'
DATABASE_FILE = 'files/history.db'


def get_creds(file: str=KEYS_FILE) -> Dict[str, str]:
    '''retrieve Twitter API credentials from file'''
    return toml.load(file)
    

def get_topics(file: str=TOPICS_FILE) -> List[str]:
    '''retrieve Twitter topics from file'''
    topics = []
    with open(file, 'r') as f:
        for line in f:
            if line.strip() != '':
                topics.append(line.strip())
    return topics


def get_random_message(file: str=MESSAGES_FILE) -> str:
    messages = []
    with open(file, 'r') as f:
        for line in f:
            messages.append(line.strip())
    
    return messages[randint(0, len(messages)-1)]


def initialize_database(file: str=DATABASE_FILE) -> bool:
    try:
        conn = sqlite3.connect(file)
        cur = conn.cursor()
        cur.execute('CREATE TABLE history (user_id text)')
        conn.commit()
        conn.close()
        return True

    except:
        return False

if __name__ == '__main__':
    choice = input("Do you want to initialize the database? (y/n): ").strip().lower()
    if choice == 'y':
        initialize_database()
