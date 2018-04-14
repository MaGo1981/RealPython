# __init__ file indicates to the Python interpreter that this directory should be treated as a module

# project/__init__.py

# this config was in the views file before blueprint

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# pulls in app configuration by looking for UPPERCASE variables
# from_object() method takes an object as a parameter and passes it to config
# Flask looks for variables within the object that are defined using ALL CAPITAL LETTERS
app.config.from_pyfile('_config.py')
db = SQLAlchemy(app)

from project.users.views import users_blueprint
from project.tasks.views import tasks_blueprint

# register our blueprints
app.register_blueprint(users_blueprint)
app.register_blueprint(tasks_blueprint)
