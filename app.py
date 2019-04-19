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
from werkzeug import secure_filename
app = Flask(__name__)

import info
import sys,os
import bcrypt
import MySQLdb

app = Flask(__name__)
app.secret_key = 'draft'

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
    return render_template('tagsList.html', title = "Tags List", logged_in=logged_in)
    
@app.route('/userPortal/')
def userPortal():
    logged_in = session.get('logged_in', False)
    if not logged_in: # the link is only available after the user is logged in
        flash("Please log in!")
        return redirect(url_for("login"))
    return render_template('userPortal.html', title = "User Portal", username=session.get('username'),logged_in=logged_in)
    
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
        tags = request.form.get('post-tags','').split(',')
        
        newpost = {"title":title,"content":content,"location":location,
                "event_time":event_time,"event_date":event_date, "tags":tags}

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
        
        # test if any errors occured then take user back to insert page, with 
        # the info that they already provided prefilled
        if error:
            return render_template('createPost.html', title="Create a Post!",post=newpost, logged_in=logged_in)
        else: 
            pid = info.insertPost(conn, title, content, location, event_time, event_date, tags)
            return redirect(url_for('displayPost', pid=pid))

# url for post page
@app.route('/posts/<int:pid>')
def displayPost(pid):
    logged_in = session.get('logged_in', False)
    if not logged_in: # the link is only available after the user is logged in
        flash("Please log in!")
        return redirect(url_for("login"))
    conn = info.getConn('c9')
    postInfo = info.readOnePost(conn,pid)
    return render_template('post.html',post=postInfo,logged_in=session.get('logged_in',False))

# url for simple search FORM
'''
Potential Issue:
So far, we are allowing users to search posts when they are not logged in. It is
similar to the Wellesley Directory, where users are able to search for information
without logging in, but they are not allowed to see too much detailed information
in the search results. 
'''
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
@app.route('/advancedSearch',methods=['GET', 'POST'])
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
    if not logged_in: # the link is only available after the user is logged in
        flash("Please log in!")
        return redirect(url_for("login"))
    keyword = session.get('keyword','')
    tags = session.get('tags','')
    conn = info.getConn('c9')
    posts = info.searchPosts(conn,keyword,tags)
    tagHolder = "enter tags separated by comma: e.g. cs, club" if (tags != '') else tags

    return render_template('generalFeed.html',title = "General Feed", keyword=keyword,tags=tagHolder,posts=posts,logged_in=session.get('logged_in',False))
    
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
        curs.execute('SELECT username FROM accounts WHERE username = %s',
                     [username])
        row = curs.fetchone()
        if row is not None:
            flash('That username is taken')
            return redirect( url_for('login') )
        curs.execute('INSERT into accounts(username,hashed) VALUES(%s,%s)',
                     [username, hashed])
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

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)
    print(session)
