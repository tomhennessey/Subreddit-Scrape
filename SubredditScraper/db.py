#!/usr/bin/env python3

# cribbed from sqlitetutorial.net/sqlite-python

import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Connected to SQLite DB")
        return conn
    except Error as e:
        print(e)


def create_table_submissions(conn):
    create_table_sql = """ CREATE TABLE IF NOT EXISTS submissions (
                                        prim_key integer PRIMARY KEY,
                                        author text NOT NULL,
                                        created_utc text NOT NULL,
                                        title text NOT NULL,
                                        selftext text,
                                        id text NOT NULL,
                                        is_self integer NOT NULL,
                                        retrieved_on text NOT NULL,
                                        num_comments integer NOT NULL,
                                        permalink text NOT NULL
                                        ); """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_table_comments(conn):
    create_table_sql = """ CREATE TABLE IF NOT EXISTS comments (
                                        prim_key integer PRIMARY KEY,
                                        author text NOT NULL,
                                        created_utc text NOT NULL,
                                        id text NOT NULL,
                                        body text NOT NULL,
                                        parent text NOT NULL
                                        ); """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_submission(conn, submission):
    sql = ''' INSERT INTO submissions(author, created_utc, title, selftext, id, is_self, retrieved_on,
                                num_comments, permalink)
                                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                                '''
    cur = conn.cursor()
    cur.execute(sql, submission)
    conn.commit()
    return cur.lastrowid

def insert_comment(conn, comment):
    sql = ''' INSERT INTO comments(author, created_utc, id, body, parent)
                            VALUES(?, ?, ?, ?, ?)
                            '''
    cur = conn.cursor()
    cur.execute(sql, comment)
    conn.commit()
    return cur.lastrowid



