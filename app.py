#!/usr/bin/python2.7
'''
Platform 106 -- Draft Version
Authors: Lisa Huang, Shrunothra Ambati, Jocelyn Shiue
Date: 04/19/2019

app.py
The main file of the app.
'''

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory,jsonify)
from werkzeug.utils import secure_filename

app = Flask(__name__)

import datetime

import info
import sys,os
import bcrypt
import MySQLdb
import imghdr

app = Flask(__name__)
app.secret_key = 'draft'

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

app.config['UPLOADS'] = 'uploads'
app.config['MAX_UPLOAD'] = 256000

@app.route('/')
def home():
    return render_template('home.html', title="Home", logged_in=session.get('logged_in',False))
    
@app.route('/login/')
def login():
    return render_template('login.html', title = "Login", logged_in=session.get('logged_in',False))
    
@app.route('/tagsList')
def tagsList():
    logged_in = session.get('logged_in', False)
    if not logged_in: # the link is only available after the user is logged in
        flash("Please log in!")
        return redirect(url_for("login"))
    
    conn = info.getConn('c9')
    tags = info.getTags(conn)
    print(tags)
    # nums = info.getNumPostsThatUseTag(conn)
    # print(nums)
    #need to add nums info to tags dictionary
    for tag in tags:
        followed = info.isFollowed(conn, tag['tid'], session.get('username'))
        if followed == None:
            followed = "0"
        else:
            followed = "1"
        tag['followed'] = followed
        
    
    return render_template('tagsList.html', title = "Tags List", tags=tags, logged_in=logged_in)
    
@app.route('/userPortal/')
def userPortal():
    logged_in = session.get('logged_in', False)
    if not logged_in: # the link is only available after the user is logged in
        flash("Please log in!")
        return redirect(url_for("login"))
    
    conn = info.getConn('c9')
    usr=session.get('username')
    stars = info.displayStarredEvents(conn,usr)
    posts = info.displayPostsByUser(conn,usr)
    follows = info.displayFollowedTags(conn,usr)
    
    for star in stars:
        isStarred = info.isStarred(conn,star['pid'],usr)
        starred = "0" if isStarred is None else "1"
        star['starred'] = starred
            
    for follow in follows:
        followed = info.isFollowed(conn, follow['tid'], usr)
        if followed == None:
            followed = "0"
        else:
            followed = "1"
        follow['followed'] = followed

    return render_template('userPortal.html', title = "User Portal", stars=stars,
                        posts=posts, follows=follows, username=usr,logged_in=logged_in)

@app.route('/userPortal/updateProfile/', methods=['GET','POST'])
def updateProfile():
    logged_in = session.get('logged_in', False)
    if not logged_in: # the link is only available after the user is logged in
        flash("Please log in!")
        return redirect(url_for("login"))
    
    # information from database
    conn = info.getConn('c9')
    usr=session.get('username')
    oldNum = info.getUserPhone(conn,usr)
    if request.method == "GET":
        # set up the page and pre-fill the form using info from database
        if oldNum['phoneNum']:
            num = oldNum['phoneNum']
        else:
            num = ""
        return render_template('updateProfile.html', num=num,logged_in=session.get('logged_in',False))
    else:
        # the update function, grab info filled in by the user
        newNum = request.form.get("phoneNum")

        info.updateUserPhone(conn, usr, newNum)
        print("Phone number of ({}) was updated successfully.".format(usr))
        
        return redirect(url_for('updateProfile'))


#Builds the create post page
@app.route('/createPost', methods=['GET','POST'])
def createPost():
    logged_in = session.get('logged_in', False)
    if not logged_in: # the link is only available after the user is logged in
        flash("Please log in!")
        return redirect(url_for("login"))
    conn = info.getConn('c9')
    if request.method == 'GET':
        #blank form rendered when page is first visited
        return render_template('createPost.html', 
                          title="Create a Post!",post=session.get('newpost',None), logged_in=logged_in)
                          
    else:
        #flash warning messages if form is filled out incorrectly
        
        error = False
        title = request.form.get('post-title','')
        content = request.form.get('post-content','')
        location = request.form.get('post-location','')
        event_time = request.form.get('post-eventtime','')
        event_date = request.form.get('post-eventdate','')
        tags = request.form.get('post-tags','')
        picture = request.files.get('post-picture',None)
        print(picture)
        
        newpost = {"title":title,"content":content,"location":location,
                "event_time":event_time,"event_date":event_date, "tags":tags,'picture':picture}

        if title == "":
            flash('Missing value: Please enter a title for your event!')
            error = True
        if location == "":
            flash('Missing value: Please enter a location for your event!')
            error = True
        if event_date == "":
            flash('Missing value: Please enter a date for your event!')
            error = True
        if event_time == "":
            flash('Missing value: Please enter a time for your event!')
            error = True
        # if picture is None:
        #      flash('Missing value: Please upload a picture for your event!')
        #      error = True

        # test if any errors occured then take user back to insert page, with 
        # the info that they already provided prefilled
        if error:
            return render_template('createPost.html', title="Create a Post!",post=newpost, logged_in=logged_in)
        else: 
            pid = info.insertPost(conn, title, content, location, event_time, event_date, tags.split(','), session.get('username'))
            
            try: #Handing the image uploading
                fsize = os.fstat(picture.stream.fileno()).st_size
                print 'file size is ',type(fsize)
                # if fsize == 0:
                    # return render_template('createPost.html', title="Create a Post!",post=newpost, logged_in=logged_in)
                if fsize > app.config['MAX_UPLOAD']:
                    raise Exception('File is too big')
                mime_type = imghdr.what(picture)
                if mime_type.lower() not in ['jpeg','gif','png']:
                    raise Exception('Not a JPEG, GIF or PNG: {}'.format(mime_type))
                filename = secure_filename("{}.{}".format(pid,mime_type))
                print(filename)
                pathname = os.path.join(app.config['UPLOADS'],filename)
                picture.save(pathname)
                flash('Upload successful')
                conn = info.getConn('c9')
                curs = conn.cursor()
                curs.execute('''UPDATE posts 
                                SET imagefile = %s
                                WHERE pid = %s''',
                             [filename, pid])
                            #test if any errors occured then take user back to insert page
                conn.commit()
            
            
                return redirect(url_for('displayPost', pid=pid))
        
            except Exception as err:
                flash('Upload failed {why}'.format(why=err))
                #blank form rendered when page is first visited
                return render_template('createPost.html', 
                                  title="Create a Post!",post=newpost, logged_in=logged_in)
                
        


# url for post page
@app.route('/posts/<int:pid>')
def displayPost(pid):
    logged_in = session.get('logged_in', False)

    conn = info.getConn('c9')
    postInfo = info.readOnePost(conn,pid)
    
    if logged_in:
        username = session.get('username')
        starred = info.isStarred(conn,pid,username)
        isAuthor = info.isAuthor(conn,pid,username)
        postInfo["starred"] = "0" if starred is None else "1"
    
        return render_template('post.html',isAuthor=isAuthor,post=postInfo,logged_in=session.get('logged_in',False))
    
    else:
        return render_template('post.html',post=postInfo,logged_in=session.get('logged_in',False))
   
@app.route('/pic/<pid>')
def pic(pid):
    conn = info.getConn('c9')
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select pid,imagefile from posts where pid = %s''', [pid])
    pic = curs.fetchone()['imagefile']
    if pic is None:
        flash('No picture for {}'.format(pid))
        val = ""
    else:
        val = send_from_directory(app.config['UPLOADS'],pic)
    return val

 
@app.route('/updatePost/<int:pid>',methods=['GET','POST'])
def updatePost(pid):
    logged_in = session.get('logged_in', False)
    if not logged_in: # the link is only available after the user is logged in
        flash("Please log in!")
        return redirect(url_for("login"))
    conn = info.getConn('c9')
    # information from database
    post = info.readOnePost(conn,pid)
    time_obj = datetime.datetime.strptime(str(post['event_time']),'%H:%M:%S').time()
    post['event_time'] = str(time_obj)[:5] # hh:mm in 12-hour format
    oldtags = post.get('tags')
    
    if request.method == "GET":
        # set up the page and pre-fill the form using info from database
        if len(oldtags) == 0:
            post['tags'] = ''
        else:
            post['tags'] = ",".join(oldtags)
        return render_template('updatePost.html', post=post,logged_in=session.get('logged_in',False))
    
    else:
        # the delete function, flash message and redirect to home page
        if request.form.get('submit') == 'delete':
            info.deletePost(conn,pid)
            print("Post ({}) was deleted successfully.".format(pid))
            return redirect(url_for('userPortal'))
        # the update function, grab info filled in by the user
        else:
            title = request.form.get('post-title')
            content = request.form.get('post-content')
            location = request.form.get('post-location')
            date = request.form.get('post-eventdate')
            time = request.form.get('post-eventtime')
            newtags = request.form.get('post-tags','')
            picture = request.files.get('post-picture',None)
            


            info.updatePost(conn,pid, title, content, location, None,time,date,session.get('username'),oldtags,newtags.split(','))
            print("Post ({}) was updated successfully.".format(pid))
            
            try: #Handing the image uploading
                fsize = os.fstat(picture.stream.fileno()).st_size
                print 'file size is ',type(fsize)
               
                if fsize > app.config['MAX_UPLOAD']:
                    raise Exception('File is too big')
                mime_type = imghdr.what(picture)
                if mime_type.lower() not in ['jpeg','gif','png']:
                    raise Exception('Not a JPEG, GIF or PNG: {}'.format(mime_type))
                filename = secure_filename("{}.{}".format(pid,mime_type))
                print(filename)
                pathname = os.path.join(app.config['UPLOADS'],filename)
                picture.save(pathname)
                flash('Upload successful')
                conn = info.getConn('c9')
                curs = conn.cursor()
                curs.execute('''UPDATE posts 
                                SET imagefile = %s
                                WHERE pid = %s''',
                             [pid, filename])
                            #test if any errors occured then take user back to insert page
                conn.commit()
            
            
                return redirect(url_for('displayPost', pid=pid))
        
            except Exception as err:
                flash('Upload failed {why}'.format(why=err))
                #blank form rendered when page is first visited
                return render_template('updatePost.html', 
                                  title="Create a Post!",post=post, logged_in=logged_in)
            
   
            
                                  
# url for simple search FORM
@app.route('/basicSearch',methods=['POST'])
def basicSearch():
    title = ''
    
    if request.method == 'POST':
        title = request.form.get('searchterm')
        # save the keyword and tags in session to be displayed in generalFeed
        session['keyword'] = title
        session['tags'] = ''

        return redirect(url_for("generalFeed"))
    return redirect(request.referrer)

# url for advanced search FORM (in a search page)        
@app.route('/advancedSearch',methods=['POST'])
def advancedSearch():
    if request.method == 'POST':
        title = request.form.get('searchterm','')
        tags = request.form.get('searchtags','')
        # save the keyword and tags in session to be displayed in generalFeed
        session['keyword'] = title
        session['tags'] = tags
        
        # event time, location... more to follow
        return redirect(url_for("generalFeed"))
    return redirect(request.referrer)

# url that hosts the advanced search form as well as search results    
@app.route('/generalFeed/')
def generalFeed():
    logged_in = session.get('logged_in', False)
    # if not logged_in: # the link is only available after the user is logged in
        # flash("Please log in!")
        # return redirect(url_for("login"))
    keyword = session.pop('keyword','')
    tags = session.pop('tags','')
    conn = info.getConn('c9')
    posts = info.searchPosts(conn,keyword,tags)
    tagHolder = "enter tags separated by comma: e.g. cs, club" if (tags != '') else tags
    
    return render_template('generalFeed.html',title = "General Feed", keyword=keyword,tags=tagHolder,posts=posts,logged_in=session.get('logged_in',False))    

    
# url that hosts the advanced search form as well as search results    
@app.route('/searchTag/<tag>')
def searchTag(tag):
    session['tags'] = tag
    return redirect(url_for("generalFeed"))


@app.route('/join/', methods=["POST"])
def join():
    try:
        username = request.form['username']
        passwd1 = request.form['password1']
        passwd2 = request.form['password2']
        if passwd1 != passwd2:
            flash('passwords do not match')
            return redirect( url_for('index'))
        hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
        conn = info.getConn('c9')
        curs = conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            curs.execute('INSERT into accounts(username,hashed) VALUES(%s,%s)',
                     [username, hashed])
            conn.commit()
        except MySQLdb.IntegrityError as err:
            flash('That username is taken')
            return redirect(url_for('login'))
            
        session['username'] = username
        session['logged_in'] = True
        return redirect( url_for('userPortal') )
        
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('login') )
        
@app.route('/loginAction/', methods=["POST"])
def loginAction():
    try:
        username = request.form['username']
        passwd = request.form['password']
        conn = info.getConn('c9')
        curs = conn.cursor(MySQLdb.cursors.DictCursor)
        curs.execute('SELECT hashed FROM accounts WHERE username = %s',
                     [username])
        row = curs.fetchone()
        if row is None:
            flash('login incorrect. Try again or join')
            return redirect( url_for('index'))
        hashed = row['hashed']
        # strings always come out of the database as unicode objects
        if bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8')) == hashed:
            flash('successfully logged in as '+username)
            session['username'] = username
            session['logged_in'] = True
            return redirect( url_for('userPortal') )
        else:
            flash('login incorrect. Try again or join')
            return redirect( url_for('login'))
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('login') )

@app.route('/logout/')
def logout():
    try:
        if 'username' in session:
            username = session['username']
            session.pop('username')
            session.pop('logged_in')
            flash('You are logged out')
            return redirect(url_for('home'))
        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('login') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('login') )
        
""" The route for star/unstar post with ajax """     
@app.route('/starAjax',methods=['POST'])      
def starAjax():
    if request.method == 'POST':
        conn = info.getConn('c9')
        usr = session.get('username')
        pid = request.form.get('pid')
        starred = request.form.get('starred')

        # check if user is logged in
        if usr is not None:
            print(starred)
            print(type(starred))
            if starred == "0":
                info.starPost(conn,pid,usr)
                print("post {} is starred by user {}".format(pid,usr))
                return jsonify( {'error':False, 'pid': pid, 'starred': "1"} )
            else:
                info.unstarPost(conn,pid,usr)
                print("post {} is unstarred by user {}".format(pid,usr))
                return jsonify( {'error':False, 'pid': pid, 'starred': "0"} )
        else:
            print("Need to login")
            return jsonify( {'error': True, 'err': "need to login"} )

""" The route for follow/unfollow tag with ajax """     
@app.route('/followAjax',methods=['POST'])      
def followAjax():
    if request.method == 'POST':
        conn = info.getConn('c9')
        usr = session.get('username')
        tid = request.form.get('tid')
        followed = request.form.get('followed')
        print(followed)

        # check if user is logged in
        if usr is not None:
            if followed == "0":
                print(tid)
                print(usr)
                info.followTag(conn,tid,usr)
                print("post {} is followed by user {}".format(tid,usr))
                return jsonify( {'error':False, 'tid': tid, 'followed': "1"} )
            else:
                info.unfollowTag(conn,tid,usr)
                print("post {} is unfollowed by user {}".format(tid,usr))
                return jsonify( {'error':False, 'tid': tid, 'followed': "0"} )
        else:
            print("Need to login")
            return jsonify( {'error': True, 'err': "need to login"} )

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)

