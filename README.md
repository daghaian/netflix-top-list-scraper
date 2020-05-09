# Netflix Top List Scraper
Scrapes the Top 10 Lists for Movies/TV for US netflix

## Requirements
1. You must have Python 3.~ installed

## Installation
1. Run `pip install -r requirements.txt `from within the repo
2. Make sure you either expose the required environment variables before running script or edit the script yourself and replace the appropriate values for the expected variables
4. Download the appropriate version of chrome driver and place it inside the repo ([https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads))
4. Run `python netflix.py` 

## Configuration
The following environment variables must either be set in the shell you're running the script from or can be edited permanently inside of the `netflix.py` file itself

|Variable  |Description  | Example
|--|--|--|
|TRAKT_API_KEY  |Your Trakt API key  | N/A	|
|TRAKT_ACCESS_TOKEN | Your Trakt access token (Further information can be found [here]([https://trakt.docs.apiary.io/#](https://trakt.docs.apiary.io/#))| N/A
|TRAKT_MOVIE_LIST | URL of trakt movie list (Root URL is api.trakt.tv) | https://api.trakt.tv/users/painbringer112/lists/netflix-top-10-movies
|TRAKT_TV_LIST | URL of trakt TV list (Root URL is api.trakt.tv) | https://api.trakt.tv/users/painbringer112/lists/netflix-top-10-shows |
|NETFLIX_USERNAME | Username of your Netflix account | N/A
|NETFLIX_PASSWORD | Password of your Netflix account | N/A


