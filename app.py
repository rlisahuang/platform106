from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
import info
import sys,os

app = Flask(__name__)
app.secret_key = 'draft'

@app.route('/')
def home():
    return render_template('home.html', title="Home")
    
#Builds the create post page
@app.route('/createPost', methods=['GET','POST'])
def createPost():
    conn = info.getConn('c9')
    error = False
    if request.method == 'GET':
        #blank form rendered when page is first visited
        return render_template('createPost.html', 
                          title="Create a Post!")
                          
    else:
        #flash warning messages if form is filled out incorrectly
        if request.form.get('post-title') == "":
            flash('Missing value: Please enter a title for your event!')
            error = True
        if request.form.get('post-location') == "":
            flash('Missing value: Please enter a location for your event!')
            error = True
        if request.form.get('post-eventdate') == "":
            flash('Missing value: Please enter a date for your event!')
            error = True
        if request.form.get('post-eventtime') == "":
            flash('Missing value: Please enter a time for your event!')
            error = True
        
        #test if any errors occured then take user back to insert page
        if error == True:
            return render_template('createPost.html', title="Create a Post!")
            
        title = request.form.get('post-title')
        content = request.form.get('post-content')
        location = request.form.get('post-location')
        event_time = request.form.get('post-eventtime')
        event_date = request.form.get('post-eventdate')
        
        post = info.insertPost(conn, title, content, location, event_time, event_date)
        return render_template('createPost.html', post=post)

# url for post page
@app.route('/posts/<int:pid>')
def displayPost(pid):
    conn = info.getConn('c9')
    postInfo = info.readOnePost(conn,pid)
    
    return render_template('post.html',postInfo=postInfo)

# url for simple search FORM
@app.route('/basicSearch',methods=['POST'])
def searchPosts():
    title = ''
    print(request.method)
    if request.method == 'POST':
        title = request.form.get('searchterm')
        print("hello!!!")
        # return redirect(url_for("searchResults",keyword=title))
    elif request.method == 'GET':
        print("oops")

    return redirect(url_for("searchResults",keyword=title))

# url for advanced search FORM (in a search page)        
@app.route('/advancedSearch',methods=['GET', 'POST'])
def advancedSearch():
    if request.method == 'POST':
        title = request.form.get('searchterm',None)
        tags = request.form.get('tags',None)
        # event time, location... more to follow
    return redirect(url_for("searchResults",keyword=title,tags=tags))

# url that hosts the advanced search form as well as search results    
@app.route('/searchResults/')
def searchResults(keyword,tags=''):
    # if keyword is not None or tags is not None:
    conn = info.getConn('c9')
    posts = info.searchPosts(conn,keyword,tags)
    print(keyword)
    print(posts)

    return render_template('search_results.html',posts=posts)
    # else:
    #     return

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8080)