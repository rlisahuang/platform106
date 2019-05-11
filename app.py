from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory,jsonify)
from werkzeug import secure_filename
app = Flask(__name__)

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
    return render_template('home.html', title="Home")
    
@app.route('/login/')
def login():
    return render_template('login.html', title = "Login")
    
@app.route('/tagsList')
def tagsList():
    return render_template('tagsList.html', title = "Tags List")
    
@app.route('/userPortal/')
def userPortal():
    return render_template('userPortal.html', title = "User Portal")
    
@app.route('/generalFeed/')
def generalFeed():
    return render_template('generalFeed.html', title = "General Feed")
    
#Builds the create post page
@app.route('/createPost', methods=['GET','POST'])
def createPost():
    conn = info.getConn('c9')
    error = False
    if request.method == 'GET':
        #blank form rendered when page is first visited
        return render_template('createPost.html', 
                          title="Create a Post!",post=session.get('newpost',None))
                          
    else:
        #flash warning messages if form is filled out incorrectly
        
        title = request.form.get('post-title','')
        content = request.form.get('post-content','')
        location = request.form.get('post-location','')
        event_time = request.form.get('post-eventtime','') #check if this works!:)
        event_date = request.form.get('post-eventdate','')
        picture = request.form.get('picture','')
        
        newpost = {"title":title,"content":content,"location":location,"event_time":event_time,
            "event_date":event_date, "picture":picture}
        session['newpost'] = newpost
        
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
        if picture == "":
            flash('Missing value: Please enter a picture for your event!')
            error = True
            
        try: #Handing the image uploading
            fsize = os.fstat(picture.stream.fileno()).st_size
            print 'file size is ',fsize
            if fsize > app.config['MAX_UPLOAD']:
                raise Exception('File is too big')
            mime_type = imghdr.what(picture)
            if mime_type.lower() not in ['jpeg','gif','png']:
                raise Exception('Not a JPEG, GIF or PNG: {}'.format(mime_type))
            # filename = secure_filename('{}.{}'.format(nm,mime_type))
            # pathname = os.path.join(app.config['UPLOADS'],filename)
            # f.save(pathname)
            flash('Upload successful')
            # conn = getConn('wmdb')
            # curs = conn.cursor()
            # curs.execute('''insert into picfile(nm,filename) values (%s,%s)
            #                 on duplicate key update filename = %s''',
            #              [nm, filename, filename])
                        #test if any errors occured then take user back to insert page
            if error == True:
                return render_template('createPost.html', title="Create a Post!",post=session.get('newpost'))
            
            post = info.insertPost(conn, title, content, location, event_time, event_date, picture)
            print(post)
            pid = post["LAST_INSERT_ID()"]
            session.pop('newpost',None)
            return redirect(url_for('displayPost', pid=pid))

        except Exception as err:
            flash('Upload failed {why}'.format(why=err))
            #blank form rendered when page is first visited
            return render_template('createPost.html', 
                              title="Create a Post!",post=session.get('newpost',None))
                
        


# url for post page
@app.route('/posts/<int:pid>')
def displayPost(pid):
    conn = info.getConn('c9')
    postInfo = info.readOnePost(conn,pid)
    
    return render_template('post.html',post=postInfo)

# url for simple search FORM
@app.route('/basicSearch',methods=['POST'])
def basicSearch():
    title = ''
    if request.method == 'POST':
        title = request.form.get('searchterm')
        session['keyword'] = title
        session['tags'] = ''

        return redirect(url_for("searchResults"))
        
    return redirect(request.referrer)

# url for advanced search FORM (in a search page)        
@app.route('/advancedSearch',methods=['GET', 'POST'])
def advancedSearch():
    if request.method == 'POST':
        title = request.form.get('searchterm','')
        tags = request.form.get('searchtags','')
        session['keyword'] = title
        session['tags'] = tags
        # event time, location... more to follow
        return redirect(url_for("searchResults"))
    return redirect(request.referrer)

# url that hosts the advanced search form as well as search results    
@app.route('/searchResults/')
def searchResults():
    # if keyword is not None or tags is not None:
    
    keyword = session.get('keyword','')
    tags = session.get('tags','')
    conn = info.getConn('c9')
    posts = info.searchPosts(conn,keyword,tags)
    print(keyword)
    
    tagHolder = "enter tags separated by comma: e.g. cs, club" if (tags != '') else tags

    return render_template('search_results.html',keyword=keyword,tags=tagHolder ,posts=posts)
    
#--- Login User Below



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
        session['visits'] = 1
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
            # Same response as wrong password, so no information about what went wrong
            flash('login incorrect. Try again or join')
            return redirect( url_for('index'))
        hashed = row['hashed']
        # strings always come out of the database as unicode objects
        if bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8')) == hashed:
            flash('successfully logged in as '+username)
            session['username'] = username
            session['logged_in'] = True
            session['visits'] = 1
            return redirect( url_for('userPortal') )
        else:
            flash('login incorrect. Try again or join')
            return redirect( url_for('login'))
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('login') )


# @app.route('/user/<username>')
# def user(username):
#     try:
#         # don't trust the URL; it's only there for decoration
#         if 'username' in session:
#             username = session['username']
#             session['visits'] = 1+int(session['visits'])
#             return render_template('greet.html',
#                                   page_title='My App: Welcome '+username,
#                                   name=username,
#                                   visits=session['visits'])
#         else:
#             flash('you are not logged in. Please login or join')
#             return redirect( url_for('index') )
#     except Exception as err:
#         flash('some kind of error '+str(err))
#         return redirect( url_for('index') )

# @app.route('/logout/')
# def logout():
#     try:
#         if 'username' in session:
#             username = session['username']
#             session.pop('username')
#             session.pop('logged_in')
#             flash('You are logged out')
#             return redirect(url_for('index'))
#         else:
#             flash('you are not logged in. Please login or join')
#             return redirect( url_for('index') )
#     except Exception as err:
#         flash('some kind of error '+str(err))
#         return redirect( url_for('index') )

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8082)