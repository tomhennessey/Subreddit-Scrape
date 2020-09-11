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
    return(api.search_submissions(after=start_epoch, before=end_epoch, subreddit='teachers', limit=4000000))

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
    return conn


def main():
    #init_log()
    gen = generate_submissions()
    conn = init_db()

    for i in list(gen):
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
            db.insert(conn, submission)
            print(utc_to_local(i.created_utc))


if __name__ == "__main__":
    main()
