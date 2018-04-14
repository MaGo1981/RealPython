# project/tasks/views.py


import datetime
from functools import wraps
from flask import flash, redirect, render_template, \
    request, session, url_for, Blueprint

from .forms import AddTaskForm
from project import db
from project.models import Task


################
#### config ####
################


'''
We defined the tasks Blueprint and bound each function with the
@tasks_blueprint.route decorator so that when we register the Blueprint, 
Flask will recognize each of the functions.
'''

tasks_blueprint = Blueprint('tasks', __name__)


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


def open_tasks():
    return db.session.query(Task).filter_by(
        status='1').order_by(Task.due_date.asc())


def closed_tasks():
    return db.session.query(Task).filter_by(
        status='0').order_by(Task.due_date.asc())


################
#### routes ####
################


'''
When a GET request is sent to access tasks.html to view the HTML, it first hits the
@login_required decorator and the entire function, tasks() , is momentarily replaced (or
wrapped) by the login_required() function. Then when the user is logged in, the
tasks() function is invoked, allowing the user to access tasks.html. If the user is not
logged in, they are redirected back to the login screen
'''

@tasks_blueprint.route('/tasks/')
@login_required
def tasks():
    return render_template(
        'tasks.html',
        form=AddTaskForm(request.form),
        open_tasks=open_tasks(),
        closed_tasks=closed_tasks()
    )


@tasks_blueprint.route('/add/', methods=['GET', 'POST'])
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
            return redirect(url_for('tasks.tasks'))
    return render_template(
        'tasks.html',
        form=form,
        error=error,
        open_tasks=open_tasks(),
        closed_tasks=closed_tasks()
    )



'''
We're querying the database for the row associated with the task_id , as we did
before. However, instead of just updating the status to 0 , we're checking to make sure
that the user_id associated with that specific task is the same as the user_id of the
user in session.
Now the if user_id in session matches the user_id that posted the task or if the user's
role is 'admin', then that user has permission to update or delete the task.
'''

@tasks_blueprint.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
    new_id = task_id
    task = db.session.query(Task).filter_by(task_id=new_id)
    if session['user_id'] == task.first().user_id or session['role'] == "admin":
        task.update({"status": "0"})
        db.session.commit()
        flash('The task is complete. Nice.')
        return redirect(url_for('tasks.tasks'))
    else:
        flash('You can only update tasks that belong to you.')
        return redirect(url_for('tasks.tasks'))


@tasks_blueprint.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    new_id = task_id
    task = db.session.query(Task).filter_by(task_id=new_id)
    if session['user_id'] == task.first().user_id or session['role'] == "admin":
        task.delete()
        db.session.commit()
        flash('The task was deleted. Why not add a new one?')
        return redirect(url_for('tasks.tasks'))
    else:
        flash('You can only delete tasks that belong to you.')
        return redirect(url_for('tasks.tasks'))
