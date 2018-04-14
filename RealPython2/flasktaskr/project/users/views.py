# project/users/views.py


#################
#### imports ####
#################

from functools import wraps
from flask import flash, redirect, render_template, \
    request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError

from .forms import RegisterForm, LoginForm
from project import db
from project.models import User


################
#### config ####
################


'''
We defined the users Blueprint and bound each function with the
@users_blueprint.route decorator so that when we register the Blueprint, 
Flask will recognize each of the functions.
'''

users_blueprint = Blueprint('users', __name__) 
# parametar __name__ se nalazi i u opciji bez blueprint
# app = Flask(__name__)


##########################
#### helper functions ####
##########################

'''
The login_required decorator, meanwhile, checks to make sure that a 
user is authorized before allowing access to certain pages.

When the session key, logged_in , is set to True , the user has
the rights to view the main.html page.
'''


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('users.login'))
    return wrap


################
#### routes ####
################


''''
The pop() function used here is defined within the session class. It is
not the pop() function native to python that is used on lists.
'''

@users_blueprint.route('/logout/')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('role', None)
    flash('Goodbye!')
    return redirect(url_for('users.login'))


'''
Notice how we had to specify a POST request. By default, routes are set
up automatically to handle GET requests. If you need to add different HTTP
methods, such as a POST, you must add the methods argument to the decorator.

Since we are issuing a POST request, we need to add {{ form.csrf_token }} to
all forms in the templates. This applies the CSRF prevention setting to the 
form that we enabled in the configuration.

In the first function, login() , we mapped the URL / 
to the function, which in turn sets
the route to login.html in the templates directory 
if correct username and password are entered.

When a user submits their user credentials via a POST request, the database
is queried for the submitted username and password. If the credentials are 
not found, an error populates; otherwise, the user is logged in and 
redirected to tasks.html.
'''

# razlika od originalnog koda - bez blueprint
# @app.route('/', methods=['GET', 'POST'])
@users_blueprint.route('/', methods=['GET', 'POST'])
def login():
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
                return redirect(url_for('tasks.tasks'))
            else:
                error = 'Invalid username or password.'
    return render_template('login.html', form=form, error=error)


'''
The user information obtained from the register.html template (which we still need
to create) is stored inside the variable new_user . That data is then added to the
database, and after successful registration, the user is redirected to login.html with a
message thanking them for registering. validate_on_submit() returns either True or
False depending on whether the submitted data passes the form validators associated
with each field in the form.

The code within the try block attempts to execute. If it fails due to the
exception specified in the except block, the code execution stops and the code within
the except block is ran. If the error does not occur then the program fully executes and
the except block is skipped altogether.
'''


@users_blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User(
                form.name.data,
                form.email.data,
                form.password.data,
            )
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Thanks for registering. Please login.')
                return redirect(url_for('users.login'))
            except IntegrityError:
                error = 'That username and/or email already exist.'
                return render_template('register.html', form=form, error=error)
    return render_template('register.html', form=form, error=error)
