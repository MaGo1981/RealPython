# project/views.py

from functools import wraps
from flask import Flask, flash, redirect, render_template, \
request, session, url_for, g
from forms import AddTaskForm 
# our file forms.py
from flask_sqlalchemy import SQLAlchemy



# config
app = Flask(__name__)
# pulls in app configuration by looking for UPPERCASE variables
# from_object() method takes an object as a parameter and passes it to config
# Flask looks for variables within the object that are defined using ALL CAPITAL LETTERS
app.config.from_object('_config')
db = SQLAlchemy(app)

from models import Task

# helper functions
    
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
    open_tasks = db.session.query(Task) \
    .filter_by(status='1').order_by(Task.due_date.asc())
    closed_tasks = db.session.query(Task) \
    .filter_by(status='0').order_by(Task.due_date.asc())
    # display some information to the user
    # using class AddTaskForm created in forms.py (our file)
    return render_template('tasks.html',form=AddTaskForm(request.form), open_tasks=open_tasks, closed_tasks=closed_tasks)

    
# Add new tasks
@app.route('/add/', methods=['POST']) 
@login_required
def new_task():
    form = AddTaskForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_task = Task(
            form.name.data,
            form.due_date.data,
            form.priority.data,
            '1'
            )
            db.session.add(new_task)
            db.session.commit()
            flash('New entry was successfully posted. Thanks.')
    return redirect(url_for('tasks'))
        
    
# Mark tasks as complete
@app.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
    new_id = task_id
    db.session.query(Task).filter_by(task_id=new_id).update({"status": "0"})
    db.session.commit()
    flash('The task is complete. Nice.')
        # url_for() function generates an endpoint for the provided method.
    return redirect(url_for('tasks'))
      
# Delete Tasks
@app.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    new_id = task_id
    db.session.query(Task).filter_by(task_id=new_id).delete()
    db.session.commit()
    flash('The task was deleted. Why not add a new one?')
    # url_for() function generates an endpoint for the provided method.
    return redirect(url_for('tasks'))


