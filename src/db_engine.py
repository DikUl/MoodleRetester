#-*- coding: utf-8 -*-
'''
Created on 30.05.2011

@author: dik
'''

import MySQLdb

class MoodleDBEngine(object):
    '''
    classdocs
    '''
    host = 'localhost'
    dbs = 'moodle'
    login = None
    password = None
    conn = None
    cur = None


    def __init__(self, host, db, login, password):
        '''
        Constructor
        '''
        self.host = host
        self.login = login
        self.password = password
        self.dbs = db
        self.conn = MySQLdb.connect(host=host, 
                                    db=db, 
                                    user=login, 
                                    passwd=password, 
                                    init_command='SET NAMES utf8')
        self.cur = self.conn.cursor()
        self.tcur = self.conn.cursor()
    
    def test1(self):
        '''
        Test of DB
        '''
        self.cur.execute("""SELECT * FROM mdl_question_states""")
        for i in self.cur.fetchall():
            print i
            
    def get_struct(self):
        self.cur.execute()

if __name__ == "__main__":
    dbe = MoodleDBEngine('localhost', 'moodle', 'root', 'dik888')
    dbe.test1()