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
    if request.method == 'GET':
        #blank form rendered when page is first visited
        return render_template('createPost.html', 
                          title="Create a Post!",post=session.get('newpost',None))
                          
    else:
        #flash warning messages if form is filled out incorrectly
        
        error = False
        title = request.form.get('post-title','')
        content = request.form.get('post-content','')
        location = request.form.get('post-location','')
        event_time = request.form.get('post-eventtime','') #check if this works!:)
        event_date = request.form.get('post-eventdate','')
        tags = request.form.get('post-tags','')
        
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
        
        #test if any errors occured then take user back to insert page
        if error:
            return render_template('createPost.html', title="Create a Post!",post=newpost)
        else: 
            # ADD TAGS
            post = info.insertPost(conn, title, content, location, event_time, event_date)
            print(post)
            pid = post["LAST_INSERT_ID()"]
            session.pop('newpost',None)
            return redirect(url_for('displayPost', pid=pid))

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

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8080)