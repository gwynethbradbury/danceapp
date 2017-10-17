from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

# 'BooleanField', 'DecimalField', 'DateField', 'DateTimeField', 'FieldList',
# 'FloatField', 'FormField', 'IntegerField', 'RadioField', 'SelectField',
# 'SelectMultipleField', 'StringField',

# 'BooleanField', 'TextAreaField', 'PasswordField', 'FileField',
#     'HiddenField', 'SubmitField', 'TextField'

class UsernamePasswordForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
class EmailPasswordForm(Form):
    username = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeatpassword = PasswordField('Repeat Password', validators=[DataRequired()])

class EmailForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])

class PasswordForm(Form):
    password = PasswordField('Password', validators=[DataRequired()])