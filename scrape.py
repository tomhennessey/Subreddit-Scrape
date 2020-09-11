#!/usr/bin/env python3

import praw
from psaw import PushshiftAPI
import datetime as dt
import logging
import time
import os

import db

# initialize verbose logging
def init_log():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger = logging.getLogger('psaw')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

# convert unix timestamp to something readable for output
def utc_to_local(utc_dt):
    return dt.datetime.fromtimestamp(utc_dt).strftime('%Y-%m-%d %I:%M:%S%p')

# generate start and end epochs as the first and last
# 15 days of each month
def epoch_generate(month_num, month_half):
    if month_half == 1:
        start_epoch = int(dt.datetime(2020, month_num, 1).timestamp())
        end_epoch = int(dt.datetime(2020, month_num, 15).timestamp())
    else:
        start_epoch = int(dt.datetime(2020, month_num, 15).timestamp())
        end_epoch = int(dt.datetime(2020, month_num + 1, 1).timestamp())
   
    return (start_epoch, end_epoch)

# gets submissions between start/end epochs from 'teachers' subreddit
# limit seems to top out at 3999 but you need to put a much larger number 
# to get there
def generate_submissions_psaw(month_num, month_half):
    # init api
    api = PushshiftAPI()
    
    epoch_tuple = epoch_generate(month_num, month_half)
    start_epoch = epoch_tuple[0]
    end_epoch = epoch_tuple[1]
    
    # Pushapi says they have 32888 submissions in this time period, 
    # hence the limit
    return(api.search_submissions(after=start_epoch, before=end_epoch, subreddit='teachers', limit=40000))

# takes a generated psaw object to start praw api
# matches submission id's from psaw to find associated comments 
# with praw
def generate_comments(reddit, submission_id):

    # get submission from praw via submission_id from psaw
    submission = reddit.submission(id=submission_id)

    # should load all folded comments, but i'm afraid to use it too
    # much with a large dataset as it uses a network request each
    # call and might get us banned from reddit
    return submission.comments

# timer to keep track of praw api requests
def praw_timer(reddit):
    if reddit.auth.limits['remaining'] < 15:
        print("Waiting for PRAW API limit to reset...")
        time.sleep(4)

# create submissions and ocmments tables in SQLite DB
def init_db():
    conn = db.create_connection(r"./corpus.db")
    db.create_table_submissions(conn)
    db.create_table_comments(conn)
    print("DB Init Success")
    return conn

# clear terminal screen in windows or unix
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    #init_log()
    reddit = praw.Reddit("bot1")
    conn = init_db()

    for month in range(1, 10):
        for half in range (1, 3):
            gen = generate_submissions_psaw(month, half)

            for inx, i in enumerate(list(gen)):
                # only get submission that are self posts
                if hasattr(i, 'selftext'):
                    if hasattr(i, 'author'):
                        submission = (i.author, utc_to_local(i.created_utc), i.title,
                                i.selftext, i.id, i.is_self, utc_to_local(i.retrieved_on),
                                i.num_comments, i.permalink)
                    else:
                        submission = ('deleted', utc_to_local(i.created_utc), i.title,
                                i.selftext, i.id, i.is_self, utc_to_local(i.retrieved_on),
                                i.num_comments, i.permalink)
                    db.insert_submission(conn, submission)
                    
                    if i.num_comments > 0:
                        comments = generate_comments(reddit, i.id)
                        praw_timer(reddit)
                        for ind, j in enumerate(list(comments)):
                            try:
                                comment = (str(j.author), str(utc_to_local(j.created_utc)), 
                                        str(j.id), str(j.body), str(i.id))  
                                db.insert_comment(conn, comment)
                            except AttributeError as e:
                                print(e)
                                continue
                        clear_screen()
                        print("PRAW requests remaining: ", end="") 
                        print(reddit.auth.limits['remaining'])
                        print("At submission index ", end="")
                        print(inx)                        
                        print(" of current month - ")
                        print(utc_to_local(i.created_utc))



if __name__ == "__main__":
    main()
