# -*- coding: utf-8 -*-
"""
Created on Sun Mar  4 13:29:31 2018

@author: Marko
"""

# blog.py - controller


# imports
from flask import Flask, render_template, request, session, \
    flash, redirect, url_for, g
import sqlite3
from functools import wraps

# configuration
DATABASE = 'blog.db'
USERNAME = 'admin'
PASSWORD = 'admin'
SECRET_KEY = 'hard_to_guess' # encription key

# create the application object
# instance of the Flask class created and assigned to a variable
# the class was implemented  inside module flask (this is using)

app = Flask(__name__)

# pulls in configurations by looking for UPPERCASE variables
app.config.from_object(__name__)


# function used for connecting to the database
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

# This checks to see if logged_in is in the session. If it is, then we call the appropriate
# function (e.g., the function that the decorator is applied to), and if not, the user is
# redirected back to the login screen with a message stating that a log in is required.

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        
        # If the correct username and password are entered, the user is
        # redirected to the main page and the session key, logged_in , 
        # is set to True

        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    status_code = 200
       # Notice how we had to specify a POST request. By default, routes are set
       # up automatically to handle GET requests. If you need to add different HTTP
       # methods, such as a POST, you must add the methods argument to the decorator.'''
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or\
                request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid Credentials. Please try again.'
            status_code = 401
        else:
            session['logged_in'] = True
            return redirect(url_for('main'))
    return render_template('login.html', error=error), status_code


@app.route('/main')
#checks to make sure that a user is authorized 
# before allowing access to certain pages
# Show Posts
@login_required
def main():
    # connects to the database
    g.db = connect_db()
    # then fetches data from the posts table within the database
    cur = g.db.execute('select * from posts')
    # creates an array of dictionaries assigned to the variable posts
    # turning SQL database data into a dictionary
    posts = [dict(title=row[0], post=row[1]) for row in cur.fetchall()]
    g.db.close()
    # passes that variable (containing dict) to the main.html file
    return render_template('main.html', posts=posts)


@app.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form['title']
    post = request.form['post']
    if not title or not post:
        flash("All fields are required. Please try again.")
        return redirect(url_for('main'))
    else:
        g.db = connect_db()
        # the data is added, as a new row, to the database table
        g.db.execute(
            'insert into posts (title, post) values (?, ?)',
            [request.form['title'], request.form['post']]
        )
        g.db.commit()
        g.db.close()
        flash('New entry was successfully posted!')
        return redirect(url_for('main'))

# The logout() function uses the pop() function to reset the session key to the 
# default value when the user logs out. The user is then redirected back to the 
# login screen and a message is flashed indicating that they were logged out.'''
@app.route('/logout')
def logout():
    # The pop() function used here is defined within the session class. 
    # It is not the pop() function native to python that is used on lists.'''
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)