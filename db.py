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


def create_table(conn):
    """ create a table from the create_table_sql statement
    """
    create_table_sql = """ CREATE TABLE IF NOT EXISTS submissions (
                                        prim_key integer PRIMARY KEY,
                                        author text NOT NULL,
                                        created_utc integer NOT NULL,
                                        title text NOT NULL,
                                        selftext text,
                                        id text NOT NULL,
                                        is_self integer NOT NULL,
                                        retrieved_on integer NOT NULL,
                                        num_comments integer NOT NULL
                                    ); """

    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert(conn, submission):
    sql = ''' INSERT INTO submissions(author, created_utc_integer, 
                                title, selftext, id, is_self, 
                                retrieved_on, num_comments)
                                VALUES(?,?,?,?,?,?,?,?)
                                '''
    cur = conn.cursor()
    cur.execute(sql, submission)
    conn.commit()
    return cur.lastrowid

"""
TABLE1 submissions: 
    author
    created_utc
    title
    selftext
    id
    is_self
    retrieved_on
    num_comments

TABLE2 comments:

"""

def main():
    database = r"./corpus.db"

    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS submissions (
                                        id integer PRIMARY KEY,
                                        author text NOT NULL,
                                        created_utc integer NOT NULL,
                                        title text NOT NULL,
                                        selftext text,
                                        id text NOT NULL,
                                        is_self integer NOT NULL,
                                        retrieved_on integer NOT NULL,
                                        num_comments integer NOT NULL
                                    ); """

    """sql_create_tasks_table = CREATE TABLE IF NOT EXISTS task (
                                id integer PRIMARY KEY,
                                name text NOT NULL,
                                priority integer,
                                status_id integer 

"""

if __name__ == "__main__":
    create_connection("./corpus.db")

