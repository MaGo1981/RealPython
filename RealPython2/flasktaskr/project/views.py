# project/views.py

#################
#### imports ####
#################

from forms import AddTaskForm, RegisterForm, LoginForm
# our file forms.py
from functools import wraps
from flask import Flask, flash, redirect, render_template, \
request, session, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy.exc import IntegrityError



################
#### config ####
################
app = Flask(__name__)
# pulls in app configuration by looking for UPPERCASE variables
# from_object() method takes an object as a parameter and passes it to config
# Flask looks for variables within the object that are defined using ALL CAPITAL LETTERS
app.config.from_object('_config')
db = SQLAlchemy(app)

from models import Task, User 
# our file models.py

# helper functions
    
def login_required(test):
    '''
    The login_required decorator, meanwhile, checks to make sure that a 
    user is authorized before allowing access to certain pages
    '''
    @wraps(test)    
    def wrap(*args, **kwargs):
        '''
        when the session key, logged_in , is set to True , the user has
        the rights to view the main.html page
        '''
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            # url_for() function generates an endpoint for the provided method.
            return redirect(url_for('login'))
    return wrap

# display the error messages to the end user
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text, error), 'error')
            
def open_tasks():
    return db.session.query(Task).filter_by(
        status='1').order_by(Task.due_date.asc())


def closed_tasks():
    return db.session.query(Task).filter_by(
        status='0').order_by(Task.due_date.asc())
    
# route handlers
@app.route('/logout/')
@login_required
def logout():
    '''
    The pop() function used here is defined within the session class. It is
    not the pop() function native to python that is used on lists.
    '''
    session.pop('logged_in', None)
    session.pop('user_id', None) # pg 162
    session.pop('role', None) # pg 214
    flash('Goodbye!')
    return redirect(url_for('login'))
    
'''
Notice how we had to specify a POST request. By default, routes are set
up automatically to handle GET requests. If you need to add different HTTP
methods, such as a POST, you must add the methods argument to the decorator.

Since we are issuing a POST request, we need to add {{ form.csrf_token }} to
all forms in the templates. This applies the CSRF prevention setting to the 
form that we enabled in the configuration.
'''
@app.route('/', methods=['GET', 'POST'])
def login():
    '''
    In the first function, login() , we mapped the URL / 
    to the function, which in turn sets
    the route to login.html in the templates directory 
    if correct username and password are entered.
    
    When a user submits their user credentials via a POST request, the database
    is queried for the submitted username and password. If the credentials are 
    not found, an error populates; otherwise, the user is logged in and 
    redirected to tasks.html.
    '''
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(name=request.form['name']).first()
            if user is not None and user.password == request.form['password']:
                session['logged_in'] = True
                session['user_id'] = user.id
                session['role'] = user.role # we're simply adding the user's role to the session 
                                            # cookie on the login, then removing it on logout.
                flash('Welcome!')
                return redirect(url_for('tasks'))
            else:
                error = 'Invalid username or password.'
        else:
            error = 'Both fields are required.'
    return render_template('login.html', form=form, error=error)


'''
When a GET request is sent to access tasks.html to view the HTML, it first hits the
@login_required decorator and the entire function, tasks() , is momentarily replaced (or
wrapped) by the login_required() function. Then when the user is logged in, the
tasks() function is invoked, allowing the user to access tasks.html. If the user is not
logged in, they are redirected back to the login screen
'''
@app.route('/tasks/')
@login_required
def tasks():
    # display some information to the user
    # using class AddTaskForm created in forms.py (our file)
    return render_template(
        'tasks.html',
        form=AddTaskForm(request.form),
        open_tasks=open_tasks(),
        closed_tasks=closed_tasks()
    )
    
# Add new tasks
@app.route('/add/', methods=['POST']) 
@login_required
def new_task():
    error = None
    form = AddTaskForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_task = Task(
                form.name.data,
                form.due_date.data,
                form.priority.data,
                datetime.datetime.utcnow(),
                '1',
                session['user_id']
            )
            db.session.add(new_task)
            db.session.commit()
            flash('New entry was successfully posted. Thanks.')
            return redirect(url_for('tasks'))
    return render_template(
        'tasks.html',
        form=form,
        error=error,
        open_tasks=open_tasks(),
        closed_tasks=closed_tasks()
    )
    
    
# Mark tasks as complete
@app.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
    '''
    We're querying the database for the row associated with the task_id , as we did
    before. However, instead of just updating the status to 0 , we're checking to make sure
    that the user_id associated with that specific task is the same as the user_id of the
    user in session.
    Now the if user_id in session matches the user_id that posted the task or if the user's
    role is 'admin', then that user has permission to update or delete the task.
    '''
    new_id = task_id
    task = db.session.query(Task).filter_by(task_id=new_id)
    if session['user_id'] == task.first().user_id or session['role'] == "admin": # pg 214
        task.update({"status": "0"})
        db.session.commit()
        flash('The task is complete. Nice.')
        return redirect(url_for('tasks'))
    else:
        flash('You can only update tasks that belong to you.')
        # url_for() function generates an endpoint for the provided method.
        return redirect(url_for('tasks'))

      
# Delete Tasks
@app.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    new_id = task_id
    task = db.session.query(Task).filter_by(task_id=new_id)
    if session['user_id'] == task.first().user_id or session['role'] == "admin":
        task.delete()
        db.session.commit()
        flash('The task was deleted. Why not add a new one?')
        return redirect(url_for('tasks'))
    else:
        flash('You can only delete tasks that belong to you.')
        return redirect(url_for('tasks'))
        # url_for() function generates an endpoint for the provided method.

    
@app.route('/register/', methods=['GET', 'POST'])
def register():
    '''
    The user information obtained from the register.html template (which we still need
    to create) is stored inside the variable new_user . That data is then added to the
    database, and after successful registration, the user is redirected to login.html with a
    message thanking them for registering. validate_on_submit() returns either True or
    False depending on whether the submitted data passes the form validators associated
    with each field in the form.
    '''
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User(
            form.name.data,
            form.email.data,
            form.password.data,
            )
            '''
            The code within the try block attempts to execute. If it fails due to the
            exception specified in the except block, the code execution stops and the code within
            the except block is ran. If the error does not occur then the program fully executes and
            the except block is skipped altogether.
            '''
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Thanks for registering. Please login.')
                return redirect(url_for('login'))
            except IntegrityError:
                error = 'That username and/or email already exist.'
                return render_template('register.html', form=form, error=error)
    return render_template('register.html', form=form, error=error)
