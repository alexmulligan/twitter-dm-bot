from typing import List, Tuple
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import re

WEBDRIVER_LOCATION = "files/chromedriver"
PAGE_LOAD_TIME = 4
SCROLL_PAUSE_TIME = 0.75


def get_tweets(topic_url: str) -> List[Tuple[str, str]]:
    '''Load a Twitter page of a topic and retrieve top tweets from that topic'''
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome("/usr/local/bin/chromedriver", options=options)

    # Request page and wait for content to load - Twitter requires this as it loads the page before it loads the content
    driver.get(topic_url)
    time.sleep(PAGE_LOAD_TIME)

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            time.sleep(SCROLL_PAUSE_TIME)
            break
        last_height = new_height

    page_source = driver.page_source
    driver.close()
    soup = BeautifulSoup(page_source, 'lxml')
    # Find all 'a' elements whose href are a URL that contains "/status/"
    elements = soup.find_all('a', {'href': re.compile(r'.*/status/.*')}) # TODO: refine this regex to exclude anything with "photo" in it

    # Retrieve username and tweet ID from URL, and filter out duplicates
    # TODO: refactor this so it's clear and concise
    tweet_records = []
    for element in elements:
        href = element['href']

        if not 'photo' in href:
            tweet = tuple(href.strip('/').split('/status/'))
            if not tweet in tweet_records:
                tweet_records.append(tweet)

    return tweet_records
