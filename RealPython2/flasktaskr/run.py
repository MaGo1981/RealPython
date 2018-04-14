# project/run.py


'''
To start, this application has the following features:
    
1. Users can sign in and out from the landing page

2. New users can register on a separate registration page

3. Once signed in, users can add new tasks (each task consists of a name, 
   due date, priority, status, and a unique ID)

4. Users can view all incomplete tasks from the same page

5. Users can also delete tasks and mark tasks as complete 
(deleted tasks will be removed from the database)
'''

# from project means from __init__.py file in project folder
from project import app
app.run(debug=True)
