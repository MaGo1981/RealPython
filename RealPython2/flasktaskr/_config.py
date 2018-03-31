

import os

# grab the folder where this script lives
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = 'flasktaskr.db'
USERNAME = 'admin'
PASSWORD = 'admin'
WTF_CSRF_ENABLED = True  #  WTF_CSRF_ENABLED config setting is used for cross-site request forgery prevention, which makes your app more secure
SECRET_KEY = 'myprecious' #  SECRET_KEY config setting is used in conjunction with the WTF_CSRF_ENABLED
#  setting in order to create a cryptographic token that is used to validate a form. It's
#  also used for the same reason in conjunction with sessions

# define the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# the database uri
# we're defining the SQLALCHEMY_DATABASE_URI to tell SQLAlchemy where to access the database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
