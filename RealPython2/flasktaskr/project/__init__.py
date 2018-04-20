# __init__ file indicates to the Python interpreter that this directory should be treated as a module

# project/__init__.py

# this config was in the views file before blueprint

import datetime
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
# pulls in app configuration by looking for UPPERCASE variables
# from_object() method takes an object as a parameter and passes it to config
# Flask looks for variables within the object that are defined using ALL CAPITAL LETTERS
app.config.from_pyfile('_config.py')
# pass the Flask app object into class wrapper
bcrypt = Bcrypt(app) 
db = SQLAlchemy(app)


from project.users.views import users_blueprint
from project.tasks.views import tasks_blueprint

# register our blueprints
app.register_blueprint(users_blueprint)
app.register_blueprint(tasks_blueprint)

# error handlers

@app.errorhandler(404)
def page_not_found(error):
    if app.debug is not True:
        now = datetime.datetime.now()
        r = request.url
        with open('error.log', 'a') as f:
            current_timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
            f.write("\n404 error at {}: {} ".format(current_timestamp, r))
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if app.debug is not True:
        now = datetime.datetime.now()
        r = request.url
        with open('error.log', 'a') as f:
            current_timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
            f.write("\n500 error at {}: {} ".format(current_timestamp, r))
    return render_template('500.html'), 500


'''
When an error occurs we add the timestamp and the request to an
error log, error.log. Notice how these errors are only logged when debug mode is off.
Why do you think we would want that? Well, as you know, when the debug mode is on,
errors are caught by the Flask debugger and then handled gracefully by displaying a
nice formatted page with info on how to correct the issue. Since this is caught by the
debugger, it will not throw the right errors. Further, since debug mode will always be off
in production, these errors will be caught by the custom error logger.
'''