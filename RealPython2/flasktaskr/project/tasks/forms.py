# project/tasks/forms.py


from flask_wtf import Form
from wtforms import StringField, DateField, IntegerField, \
    SelectField
from wtforms.validators import DataRequired


class AddTaskForm(Form):
    task_id = IntegerField()
    name = StringField('Task Name', validators=[DataRequired()])
    due_date = DateField(
        'Date Due (mm/dd/yyyy)',
        validators=[DataRequired()], format='%m/%d/%Y'
    )
    priority = SelectField(
        'Priority',
        validators=[DataRequired()],
        choices=[
            ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
            ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')
        ]
    )
    status = IntegerField('Status')
'''
validators - validate the data submitted by the user.
DataRequired simply means that the field cannot be blank, while the 
format validator restricts the input to the MM/DD/YY date format

NOTE: 
    
The validators and choices are set up correctly in the form; however, we're
not currently using any logic in the new_task() view function to prevent a form
submission if the submitted data does not conform to the specific validators. 

We need to use a method called validate_on_submit() , which returns True if the
data passes validation, in the function. We'll look at this further down the road.
'''
