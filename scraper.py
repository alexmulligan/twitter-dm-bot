from typing import List, Tuple
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import re
from util import log
import sys

WEBDRIVER_LOCATION = "files/chromedriver"
PAGE_LOAD_TIME = 4 # seconds
SCROLL_PAUSE_TIME = 0.75 # seconds


def get_tweets(topic_url: str) -> List[Tuple[str, str]]:
    '''Load a Twitter page of a topic and retrieve top tweets from that topic'''
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')
        driver = webdriver.Chrome(WEBDRIVER_LOCATION, options=options)

        # Request page and wait for content to load - Twitter requires this as it loads the page before it loads the content
        driver.get(topic_url)
        time.sleep(PAGE_LOAD_TIME)

        # Continuously scroll down until the page ends -- this is necessary to load all tweets from the topic
        last_height = driver.execute_script("return document.body.scrollHeight") # Get scroll height
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Scroll down to bottom
            time.sleep(SCROLL_PAUSE_TIME) # Wait to load page

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                time.sleep(SCROLL_PAUSE_TIME)
                break
            last_height = new_height

        page_source = driver.page_source
        driver.close()
        soup = BeautifulSoup(page_source, 'lxml')
        # Find all 'a' elements whose href are a URL that contains "/status/" -- this will get all tweets on the page
        elements = soup.find_all('a', {'href': re.compile(r'.*/status/.*')})

        # Retrieve username and tweet ID from URL, and filter out duplicates
        tweet_records = []
        for element in elements:
            href = element['href']

            if not 'photo' in href:
                tweet = tuple(href.strip('/').split('/status/'))
                if not tweet in tweet_records:
                    tweet_records.append(tweet)

        return tweet_records
    except:
        log("E1: Failed getting tweets", "ERROR")
        sys.exit(1) # Exit Code 1 - scraping error
