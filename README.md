# Subreddit Scrape
A simple subreddit scraper. Able to scrape submissions and comments of a particular subject over a specified date. 

## Dependencies
-praw
-psaw
-python 3
Simply run 
	pip install -r requirements.txt 
to download python dependencies. 

## praw.ini
You must have a praw.ini file in the base folder with client name "bot1" and strings client_id, client_secret, user_agent, reddit username, and reddit password

## Usage
Nix: 
	./scrape.py [subreddit] [output_file] [-cv]
Options:
-c = comments on
-v = verbose mode on
