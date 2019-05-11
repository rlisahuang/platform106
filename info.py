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
import auth

def getConn(db):
    # conn = auth.mysqlConnectCNF(db='c9')
    conn = MySQLdb.connect(host='localhost',
                           user='ubuntu',
                           passwd='',
                           db=db)
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

def insertPost(conn, title, content, location, event_time, event_date, tags, username):
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
    val = (title, content, location, 0, None, event_time, event_date,username)
    # time_created based on mysql's now() function, but it is in UTC instead of
    # UTC-4 -- may have to fixed this later
    curs.execute("""INSERT INTO posts 
    (title, content, time_created, location, num_starred, imagefile, event_time, event_date,author) 
    VALUES (%s, %s, now(), %s, %s, %s, %s, %s,%s)""", val)
    conn.commit()

    curs.execute("""select LAST_INSERT_ID()""")
    #alternative version -- curs.execute("""select max(LAST_INSERT_ID()) from posts""")
    previous_pid_dict = curs.fetchone()
    previous_pid = previous_pid_dict["LAST_INSERT_ID()"]
    print(previous_pid)
    
    #inserting new tags into the tags table
    for tag in tags:
        curs.execute("""SELECT EXISTS(SELECT 1 from tags where tag_name = %s)""", [tag])
        tagExist = curs.fetchone().get("""EXISTS(SELECT 1 from tags where tag_name = '{}')""".format(tag))
        if not tagExist:
            curs.execute("""INSERT INTO tags (tag_name) VALUES (%s)""", [tag]) 
            conn.commit()

    #linking the tag and post in the tagged table
    for tag in tags:
        curs.execute("""select tid from tags where tag_name = %s""", [tag])
        tag_id = curs.fetchone().get('tid')
        curs.execute("""INSERT INTO tagged (tid, pid) VALUES (%s, %s)""", (tag_id, previous_pid))
        conn.commit()
    
    return previous_pid
    
def updatePost(conn, pid, title, content, location, imagefile, event_time, event_date,author,oldtags,newtags):
    '''
    <IN PROGRESS>
    Function that updates an existing post given information read from the front
    end.
    
    Potential Problem:
        The feature is not implemented in the front end and the current 
    implementation has not been tested yet. Changes might occur in the future.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    for tag in oldtags:
        curs.execute('''DELETE t1
                        FROM tagged t1
                        inner join tags t2
                        using (tid) 
                        where t1.pid = %s and t2.tag_name = %s''',[pid,tag])
        conn.commit()
    
    for tag in newtags:
        curs.execute("""select tid from tags where tag_name = %s""", [tag])
        tag_id = curs.fetchone()
        if not tag_id:
            curs.execute("""INSERT INTO tags (tag_name) VALUES (%s)""", [tag]) 
            conn.commit()
            curs.execute("""select LAST_INSERT_ID()""")
            tid = curs.fetchone()["LAST_INSERT_ID()"]
        else:
            tid = tag_id['tid']
        curs.execute('''INSERT INTO tagged (tid,pid) values (%s,%s)''',(tid,pid))
        conn.commit()
        
    sql = '''UPDATE posts 
            SET title = %s, content = %s, location = %s, imagefile = %s, event_time = %s, 
                event_date = %s, author=%s
            WHERE pid = %s'''
    val = (title, content, location, imagefile, event_time, event_date, author, pid)
    curs.execute(sql, val)
    conn.commit()
    
def deletePost(conn,pid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute("""delete from starred where pid = %s""",[pid])
    curs.execute("""delete from tagged where pid = %s""",[pid])
    curs.execute("""DELETE FROM posts WHERE pid = %s""", [pid])
    conn.commit()
    
def readOnePost(conn,pid):
    ''' 
    Function to return all info regarding one post to be displayed in the 
    post page given the pid.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
        
    curs.execute('''select * from posts where pid = %s''',[pid])
    post = curs.fetchone()
    post['tags'] = []
    if post is not None: # check if the pid is valid. if so, update the tag information
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
    if tags != '': # search with tags
        curs.execute('''select * from posts inner join tagged using (pid) 
                    inner join tags using (tid) 
                    where posts.title like %s and tags.tag_name like (%s)''', ["%"+keyword+"%","%"+tags+"%"])
    else: # search without tags
        curs.execute('''select * from posts where posts.title like %s''', ["%"+keyword+"%"])
                    
    posts = curs.fetchall()
    for p in posts:
        curs.execute('''select * from tags inner join tagged 
                        on tags.tid =tagged.tid where tagged.pid=%s''',[p.get('pid')])
        tags = [tag.get('tag_name') for tag in curs.fetchall()]
        p['tags'] = tags
        row2utf8(p)
    return posts

def isStarred(conn,pid,username):
    curs = curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from starred where pid = %s and username = %s''',(pid,username))
    return curs.fetchone()
    
def starPost(conn,pid,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    starred = isStarred(conn,pid,username)
    if starred is None:
        curs.execute('''insert into starred (pid,username) values (%s, %s)''',(pid,username))
        conn.commit()
    
def unstarPost(conn,pid,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    starred = isStarred(conn,pid,username)
    if starred is not None:
        curs.execute('''delete from starred where pid = %s and username = %s''',(pid,username))
        conn.commit()
    
def displayStarredEvents(conn,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from starred 
                    inner join posts using (pid) 
                    where starred.username = %s''',[username])
    return curs.fetchall()

def displayPostsByUser(conn,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from posts 
                    where author = %s''',[username])
    return curs.fetchall()
    
def isAuthor(conn,pid,username):
    curs = curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from posts where pid = %s and author = %s''',(pid,username))
    return (curs.fetchone() is not None)
    
def isFollowed(conn,tid,username):
    curs = curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from followed where tid = %s and username = %s''',(tid,username))
    return curs.fetchone()
    
def followTag(conn,tid,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    followed = isFollowed(conn,tid,username)
    if followed is None:
        curs.execute()
        curs.execute('''insert into followed (tid,username) values (%s, %s)''',(tid,username))
        conn.commit()
        curs.execute('''update tags set num_followers = num_followers + 1 where tid = %s''', (tid,))
        conn.commit()
        
def unfollowTag(conn,tid,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    followed = isFollowed(conn,tid,username)
    if followed is not None:
        curs.execute('''delete from followed where tid = %s and username = %s''',(tid,username))
        conn.commit()
        curs.execute('''update tags set num_followers = num_followers - 1 where tid = %s''', (tid,))
        conn.commit()

def displayFollowedTags(conn,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from followed 
                    inner join tags using (tid) 
                    where followed.username = %s''',[username])
    return curs.fetchall()

def getTags(conn):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute('''select * from tags''')
    allTags = curs.fetchall()
    
    return allTags


def getNumPostsThatUseTag(conn, tid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute('''select tid,count(*) from tagged where tid = %s group by tid''', (tid,))
    num = curs.fetchone()
    
    if num != None:
        return num['count(*)']
    else:
        return 0
    
def getUserPhone(conn,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute('''select phoneNum from accounts where username = %s''',[username])
    phoneNum = curs.fetchone()
    
    return phoneNum
    
def updateUserPhone(conn,username,newNum):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute('''update accounts set phoneNum = %s where username = %s''',(newNum,username))
    conn.commit()
    
def getTotalStarsByPost(conn,pid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute('''select count(*) from starred group by pid having pid = %s''',[pid])
    numStars = curs.fetchone()
    
    return numStars # {'count(*)': 1}
    
def getTotalStarsByUser(conn,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute('''select count(*) from starred group by username having username = %s''',[username])
    numStars = curs.fetchone()
    
    return numStars # {'count(*)': 1}
    
    
if __name__ == '__main__':
    conn = getConn('c9')
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    # posts = searchPosts(conn,keyword='f',tags='')
    # print(posts)
    # newpost = insertPost(conn,"testing_new_date_created", "testingfrompython", "tower", "5:01 pm", "2019-04-18")
    # print(newpost)
    #curs.execute("""SELECT EXISTS(SELECT 1 from tags where tag_name = %s)""", ['hello'])
    #test = curs.fetchone()["""EXISTS(SELECT 1 from tags where tag_name = '%s')""",('hello')]
    # print(isStarred(conn,10,'wendy'))
    # starPost(conn,10,'wendy')
    # print(isStarred(conn,10,'wendy'))
    # author18 = isAuthor(conn,18,'wanda')
    # print(author18) # true
    # author2 = isAuthor(conn,2,'wendy')
    # print(author2) # false
    # onePost = readOnePost(conn,19)
    # a =  onePost['event_time']
    # time_obj = datetime.datetime.strptime(str(a),'%I:%M:%S').time()
    # print(type(time_obj))
    # print(str(time_obj)[:5])
    n = getUserPhone(conn,"wendy")
    if n['phoneNum']:
        print("happy")
    else:
        print("sad")