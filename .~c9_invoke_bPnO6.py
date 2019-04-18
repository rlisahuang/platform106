#!/usr/bin/python2.7

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

def insertPost(conn, title, content, location, event_time, event_date):
    '''Function to insert a new post into the database
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    ts = time.time()
    
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%m-%d-%Y %H:%M:%S')
    # sql = """INSERT INTO posts 
    # (title, content, date_created, location, num_starred, imagefile, event_time, event_date) 
    # VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    val = (title, content, timestamp, location, 0, None, event_time, event_date)
    curs.execute("""INSERT INTO posts 
def getPID(conn,title,content,location,event_time,event_date):
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", val)
    curs.execute("""select LAST_INSERT_ID()""")
    return curs.fetchone()
    
# def getPID(conn,title,content,location,event_time,event_date):
    
    
def updatePost(conn, pid, title, content, location, num_starred, imagefile, event_time, event_date):
    '''Function to udpate a post already in the database
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%m-%d-%Y %H:%M:%S')
    sql = "UPDATE posts SET title = %s, content = %s, date_created = %s, location = %s, num_starred = %s, imagefile = %s, event_time = %s, event_date = %s, WHERE pid = %s"
    val = (title, content, timestamp, location, 0, None, event_time, event_date, pid)
    return curs.execute(sql, val)
    
def readOnePost(conn,pid):
    ''' Function to return all info regarding one post to be displayed in the 
        post page
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
        
    curs.execute('''select * from posts where pid = %s''',[pid])
    return curs.fetchone()
    
# def searchPostsByKeyword(conn,keyword):
#     ''' Function to return all posts containing the given keyword
#         to be displayed in the post page
#     '''
#     curs = conn.cursor(MySQLdb.cursors.DictCursor)
#     curs.execute('''select * from posts where title like %s''', ["%"+keyword+"%"])
#     all = curs.fetchall()
#     for p in all:
#         row2utf8(p)
#     return all
    
def searchPosts(conn,keyword='',tags=''):
    ''' Function to return all posts containing the given keyword
        to be displayed in the post page;
        !! "tags" is a string of tags, separated by comma (should ask the user to do so in the form)
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    if tags != '':
        curs.execute('''select * from posts inner join tagged using (pid) 
                    inner join tags using (tid) 
                    where posts.title like %s and tags.tag_name in (%s)''', ["%"+keyword+"%",tags])
    else:
        curs.execute('''select * from posts where posts.title like %s''', ["%"+keyword+"%"])
                    
    all = curs.fetchall()
    for p in all:
        row2utf8(p)
    return all
    
if __name__ == '__main__':
    conn = getConn('c9')
    posts = searchPosts(conn,keyword='f',tags='')
    print(posts)
    newpost = insertPost(conn,"testing123", "testingfrompython", "tower", "5:55 pm", "2019-04-18")
    print(newpost)