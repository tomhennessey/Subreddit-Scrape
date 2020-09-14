#!/usr/bin/env python3

import praw
from praw.models import MoreComments
from psaw import PushshiftAPI
import datetime as dt
import logging
import time
import os
import sys
import getopt

import db

def init_log():
    """
    Initiates a logger for psaw to be used with '-v' cli option. 
    """

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger = logging.getLogger('psaw')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)


def utc_to_local(utc_dt):
    """
    Converts unix utc time format to human readable form for output

    Returns
    -------
    string
        A date and time in string format
    """

    return dt.datetime.fromtimestamp(utc_dt).strftime('%Y-%m-%d %I:%M:%S%p')


def epoch_generate(month_num, year):
    """
    Generates start and end epochs to be used in 
    generate_submissions_psaw()

    Parameters
    ----------
    month_num : int
        The month number (1-12) that is being requested in scrape

    month_half: int
        Half of the month (1-2) that corresponds to first or last
        15 days


    Returns
    -------
    tuple
        A tuple containing a start and end date in linux utc format
    """

    start_time = int(dt.datetime(year, month_num, 1).timestamp())
    end_time = int(dt.datetime(year, month_num + 1, 1).timestamp())

    return (start_time, end_time)

"""
    if month_half == 1:
        start_epoch = int(dt.datetime(2020, month_num, 1).timestamp())
        end_epoch = int(dt.datetime(2020, month_num, 15).timestamp())
    else:
        start_epoch = int(dt.datetime(2020, month_num, 15).timestamp())
        end_epoch = int(dt.datetime(2020, month_num + 1, 1).timestamp())
   
    return (start_epoch, end_epoch)
    """


def generate_submissions_psaw(month_num, subreddit):
    """
    Gets submissions between start/end epochs for requested 
    subreddit

    TODO: Figure out limit paging

    Parameters
    ----------
    month_num: int
        The month number to be passed to epoch_generate()
    month_half: int
        The month half to be passed to epoch_generate()
    subreddit: string
        The name of the subreddit to be scraped

    Returns
    -------
    generator
        A generator object that will be used to loop through 
        submissions
    """
    
    # init api
    api = PushshiftAPI()
    
    epoch_tuple = epoch_generate(month_num, 2020)
    start_epoch = epoch_tuple[0]
    end_epoch = epoch_tuple[1]
    

    return(api.search_submissions(after=start_epoch, before=end_epoch, subreddit=subreddit, size=1000))


def generate_comments(reddit, submission_id):
    """
    Take a PRAW reddit object and finds comments for a given 
    submissions_id

    Parameters
    ----------
    reddit: praw.Reddit
        A PRAW Reddit API instance
    submission_id: int
        The id of the subreddit submission whose comments we want

    Returns
    -------
    submission.comments: praw.models.comment_forest.CommentForest 
        A Reddit CommentForest that can be iterated through
    """

    # get submission from praw via submission_id from psaw
    submission = reddit.submission(id=submission_id)

    # should load all folded comments
    return submission.comments


def praw_timer(reddit):
    """
    A timer that counts down remaining PRAW Api requests and
    shortly halts and retries when there are less than 10. 

    Parameters
    ----------
    reddit: praw.Reddit
        A PRAW Reddit API instance
    """

    if reddit.auth.limits['remaining'] < 10:
        print("Waiting for PRAW API limit to reset...", end="\r")
        time.sleep(4)


def init_db():
    """
    Creates a SQLite DB connection to put scraped content into

    Returns
    -------
    conn: SQLite DB instance
    """

    conn = db.create_connection(r"./corpus.db")
    db.create_table_submissions(conn)
    db.create_table_comments(conn)
    print("DB Init Success")
    return conn

def clear_screen():
    """
    Clears the terminal screen depending on OS detected
    """

    os.system('cls' if os.name == 'nt' else 'clear')


def get_args():
    """
    Retrieve CLI arguments
    """

    return getopt.getopt(sys.argv[2:], 'vh') 

def iterate_comments(reddit, submission, conn):
    comments = generate_comments(reddit, submission.id)
    praw_timer(reddit)
    for ind, j in enumerate(list(comments)):
        try:
            comment = (str(j.author), str(utc_to_local(j.created_utc)), 
                    str(j.id), str(j.body), str(submission.id))  
            db.insert_comment(conn, comment)
        except AttributeError as e:
            print(e)
            continue
        print("PRAW requests remaining: ", end="") 
        print(reddit.auth.limits['remaining'], end="\r")


def main():
    opts, args = get_args()
    subreddit = sys.argv[1]
    for opt, arg in opts:
        if opt in ['-v']:
            print("Verbose logging")
            init_log()
    reddit = praw.Reddit("bot1")
    conn = init_db()

    for month in range(1, 3):
        gen = generate_submissions_psaw(month, subreddit)

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
                    iterate_comments(reddit, i, conn)

            print(" | At submission index ", inx, end="")
            print(" of current request - ", end="")
            print(utc_to_local(i.created_utc), end="\r")


if __name__ == "__main__":
    main()
