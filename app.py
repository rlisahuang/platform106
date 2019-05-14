#!/usr/bin/python2.7
'''
Platform 106 -- Alpha Version
Authors: Lisa Huang, Shrunothra Ambati, Jocelyn Shiue
Date: 05/13/2019

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
#app.config['MAX_UPLOAD'] = 256000
app.config['MAX_UPLOAD'] = 2097152 #-- 2.0 MB

@app.route('/')
def home():
    conn = info.getConn('c9')
    featuredEvents = info.getFeaturedEvents(conn)
    print (featuredEvents)
    return render_template('home.html', title="Home", featuredEvents = featuredEvents, logged_in=session.get('logged_in',False))
    
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
    tag = session.pop('tags','')
    tags = info.getTags(conn, tag)

    # update each tag dictionary with info indicating 1) whether it is followed by
    # this user, 2) how many posts that use this tag and 3) how many followers
    # in total
    for tag in tags:
        followed = info.isFollowed(conn, tag['tid'], session.get('username'))
        if followed == None:
            followed = "0"
        else:
            followed = "1"
        tag['followed'] = followed
        tag['num_posts'] = info.getNumPostsThatUseTag(conn, tag['tid'])
    
    return render_template('tagsList.html', title = "Tags List", tags=tags, logged_in=logged_in)
 
# url for tags search FORM (in tagsList page)        
@app.route('/tagsSearch',methods=['POST'])
def tagsSearch():
    if request.method == 'POST':
        tag = request.form.get('searchtags','')
        # save the tags in session to be displayed in generalFeed
        session['tags'] = tag
        
        return redirect(url_for("tagsList"))
    return redirect(request.referrer)
    
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
    for follow in follows:
        follow['num_posts'] = info.getNumPostsThatUseTag(conn, follow['tid'])
    
    # update each star with explicit string indicating whether the post is starred by the user
    for star in stars:
        isStarred = info.isStarred(conn,star['pid'],usr)
        starred = "0" if isStarred is None else "1"
        star['starred'] = starred
    
    # update each tag with explicit string indicating whether the tag is followed by the user        
    for follow in follows:
        isFollowed = info.isFollowed(conn, follow['tid'], usr)
        followed = "0" if isFollowed is None else "1"
        follow['followed'] = followed

    return render_template('userPortal.html', title = "User Portal", stars=stars,
                        posts=posts, follows=follows, username=usr,logged_in=logged_in)

@app.route('/userPortal/updateProfile/', methods=['GET','POST'])
def updateProfile():
    ''' Collects contact information from users '''
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
        oldNum = oldNum['phoneNum']
        num = "" if oldNum is None else oldNum
        return render_template('updateProfile.html', num=num,logged_in=session.get('logged_in',False))
        
    else:
        # the update function, grab info filled in by the user
        newNum = request.form.get("phoneNum")
        info.updateUserPhone(conn, usr, newNum)
        print("Phone number of ({}) was updated successfully.".format(usr))
        return redirect(url_for('updateProfile'))


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
                          title="Create a Post!",post=None, logged_in=logged_in)
                          
    else:
        #flash warning messages if form is filled out incorrectly

        title = request.form.get('post-title','')
        content = request.form.get('post-content','')
        location = request.form.get('post-location','')
        event_time = request.form.get('post-eventtime','')
        event_date = request.form.get('post-eventdate','')
        tags = request.form.get('post-tags','')
        picture = request.files.get('post-picture',None)

        newpost = {"title":title,"content":content,"location":location,
                "event_time":event_time,"event_date":event_date, "tags":tags,'picture':picture}
    
        error = checkRequiredInfo(title,location,event_date,event_time)

        # test if any errors occured then take user back to insert page, with 
        # the info that they already provided prefilled
        if error:
            return render_template('createPost.html', title="Create a Post!",post=newpost, logged_in=logged_in)
        
        else: 
            # first insert the post without picture, because we need the pid
            pid = info.insertPost(conn, title, content, location, event_time, event_date, tags.split(','), session.get('username'))
            
            # picture is optional
            if picture is None:
                return redirect(url_for('displayPost', pid=pid))
            else:
                # if picture is provided, try uploading
                
                try: #Handing the image uploading
                    fsize = os.fstat(picture.stream.fileno()).st_size
                    if fsize > app.config['MAX_UPLOAD']:
                        raise Exception('File is too big')
                    mime_type = imghdr.what(picture)
                    if mime_type.lower() not in ['jpeg','gif','png']:
                        raise Exception('Not a JPEG, GIF or PNG: {}'.format(mime_type))
                    filename = secure_filename("{}.{}".format(pid,mime_type))
                    pathname = os.path.join(app.config['UPLOADS'],filename)
                    picture.save(pathname)
                    
                    conn = info.getConn('c9')
                    curs = conn.cursor()
                    # upload existing record with the provided picture
                    curs.execute('''UPDATE posts 
                                    SET imagefile = %s
                                    WHERE pid = %s''',
                                 [filename, pid])
                                #test if any errors occured then take user back to insert page
                    conn.commit()
                
                
                    return redirect(url_for('displayPost', pid=pid))
            
                except Exception as err:
                    flash('Redirecting to update page: Picture upload failed {why}'.format(why=err))
                    # redirect to the update page to re-upload the picture 
                    return redirect(url_for('updatePost',pid=pid))

                
# helper function that checks if all required information is provided
def checkRequiredInfo(title, location, event_date, event_time):
    error = False
    
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
        
    return error

# url for post page
@app.route('/posts/<int:pid>')
def displayPost(pid):
    ''' Allow users who are not logged_in to see the posts, with the star function disabled '''
    logged_in = session.get('logged_in', False)

    conn = info.getConn('c9')
    postInfo = info.readOnePost(conn,pid)
    
    if logged_in:
        username = session.get('username')
        starred = info.isStarred(conn,pid,username)
        isAuthor = info.isAuthor(conn,pid,username)
        postInfo["starred"] = "0" if starred is None else "1"
    
        return render_template('post.html',isAuthor=isAuthor,post=postInfo,logged_in=logged_in)
    
    else:
        return render_template('post.html',post=postInfo,logged_in=logged_in)
   
@app.route('/pic/<pid>')
def pic(pid):
    ''' url for looking for picture in the file system with given pid '''
    conn = info.getConn('c9')
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select pid,imagefile from posts where pid = %s''', [pid])
    pic = curs.fetchone()['imagefile']
    if pic is None:
        # flash('No picture for {}'.format(pid))
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
            filename = post['imagefile']
            if filename is not None:
                os.remove(os.path.join(app.config['UPLOADS'], filename))
            info.deletePost(conn,pid)
            flash("Post ({}) was deleted successfully.".format(pid))
            print("Post ({}) was deleted successfully.".format(pid))
            return redirect(url_for('userPortal'))
       
        # the update function, grab info filled in by the user
        else:
            title = request.form.get('post-title')
            content = request.form.get('post-content')
            location = request.form.get('post-location')
            date = request.form.get('post-eventdate')
            time = request.form.get('post-eventtime')
            newtags = request.form.get('post-tags','').split(',')
            picture = request.files.get('post-picture',None)
            
            error = checkRequiredInfo(title,location,date,time)
            
            if error:
                return render_template('updatePost.html', title="Update a Post!",post=post, logged_in=logged_in)

            if picture is None: # no new pic uploaded by user, use the existing pic (if any) by default
                conn = info.getConn('c9')
                curs = conn.cursor(MySQLdb.cursors.DictCursor)
                curs.execute('''select pid,imagefile from posts where pid = %s''', [pid])
                filename = curs.fetchone()['imagefile']

            else: # user uploaded a new pic
                try: #Handing the image uploading
                    fsize = os.fstat(picture.stream.fileno()).st_size

                    if fsize > app.config['MAX_UPLOAD']:
                        raise Exception('File is too big')
                    mime_type = imghdr.what(picture)
                    if mime_type.lower() not in ['jpeg','gif','png']:
                        raise Exception('Not a JPEG, GIF or PNG: {}'.format(mime_type))
                    filename = secure_filename("{}.{}".format(pid,mime_type))
                    print(filename)
                    pathname = os.path.join(app.config['UPLOADS'],filename)
                    picture.save(pathname)
                
                except Exception as err:
                    flash('Upload failed {why}'.format(why=err))
                    # should make the code cleaner later
                    if len(oldtags) == 0:
                        post['tags'] = ''
                    else:
                        post['tags'] = ",".join(oldtags)
                    return render_template('updatePost.html', 
                                      title="Update a Post!",post=post, logged_in=logged_in)

            info.updatePost(conn,pid, title, content, location, filename,time,date,session.get('username'),oldtags,newtags)
        
            print("Post ({}) was updated successfully.".format(pid))
            return redirect(url_for('displayPost', pid=pid))
            
                                  
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
    ''' Allows users who are not logged_in to see the general feed, with star function disabled '''
    logged_in = session.get('logged_in', False)
    keyword = session.pop('keyword','')
    tags = session.pop('tags','')
    conn = info.getConn('c9')
    posts = info.searchPosts(conn,keyword,tags)
    tagHolder = "enter tags separated by comma: e.g. cs, club" if (tags != '') else tags
    
    if logged_in:
        for post in posts:
            isStarred = info.isStarred(conn,post['pid'],session.get('username'))
            print(isStarred)
            post['starred'] = "0" if isStarred is None else "1"
            print(post)
    
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
        # deal with threading races
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
                numFollows = info.followTag(conn,tid,usr)['num_followers']
                print("post {} is followed by user {}".format(tid,usr))
                return jsonify( {'error':False, 'tid': tid, 'followed': "1", 'numFollows': numFollows} )
            else:
                numFollows = info.unfollowTag(conn,tid,usr)['num_followers']
                print("post {} is unfollowed by user {}".format(tid,usr))
                return jsonify( {'error':False, 'tid': tid, 'followed': "0", 'numFollows': numFollows} )
        else:
            print("Need to login")
            return jsonify( {'error': True, 'err': "need to login"} )

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8082)

