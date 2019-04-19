#!/usr/bin/python2.7
'''
Platform 106 -- Draft Version
Authors: Lisa Huang, Shrunothra Ambati, Jocelyn Shiue
Date: 04/19/2019

info.py
File that contains functions for the backend.
'''

import sys
import MySQLdb
import time
import datetime

def getConn(db):
    conn = MySQLdb.connect(host='localhost',
                           user='ubuntu',
                           passwd='',
                           db=db)
    conn.autocommit(True)
    conn.set_character_set('utf8')
    curs = conn.cursor()
    curs.execute('set names utf8;')
    curs.execute('set character set utf8;')
    curs.execute('set character_set_connection=utf8;')
    return conn
    
#-------------------------------------------------------------------------------
# Methods needed for string character conversions

def utf8(val):
    return unicode(val,'utf8') if type(val) is str else val

def dict2utf8(dic):
    '''Because dictionaries are mutable,
    this mutates the dictionary;
    it also returns it'''
    for k,v in dic.iteritems():
        dic[k] = utf8(v)
    return dic

def tuple2utf8(tup):
    '''returns a new tuple, with byte strings
converted to unicode strings'''
    return tuple(map(utf8,tup))
    
def row2utf8(row):
    if type(row) is tuple:
        return tuple2utf8(row)
    elif type(row) is dict:
        return dict2utf8(row)
    else:
        raise TypeError('row is of unhandled type')

#-------------------------------------------------------------------------------
# Methods for getting information from, and updating the WMDB

def insertPost(conn, title, content, location, event_time, event_date, tags):
    '''
    Function that inserts a new post into the database and establish post-tag 
    relationships if given any tags.
    
    Potential Problem:
        1) The current implementation of the function assumes that titles are not 
    unique and does not prevent the user from creating a post with exactly the 
    same title and content as any existing post.
        2) the empty tag is considered as valid and could be inserted into the 
    database. Not harmful, but needs to be fixed.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    val = (title, content, location, 0, None, event_time, event_date)
    # time_created based on mysql's now() function, but it is in UTC instead of
    # UTC-4 -- may have to fixed this later
    curs.execute("""INSERT INTO posts 
    (title, content, time_created, location, num_starred, imagefile, event_time, event_date) 
    VALUES (%s, %s, now(), %s, %s, %s, %s, %s)""", val)

    curs.execute("""select LAST_INSERT_ID()""")
    previous_pid_dict = curs.fetchone()
    previous_pid = previous_pid_dict["LAST_INSERT_ID()"]
    print(previous_pid)
    
    #inserting new tags into the tags table
    for tag in tags:
        curs.execute("""SELECT EXISTS(SELECT 1 from tags where tag_name = %s)""", [tag])
        tagExist = curs.fetchone().get("""EXISTS(SELECT 1 from tags where tag_name = '{}')""".format(tag))
        if not tagExist:
            curs.execute("""INSERT INTO tags (tag_name) VALUES (%s)""", [tag]) 

    #linking the tag and post in the tagged table
    for tag in tags:
        curs.execute("""select tid from tags where tag_name = %s""", [tag])
        tag_id = curs.fetchone().get('tid')
        curs.execute("""INSERT INTO tagged (tid, pid) VALUES (%s, %s)""", (tag_id, previous_pid))
    
    return previous_pid
    
def updatePost(conn, pid, title, content, location, num_starred, imagefile, event_time, event_date):
    '''
    <IN PROGRESS>
    Function that updates an existing post given information read from the front
    end.
    
    Potential Problem:
        The feature is not implemented in the front end and the current 
    implementation has not been tested yet. Changes might occur in the future.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    sql = '''UPDATE posts 
            SET title = %s, content = %s, location = %s, imagefile = %s, event_time = %s, 
                event_date = %s, WHERE pid = %s'''
    val = (title, content, location, imagefile, event_time, event_date, pid)
    return curs.execute(sql, val)
    
def readOnePost(conn,pid):
    ''' 
    Function to return all info regarding one post to be displayed in the 
    post page given the pid.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
        
    curs.execute('''select * from posts where pid = %s''',[pid])
    post = curs.fetchone()
    if post: # check if the pid is valid. if so, update the tag information
        curs.execute('''select * from tags inner join tagged 
                        on tags.tid =tagged.tid where tagged.pid=%s''',[pid])
        tags = [tag.get('tag_name') for tag in curs.fetchall()]
        post['tags'] = tags
    return post
    
def searchPosts(conn,keyword='',tags=''):
    ''' 
    Function to return all posts containing the given keyword and tags to be 
    displayed in the result page.
    
    Potential Problems:
        The current implementation only allows for searching by keyword (basicSearch)
    or keyword+tags (advancedSearch). Potentially, we would also want to allow 
    users to search posts according to event date, location, etc. Changes to this
    function might occur in the future.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    if tags != '': # search without tags
        curs.execute('''select * from posts inner join tagged using (pid) 
                    inner join tags using (tid) 
                    where posts.title like %s and tags.tag_name in (%s)''', ["%"+keyword+"%",tags])
    else: # search with tags
        curs.execute('''select * from posts where posts.title like %s''', ["%"+keyword+"%"])
                    
    posts = curs.fetchall()
    for p in posts:
        curs.execute('''select * from tags inner join tagged 
                        on tags.tid =tagged.tid where tagged.pid=%s''',[p.get('pid')])
        tags = [tag.get('tag_name') for tag in curs.fetchall()]
        p['tags'] = tags
        row2utf8(p)
    return posts
    
if __name__ == '__main__':
    conn = getConn('c9')
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    # posts = searchPosts(conn,keyword='f',tags='')
    # print(posts)
    # newpost = insertPost(conn,"testing_new_date_created", "testingfrompython", "tower", "5:01 pm", "2019-04-18")
    # print(newpost)
    curs.execute("""SELECT EXISTS(SELECT 1 from tags where tag_name = %s)""", ['hello'])
    test = curs.fetchone()["""EXISTS(SELECT 1 from tags where tag_name = '%s')""",('hello')]
    print(test)