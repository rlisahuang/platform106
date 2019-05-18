#!/usr/bin/python2.7
'''
Platform 106 -- Alpha Version
Authors: Lisa Huang, Shrunothra Ambati, Jocelyn Shiue
Date: 05/13/2019

info.py
File that contains functions for the backend.
'''

import sys
import MySQLdb
import time
import datetime
import auth
import operator

def getConn(db):
    #conn = auth.mysqlConnectCNF(db='c9')
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
# Methods for getting information from, and updating the C9

def insertPost(conn, title, content, location, event_time, event_date, tags, username):
    '''
    Function that inserts a new post into the database and establish post-tag 
    relationships if given any tags.
    
    Potential Problem:
        1) The current implementation of the function assumes that titles are not 
    unique and does not prevent the user from creating a post with exactly the 
    same title and content as any existing post.
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
    previous_pid_dict = curs.fetchone()
    previous_pid = previous_pid_dict["LAST_INSERT_ID()"]
    print(previous_pid)
    
    curs.execute("""LOCK TABLES tags WRITE, tagged WRITE""")
    # inserting new tags into the tags table and linking the tag and post in the tagged table
    for tag in tags:
        if tag != "":
            curs.execute("""SELECT EXISTS(SELECT 1 from tags where tag_name = %s)""", [tag])
            tagExist = curs.fetchone().get("""EXISTS(SELECT 1 from tags where tag_name = '{}')""".format(tag))
            if not tagExist:
                curs.execute("""INSERT INTO tags (tag_name) VALUES (%s)""", [tag]) 
                conn.commit()
            curs.execute("""select tid from tags where tag_name = %s""", [tag])
            tag_id = curs.fetchone().get('tid')
            curs.execute("""INSERT INTO tagged (tid, pid) VALUES (%s, %s)""", (tag_id, previous_pid))
            conn.commit()
    curs.execute("""UNLOCK TABLES""")
    
    return previous_pid
    
def updatePost(conn, pid, title, content, location, imagefile, event_time, event_date,author,oldtags,newtags):
    '''
    Function that updates an existing post in the database, release existing post-tag relationships
    if any old tags are removed and establish new post-tag relationships if given any new tags.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)

    for tag in oldtags:
        curs.execute('''DELETE t1
                        FROM tagged t1
                        inner join tags t2
                        using (tid) 
                        where t1.pid = %s and t2.tag_name = %s''',[pid,tag])
        conn.commit()
    
    curs.execute("""LOCK TABLES tags WRITE, tagged WRITE""")
    for tag in newtags:
        if tag != "":
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
    curs.execute("""UNLOCK TABLES""")
        
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
    
    # delete tags that are not used by any posts entirely from the database
    curs.execute("""delete from followed where tid not in (select tid from tagged)""")
    curs.execute("""delete from tags where tid not in (select tid from tagged)""")
    conn.commit()
    
def deleteTag(conn,tid):
    # only admins have the authorization to delete tags
    curs = conn.cursor(MySQLdb.cursors.DictCursor)

    curs.execute("""delete from followed where tid = %s""",[tid])
    curs.execute("""delete from tagged where tid = %s""",[tid])
    curs.execute("""delete from tags where tid = %s""",[tid])
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
    users to search posts according to event date, location, etc. We would have loved this
    to occur in the beta version, but we didn't have time :(
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
    ''' This post is used to determine whether a post has been starred. It returns
        a dictionary with the pid and the username of the user if the user has
        starred that post. Otherwise, it returns an empty set. 
    '''
    curs = curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from starred where pid = %s and username = %s''',(pid,username))
    return curs.fetchone()
    
def starPost(conn,pid,username):
    ''' This function is used when a user wants to 'star' a post. It adds an entry
        to the starred table that shows that the user has starred that post. It 
        also updates the posts table to show the new number of stars that the 
        post has.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    starred = isStarred(conn,pid,username)
    if starred is None:
        curs.execute('''insert into starred (pid,username) values (%s, %s)''',(pid,username))
        conn.commit()
        curs.execute('''update posts set num_starred = num_starred + 1 where pid = %s''', (pid,))
        conn.commit()
    
def unstarPost(conn,pid,username):
    ''' This function is used when a user wants to 'unstar' a post. It removes
        the relationship between that user and the post they unstarred from the 
        starred table. It also updates the posts table to reflect the new number 
        of stars that that post has. 
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    starred = isStarred(conn,pid,username)
    if starred is not None:
        curs.execute('''delete from starred where pid = %s and username = %s''',(pid,username))
        conn.commit()
        curs.execute('''update posts set num_starred = num_starred - 1 where pid = %s''', (pid,))
        conn.commit()
    
def displayStarredEvents(conn,username):
    ''' This function returns all the events that are starred by a particular user.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from starred 
                    inner join posts using (pid) 
                    where starred.username = %s''',[username])
    return curs.fetchall()

def displayPostsByUser(conn,username):
    ''' This function returns all the posts where the user is also the author.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from posts 
                    where author = %s''',[username])
    return curs.fetchall()
    
def isAuthor(conn,pid,username):
    ''' This function is used to determine whether the user is the author of a 
        particular post. 
    '''
    curs = curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from posts where pid = %s and author = %s''',(pid,username))
    return (curs.fetchone() is not None)
    
def isFollowed(conn,tid,username):
    ''' This function is used to determine whether a particular tag is followed.
        It returns a dictionary with the tag id and the username of the user if
        the tag is followed, but returns an empty set if the user is not following
        that tag.
    '''
    curs = curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from followed where tid = %s and username = %s''',(tid,username))
    return curs.fetchone()
    
def followTag(conn,tid,username):
    ''' This function adds an entry to the followed table when a user follows a 
        particular tag. It also updates the tags table to reflect the number of 
        users that are following that tag.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    followed = isFollowed(conn,tid,username)
    if followed is None:
        curs.execute('''insert into followed (tid,username) values (%s, %s)''',(tid,username))
        conn.commit()
        curs.execute('''update tags set num_followers = num_followers + 1 where tid = %s''', (tid,))
        conn.commit()
    curs.execute('''select num_followers from tags where tid = %s''',[tid])
    return curs.fetchone()
        
        
def unfollowTag(conn,tid,username):
    ''' This function removes the relationship between a tag and a user when they
        decide to unfollow a tag. It also updates the tag table and subtracts 1
        from the number of followers of that particular tag.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    followed = isFollowed(conn,tid,username)
    if followed is not None:
        curs.execute('''delete from followed where tid = %s and username = %s''',(tid,username))
        conn.commit()
        curs.execute('''update tags set num_followers = num_followers - 1 where tid = %s''', (tid,))
        conn.commit()
    curs.execute('''select num_followers from tags where tid = %s''',[tid])
    return curs.fetchone()

def displayFollowedTags(conn,username):
    ''' This function returns a dictionary of all the tags followed by the user
        and the info associated with them, including number of followers and number of posts.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select t1.tid,username,tag_name,num_followers,num_posts from 
                        followed t1 
                            inner join 
                        tags t2 
                            on t1.tid = t2.tid 
                            inner join 
                        (select tid,count(*) as num_posts from tagged group by tid) t3 
                            on t2.tid = t3.tid
                        where username = %s''',[username])
    return curs.fetchall()

def getTags(conn, tag_name=''):
    ''' This function returns a dictionary of all the tags in the tags table including num_posts.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select t1.tid,tag_name,num_followers,num_posts from tags t1 
                    inner join 
                    (select tid,count(*) as num_posts from tagged group by tid) t2 
                    on t1.tid = t2.tid 
                    where tag_name like %s''',["%"+tag_name+"%"])
    allTags = curs.fetchall()
    
    return allTags


def getNumPostsThatUseTag(conn, tid):
    ''' This function returns that number of posts that use a particular tag.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute('''select tid,count(*) from tagged where tid = %s group by tid''', (tid,))
    num = curs.fetchone()
    
    if num != None:
        return num['count(*)']
    else:
        return 0
    
def getSubscriberPhoneNums(conn,pid):
    ''' This function returns the phone numbers of all users who starred a certain event.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute("""select accounts.username, phoneNum from accounts 
                inner join starred on accounts.username = starred.username 
                where pid = %s""",[pid])

    return curs.fetchall()

def getUserPhone(conn,username):
    ''' This function returns the phone number of the user from the accounts 
        table.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute('''select phoneNum from accounts where username = %s''',[username])
    phoneNum = curs.fetchone()
    
    return phoneNum['phoneNum']
    
def updateUserPhone(conn,username,newNum):
    ''' This function updates the user's phone number in the accounts table.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute('''update accounts set phoneNum = %s where username = %s''',(newNum,username))
    conn.commit()
    
def getUserEmail(conn,username):
    ''' This function returns the email of the user from the accounts 
        table.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute('''select email from accounts where username = %s''',[username])
    email = curs.fetchone()
    
    return email['email']
    
def updateUserEmail(conn,username,newEmail):
    ''' This function updates the user's email address in the accounts table.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute('''update accounts set email = %s where username = %s''',(newEmail,username))
    conn.commit()
    
def getAuthorEmail(conn, author):
    ''' This function returns the email of the author of a post from the accounts 
        table.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute('''select email from accounts where username = %s''',[author])
    email = curs.fetchone()
    
    return email['email']
    
def getTotalStarsByPost(conn,pid):
    ''' This function gets the total number of stars that each post has. 
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute('''select pid, count(*) as stars from starred where pid = %s''',[pid])
    numStars = curs.fetchone()
    
    return numStars # {'pid': pid, 'stars': num_stars}
    
def getTotalStarsByUser(conn,username):
    ''' This function gets the total number of posts that each user has starred.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute('''select username, count(*) as stars from starred where username = %s''',[username])
    numStars = curs.fetchone()
    
    return numStars # {'username': usr, 'stars': num_stars}
    
def getFeaturedEvents(conn):
    ''' This function gets the three posts with the highest number of 'stars' 
        because we want to feature events that students are most interested in
        on our home page. The function also uses an inner join to get the tags
        associated with each of those posts.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute('''select * from posts order by num_starred desc limit 3''')
    featuredEvents = curs.fetchall()
    
    for p in featuredEvents:
        curs.execute('''select * from tags inner join tagged 
                        on tags.tid =tagged.tid where tagged.pid=%s''',[p.get('pid')])
        tags = [tag.get('tag_name') for tag in curs.fetchall()]
        p['tags'] = tags
        row2utf8(p)
        
    return featuredEvents

def isEventDayTomorrow(conn, pid):
    ''' Checks whether the event date of the given event is tomorrow '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute("""select event_date from posts where pid = %s""", (pid,))
    datetime_db = curs.fetchone()
    
    event_date = datetime_db['event_date']
    tomorrow_date = datetime.date.today()+datetime.timedelta(days=1)
    
    if event_date == tomorrow_date:
        return True
    return False
    
def sortPosts(conn):
    ''' <PROBLEM>: This method intends to sort the events in General Feed, but does not
    work as expected. '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    unsortedPosts = searchPosts(conn)
    sortedPosts = sorted(unsortedPosts, key=lambda elem: elem['title'].lower)
    
    return sortedPosts
    
    
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

    # n = readOnePost(conn,1)
    # print(n)
    # curs.execute("""select event_time,event_date from posts where pid = 16""")
    # datetime_db = curs.fetchone()
    # print(type(datetime_db['event_time']))
    # print(datetime_db['event_time'])
    # print(type(datetime_db['event_date']))
    # print("event date is ")
    # print(datetime_db['event_date'])
    # print("today's date is ")
    # print(datetime.date.today())
    # print("tomorrow's date is ")
    # print(datetime.date.today()+datetime.timedelta(days=1))
    # print(datetime_db['event_date'] == datetime.date.today()+datetime.timedelta(days=1))
    
    curs.execute('''select pid,title from posts''')
    posts = curs.fetchall()
    # print(posts)
    unsortedPosts = [{'pid': 1, 'title': 'c'}, {'pid': 2, 'title': 'b'}, {'pid': 3, 'title': 'a'}]
    print(type(unsortedPosts))
    print(posts)
    sortedPosts = sorted(posts, key=lambda elem: elem['title'].lower())
    print(sortedPosts)
