#!/usr/bin/env python3
"""
A simple subreddit scraper
"""

import datetime as dt
import logging
import time
import os
import sys
import getopt

import praw
from psaw import PushshiftAPI

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


def generate_submissions_psaw(month_num, subreddit):
    """
    Gets submissions between start/end epochs for requested
    subreddit

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

    return api.search_submissions(after=start_epoch, before=end_epoch,
                                  subreddit=subreddit, size=1000)


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


def init_db(db_name):
    """
    Creates a SQLite DB connection to put scraped content into

    Returns
    -------
    conn: SQLite DB instance
    """

    conn = db.create_connection(db_name)
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

    return getopt.getopt(sys.argv[2:], 'vhc')

def iterate_comments(state, submission, conn):
    """
    TODO: Docstring
    """

    comments = generate_comments(state.reddit, submission.id)
    praw_timer(state.reddit)
    for j in list(comments):
        try:
            comment = (str(j.author), str(utc_to_local(j.created_utc)),
                    str(j.id), str(j.body), str(submission.id))
            db.insert_comment(conn, comment)
        except AttributeError as err:
            print(err)
            continue
        state.update_praw()
        state.inc_comment()
        #print("PRAW requests remaining: ", end="")
        #print(reddit.auth.limits['remaining'], end="\r")


def update_display(state_obj):
    """
    TODO: Docstring
    """

    filesize = 0
    if os.path.isfile(r"./corpus.db"):
        filesize = (int(os.stat(r"./corpus.db").st_size)) / 1048576

    output = ' PRAW Requests Remaining: {} '\
             '|Submission Request #{} '\
             '|Comment Request #{} ' \
             '|Filesize {} MB'


    print(output.format(state_obj.praw_requests,
          state_obj.submission_idx, state_obj.comment_idx,
          filesize), end="     \r", flush=True)

def usage():
    """
    TODO: Docstring
    """

    if os.name == 'nt':
        output = """Usage: python3 scrape.py [subreddit] [output file]
        Options: -v: verbose logging
                 -c: comments on"""
    else:
        output = """Usage: ./scrape.py [subreddit] [output file]
        Options: -v: verbose logging
                 -c: comments on"""

    print(output)
    exit()

class StateObj:
    """
    TODO: Docstring
    """

    reddit = []
    submission_idx = 0
    comment_idx = 0
    praw_requests = 0
    corpus_size = 0

    def __init__(self):
        self.submission_idx = 0
        self.comment_idx = 0
        self.praw_requests = 0
        self.reddit = praw.Reddit("bot1")

    def inc_sub(self):
        # increment idx
        self.submission_idx += 1

    def reset_comment(self):
        self.comment_idx = 0

    def inc_comment(self):
        self.comment_idx += 1

    def update_praw(self):
        self.praw_requests = self.reddit.auth.limits['remaining']

def main():
    """
    TODO: Docstring
    """

    if len(sys.argv) != 3:
        usage()
    opts, args = get_args()
    subreddit = sys.argv[1]
    comment_flag = False
    for opt, arg in opts:
        if opt in ['-v']:
            print("Verbose logging")
            init_log()
        if opt in ['-c']:
            comment_flag = True
            print("Comments on ")
    conn = init_db(sys.argv[2])
    state = StateObj()

    for month in range(1, 2):
        gen = generate_submissions_psaw(month, subreddit)

        for i in list(gen):
            state.inc_sub()
            update_display(state)
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
                if comment_flag:
                    iterate_comments(state, i, conn)


            #print(" | At submission index ", inx, end="")
            #print(" of current request - ", end="")
            #print(utc_to_local(i.created_utc), end="\r")


if __name__ == "__main__":
    main()
