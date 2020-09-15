import unittest

import subredditscraper
import os

class TestDB(unittest.TestCase):
    def test_create_connection(self):
        conn = db.create_connection(r"test.db")
        self.assertTrue(os.path.exists("test.db"))

    #def test_create_table_submissions(self):

    #def test_create_table_comments(self):

    #def test_insert_submission(self):

    #def test_insert_comment(self): 

if __name__ == '__main__':
    unittest.main()
