# project/db_create.py

from views import db
from models import Task
from datetime import date


# create the database and the db table
# we initialize the database schema (i.e., Task) by calling db.create_all()
db.create_all()


# insert data
# We then populate the table with some data, via the Task object from models.py to specify the schema.
# db.session.add(Task("Finish this tutorial", date(2016, 9, 22), 10, 1))
# db.session.add(Task("Finish Real Python", date(2016, 10, 3), 10, 1))


# commit the changes
# To apply the previous changes to our database we need to commit using db.session.commit()
db.session.commit()
