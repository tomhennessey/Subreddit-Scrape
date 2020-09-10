#!/usr/bin/env python3

import praw
from psaw import PushshiftAPI
import datetime as dt
import logging

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

# gets submissions between start/end epochs from 'teachers' subreddit
# with whatever limit is set to
def generate_submissions():
    # init api
    api = PushshiftAPI()
    
    # start and end dates of search
    start_epoch = int(dt.datetime(2020, 1, 1).timestamp())
    end_epoch = int(dt.datetime(2020, 9, 1).timestamp())
    
    # Pushapi says they have 32888 submissions in this time period, 
    # hence the limit
    return(api.search_submissions(after=start_epoch, before=end_epoch, subreddit='teachers', limit=32888))

# takes a generated psaw object to start praw api
# matches submission id's from psaw to find associated comments 
# with praw
def generate_comments(submission_id):
    # init praw api with praw.ini settings
    reddit = praw.Reddit("bot1")

    
    # get submission from praw via submission_id from psaw
    submission = reddit.submission(id=submission_id)

    # should load all folded comments, but i'm afraid to use it too
    # much with a large dataset as it uses a network request each
    # call and might get us banned from reddit
    #submission.comments.replace_more(limit=None)

    # print the top level comment bodies
    for index, top_level_comment in enumerate(submission.comments):
        print("_com" + str(index) + ": " + top_level_comment.body)
    return

def init_db():
    conn = db.create_connection(r"./corpus.db")
    db.create_table(conn)


def main():
    init_log()
    gen = generate_submissions()
    init_db()
    
    # we want..
    # i.author
    # i.created_utc
    # i.title
    # i.selftext (if exists)
    # i.id
    # i.is_self
    # i.retrieved_on
    # i.num_comments
    # i.permalink
    
    for i in list(gen):
        try: 
            submission = (i.author, i.created_utc, i.title, i.selftext, i.id, 
                    i.is_self, i.retrieved_on, i.num_comments, i.permalink)
            db.insert(conn, submission)
        except:
            continue

        print("_AUTHOR: " + i.author)
        print("_ID: " + i.id)
        print("_TIME: " + utc_to_local(i.created_utc))
        print("_TITLE: " + i.title)
        try: print("_TEXT: " + i.selftext + "\n")
        except:
            continue
        #print("_TOP_LEVEL_COMMENTS: ") 
        #print(generate_comments(i.id))
        print("###\n")
        


if __name__ == "__main__":
    main()
