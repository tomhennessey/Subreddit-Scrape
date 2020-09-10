#!/usr/bin/env python3

# cribbed from sqlitetutorial.net/sqlite-python

import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


"""
TABLE1: 
    author
    created_utc
    title
    selftext
    id
    is_self
    retrieved_on
    num_comments
    retireved_on

TABLE2:

"""

def main():
    database = r"./corpus.db"

    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS projects (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        begin_date text,
                                        end_date text
                                    ); """

    sql_create_tasks_table = """ CREATE TABLE IF NOT EXISTS task (
                                id integer PRIMARY KEY,
                                name text NOT NULL,
                                priority integer,
                                status_id integer 



if __name__ == "__main__":
    create_connection("./corpus.db")


`
