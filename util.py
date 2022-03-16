from typing import Dict, List
from random import randint
import toml
import sqlite3
from datetime import datetime
import sys

KEYS_FILE = 'files/keys.toml'
TOPICS_FILE = 'files/topics.txt'
MESSAGES_FILE = 'files/messages.txt'
DATABASE_FILE = 'files/history.db'
LOG_FILE = 'files/log.txt'
LOG_CONFIG = 1 # 0 - logfile only, 1 - logfile and console output


def log(message: str, level: str="INFO", file: str=LOG_FILE, config: int=LOG_CONFIG):
    '''Logs a message with level (INFO, WARN, ERROR) to a logfile and optionally the console'''
    log_text = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  [{level}]: {message}'
    with open(file, 'a') as f:
        f.write(log_text)
    
    if config:
        print(log_text)


def get_creds(file: str=KEYS_FILE) -> Dict[str, str]:
    '''retrieve Twitter API credentials from file'''
    try:
        creds = toml.load(file)
        return creds
    except:
        log("E4: Failed to get credentials from Keys file", "ERROR")
        sys.exit(4) # Exit code 4 - file io error
    

def get_topics(file: str=TOPICS_FILE) -> List[str]:
    '''retrieve Twitter topics from file'''
    try:
        topics = []
        with open(file, 'r') as f:
            for line in f:
                if line.strip() != '':
                    topics.append(line.strip())
        return topics
    except:
        log("E4: Failed to get topics from Topics file", "ERROR")
        sys.exit(4) # Exit code 4 - file io error


def get_random_message(file: str=MESSAGES_FILE) -> str:
    try:
        messages = []
        with open(file, 'r') as f:
            for line in f:
                messages.append(line.strip())
        
        return messages[randint(0, len(messages)-1)]
    except:
        log("E4: Failed to get message from Messages file", "ERROR")
        sys.exit(4) # Exit code 4 - file io error


def initialize_database(file: str=DATABASE_FILE):
    '''Initialize the application database with an empty table'''
    try:
        conn = sqlite3.connect(file)
        cur = conn.cursor()
        cur.execute('CREATE TABLE history (user_id text)')
        conn.commit()
        conn.close()
        log("Initialized Database")
    except:
        log("E3: Database Initialization Failed", "ERROR")
        sys.exit(3) # Exit code 3 - database error


def add_count_entry(entry: int, count: List[int]) -> List[int]:
    new_count = count[1:len(count)]
    new_count.append(entry)
    return new_count

if __name__ == '__main__':
    choice = input("Do you want to initialize the database? (y/n): ").strip().lower()
    if choice == 'y':
        initialize_database()
