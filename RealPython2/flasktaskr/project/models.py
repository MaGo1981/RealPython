# project/models.py

# from project means from __init__.py file in project folder

from project import db

import datetime

class Task(db.Model):
    '''class, Task()  defines the tasks table. The variable names are used
    as the column names. Any field that has a primary_key set to True will auto-increment'''
    
    __tablename__ = "tasks"

    task_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    posted_date = db.Column(db.Date, default=datetime.datetime.utcnow())
    status = db.Column(db.Integer)
    # adds ForeignKey to the database tasks table (id form users table)
    # creating relationship between tables (tasks and users) in order to correlate information
    # One to Many (1:M) - one user can post many tasks
    # ForeignKey() function is placed on the "many" side
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __init__(self, name, due_date, priority, posted_date, status, user_id):
        self.name = name
        self.due_date = due_date
        self.priority = priority
        self.posted_date = posted_date
        self.status = status
        self.user_id = user_id
        
    def __repr__(self):
        return '<name {0}>'.format(self.name)
        
class User(db.Model):
    '''This new class will create a new table in our database to house user data.'''
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    tasks = db.relationship('Task', backref='poster')
    role = db.Column(db.String, default='user')
    
    # creating relationship between tables (tasks and users) in order to correlate information
    # One to Many (1:M) - one user can post many tasks
    # new field associated with the relationship() function is not an actual field in the database
    # it simply references the objects associated with the "many" side
    
    '''
    Go back to your tasks.html. Notice that since we used poster as the 
    backref, we can use it like a regular query object.
    '''
    
    def __init__(self, name=None, email=None, password=None, role=None):
        self.name = name
        self.email = email
        self.password = password
        self.role = role
    def __repr__(self):
        return '<User {0}>'.format(self.name)   
        
    
