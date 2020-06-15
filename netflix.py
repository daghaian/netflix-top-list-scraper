
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import logging
import time
import datetime
import os
import sys
import json
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# TRAKT API CONSTS
TRAKT_API_KEY=os.getenv("TRAKT_API_KEY","YOUR_API_KEY_HERE")
TRAKT_ACCESS_TOKEN = os.getenv("TRAKT_ACCESS_TOKEN","YOUR_ACCESS_TOKEN_HERE")

# TRAKT LIST URLS
TRAKT_LISTS = {
    "movies":os.getenv("TRAKT_MOVIE_LIST","YOUR_TRAKT_MOVIE_LIST_HERE"),
    "shows":os.getenv("TRAKT_TV_LIST","YOUR_TRAKT_TV_LIST_HERE")
}


# NETFLIX ACCOUNT CREDENTIALS
NETFLIX_USERNAME = os.getenv("NETFLIX_USERNAME","YOUR_NETFLIX_USERNAME")
NETFLIX_PASSWORD = os.getenv("NETFLIX_PASSWORD","YOUR_NETFLIX_PASSWORD")


def extract_top_list(driver,list):
    # Visit genre page
    driver.get('https://www.netflix.com/browse/genre/34399' if list == 'movies' else 'https://www.netflix.com/browse/genre/83')
    logger.info("Extracting top list for {}".format(list))
    top_list = []
    while(1):
        driver.execute_script("window.scrollBy(0,250)")
        time.sleep(.5)
        try:
            expand = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"//div[@data-list-context='mostWatched']//b[@class='indicator-icon icon-rightCaret']")))
            while len(top_list) != 10:
                driver.execute_script('document.evaluate("//div[@data-list-context=\'mostWatched\']//b[@class=\'indicator-icon icon-rightCaret\']",document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()')
                WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"//div[@class='slider-refocus title-card title-card-top-10']")))
                soup = BeautifulSoup(driver.page_source,"html.parser")
                titles = soup.find_all("div",{"class":"title-card-top-10"})

                for t in titles:
                    title = t.find("div").find("a").get('aria-label')
                    if title not in top_list:
                        logger.info("Appending title: {}".format(title))
                        top_list.append(title)
            break
        except Exception as e:
            logger.info("Top list is not currently in DOM. Scrolling down...")
            continue 
    logger.info("Returning list: {}".format(top_list))
    return top_list
    

def login(driver):
    LOGIN_URL = "https://www.netflix.com/login"

    logger.info("Proceeding to login to {}".format(LOGIN_URL))
    # Visit login page of netflix
    driver.get(LOGIN_URL)
    
    # Enter user credentials
    user_el = driver.find_element_by_id("id_userLoginId")
    user_el.send_keys(NETFLIX_USERNAME)
    pass_el = driver.find_element_by_id("id_password")
    pass_el.send_keys(NETFLIX_PASSWORD)

    # Wait a few seconds before logging in to avoid botlike behavior
    time.sleep(1)

    # Click sign-in
    signin_el = driver.find_element_by_xpath("//button[@class='btn login-button btn-submit btn-small']")
    signin_el.click()
    logger.info("Signin complete, proceeding to select profile")
    # Select first profile available
    profile = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,"//div[@class='profile-icon']")))
    profile.click()
    logger.info("Profile selected")


def clear_trakt_lists():

    for item,url in TRAKT_LISTS.items():
        # Clear list
        logger.info("Clearing {} List of existing entries from the previous day".format(item))
        
        r = requests.get('{}/items'.format(url), headers={'trakt-api-key': TRAKT_API_KEY})
        if r.status_code == 200:
            data = json.loads(r.text)
            logger.info("Current items found on List: {}".format(data))

            if item == "movies":
                data = [{"ids":{"trakt":x['movie']['ids']['trakt']}} for x in data]
                data = {"movies":data}
            else:
                data = [{"ids":{"trakt":x['show']['ids']['trakt']}} for x in data]
                data = {"shows":data}
            r = requests.post('{}/items/remove'.format(url), headers={'trakt-api-key': TRAKT_API_KEY, 'Authorization': 'Bearer {}'.format(TRAKT_ACCESS_TOKEN)}, json=data)
            if r.status_code == 200:
                logger.info("Cleared {} List successfully".format(item))

def update_trakt_list_descriptions():
    current_day = datetime.datetime.now().strftime("%m/%d/%Y")

    data = {
        "description":"Updated As Of {}".format(current_day)
    }
    # Update description for movies
    logger.info("Updating description for movies list to {}".format(data))
    r = requests.put(TRAKT_LISTS["movies"], headers={"trakt-api-key": TRAKT_API_KEY, "Authorization": "Bearer {}".format(TRAKT_ACCESS_TOKEN)},json=data)
    if r.status_code == 200:
        logger.info("Updated description for movies list to {}".format(data))

    # Update description for shows
    logger.info("Updating description for shows list to {}".format(data))
    r = requests.put(TRAKT_LISTS["shows"], headers={"trakt-api-key": TRAKT_API_KEY, "Authorization": "Bearer {}".format(TRAKT_ACCESS_TOKEN)},json=data)
    if r.status_code == 200:
        logger.info("Updated description for shows list to {}".format(data))
          
def add_to_trakt(media_list, category):
    category = "movie" if category == "movies" else "show"

    for item in media_list:
        logger.info("Search for item {} to add to Trakt List".format(item))
        r = requests.get('https://api.trakt.tv/search/{}?query={}'.format(category, item),headers={'trakt-api-key':TRAKT_API_KEY})
        if r.status_code == 200:
            logger.info("Request completed successfully: {}".format(r.text))
            if category == 'movie':
                url = TRAKT_LISTS["movies"]
                data = {"movies":[json.loads(r.text)[0]['movie']]}
            else:
                url = TRAKT_LISTS["shows"]
                data = {"shows":[json.loads(r.text)[0]['show']]}
                
            r = requests.post(url, headers={'trakt-api-key': TRAKT_API_KEY, 'Authorization': 'Bearer {}'.format(TRAKT_ACCESS_TOKEN)}, json=data)
        else:
            logger.info(r.status_code)
            logger.info(r.text)


chrome_options = Options()  
chrome_options.add_argument("--headless") 
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(chrome_options=chrome_options)

login(driver)

top_movies = extract_top_list(driver,"movies")
top_shows = extract_top_list(driver,"shows")

# Clear before adding new items
clear_trakt_lists()

# Update descriptions
update_trakt_list_descriptions()

# Add new items to trakt list for movies
add_to_trakt(top_movies, "movies")

# Add new items to trakt list for shows
add_to_trakt(top_shows,"shows")


driver.quit()
