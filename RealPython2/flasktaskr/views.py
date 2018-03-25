
# project/views.py

import sqlite3
from functools import wraps
from flask import Flask, flash, redirect, render_template, \
request, session, url_for, g
from forms import AddTaskForm 
# our file forms.py


# config
app = Flask(__name__)
# pulls in app configuration by looking for UPPERCASE variables
# from_object() method takes an object as a parameter and passes it to config
# Flask looks for variables within the object that are defined using ALL CAPITAL LETTERS
app.config.from_object('_config')

# helper functions
def connect_db():
    return sqlite3.connect(app.config['DATABASE_PATH'])
    
def login_required(test):
    '''The login_required decorator, meanwhile, checks to make sure that a user is authorized
       before allowing access to certain pages'''
    @wraps(test)    
    def wrap(*args, **kwargs):
        '''when the session key, logged_in , is set to True , the user has
           the rights to view the main.html page'''
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            # url_for() function generates an endpoint for the provided method.
            return redirect(url_for('login'))
    return wrap

# route handlers
@app.route('/logout/')
def logout():
    '''The pop() function used here is defined within the session class. It is
       not the pop() function native to python that is used on lists.'''
    session.pop('logged_in', None)
    flash('Goodbye!')
    return redirect(url_for('login'))
    
'''Notice how we had to specify a POST request. By default, routes are set
   up automatically to handle GET requests. If you need to add different HTTP
   methods, such as a POST, you must add the methods argument to the decorator.'''
@app.route('/', methods=['GET', 'POST'])
def login():
    '''In the first function, login() , we mapped the URL / 
       to the function, which in turn sets
       the route to login.html in the templates directory 
       if correct username and password are entered'''
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] \
            or request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', error=error)
        else:
            # Sessions are configured, adding a value of True to the logged_in key, which is
            # removed (via the pop method) when the user logs out (session.pop('logged_in', None))
            session['logged_in'] = True
            flash('Welcome!')
            # url_for() function generates an endpoint for the provided method.
            return redirect(url_for('tasks'))
    return render_template('login.html')


'''When a GET request is sent to access tasks.html to view the HTML, it first hits the
@login_required decorator and the entire function, tasks() , is momentarily replaced (or
wrapped) by the login_required() function. Then when the user is logged in, the
tasks() function is invoked, allowing the user to access tasks.html. If the user is not
logged in, they are redirected back to the login screen'''
@app.route('/tasks/')
@login_required
def tasks():
    '''We queried the database for open and closed tasks and assigned them to 
    two variables, open_tasks and closed tasks . We then passed those variables
    to the tasks.html page. These variables will then be used to populate the 
    open and closed task lists'''
    g.db = connect_db()
    cursor = g.db.execute(
    'select name, due_date, priority, task_id from tasks where status=1'
    )
    open_tasks = [
    dict(name=row[0], due_date=row[1], priority=row[2],
    task_id=row[3]) for row in cursor.fetchall()
    ]
    cursor = g.db.execute(
    'select name, due_date, priority, task_id from tasks where status=0'
    )
    closed_tasks = [
    dict(name=row[0], due_date=row[1], priority=row[2],
    task_id=row[3]) for row in cursor.fetchall()
    ]
    g.db.close()
    # display some information to the user
    # using class AddTaskForm created in forms.py (our file)
    return render_template('tasks.html', form=AddTaskForm(request.form), open_tasks=open_tasks, closed_tasks=closed_tasks)
    
# Add new tasks
@app.route('/add/', methods=['POST']) 
@login_required
def new_task():
    g.db = connect_db()
    name = request.form['name']
    date = request.form['due_date']
    priority = request.form['priority']
    if not name or not date or not priority:
        flash("All fields are required. Please try again.")
        # url_for() function generates an endpoint for the provided method.
        return redirect(url_for('tasks'))
    else:
        g.db.execute('insert into tasks (name, due_date, priority, status) \
            values (?, ?, ?, 1)', [
                request.form['name'],
                request.form['due_date'],
                request.form['priority']
            ]
        )
        g.db.commit()
        g.db.close()
        flash('New entry was successfully posted. Thanks.')
        # url_for() function generates an endpoint for the provided method.
        return redirect(url_for('tasks'))
    
# Mark tasks as complete
@app.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
    ''' we have to convert the task_id variable to a string, since we are using string
    concatenation to combine the SQL query with the task_id , which is an integer.'''
    g.db = connect_db()
    g.db.execute(
        'update tasks set status = 0 where task_id='+str(task_id)
    )
    g.db.commit()
    g.db.close()
    flash('The task was marked as complete.')
    # url_for() function generates an endpoint for the provided method.
    return redirect(url_for('tasks'))
    
# Delete Tasks
@app.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    ''' we have to convert the task_id variable to a string, since we are using string
    concatenation to combine the SQL query with the task_id , which is an integer.'''
    g.db = connect_db()
    g.db.execute('delete from tasks where task_id='+str(task_id))
    g.db.commit()
    g.db.close()
    flash('The task was deleted.')
    # url_for() function generates an endpoint for the provided method.
    return redirect(url_for('tasks'))
