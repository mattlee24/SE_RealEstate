#Imports all thats needed for the forms.py file (mainly flask modules but datetime in there too!)
from datetime import datetime
from flask_wtf import FlaskForm
from flask_uploads import configure_uploads, UploadSet, IMAGES
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FileField, DateField
from wtforms.validators import *
from flask_wtf.file import FileField, FileAllowed, FileRequired

#Creates Registration form to be used throughout code
class RegistrationForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired(), email()])
    username = StringField(validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField(validators=[DataRequired(), Length(min=8)])
    confirmPassword = PasswordField(validators=[DataRequired(), EqualTo('password')])
    role = SelectField(choices=[('Standard User', 'Standard User'),('Administrator', 'Administrator')], default="Standard User")
    submit = SubmitField('Confirm New User', id="submitbtn-register")

#Creates Login form to be used throughout code
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), email()], id="loginemail")
    password = PasswordField('Password', validators=[DataRequired()], id="loginpass")
    submit = SubmitField('Login', id="submitbtn-login")

#Creates Edit(for administrator to edit passwords) form to be used throughout code
class EditForm(FlaskForm):
    password = PasswordField(validators=[DataRequired(), Length(min=8)])
    confirmPassword = PasswordField(validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update', id="updatebtn")

#Creates Edit Post form to be used throughout code
class EditPostForm(FlaskForm):
    title = StringField(validators=[DataRequired()], id="editTitle")
    description = StringField(validators=[DataRequired(), Length(max=800)], id="editDescription")
    displayImg = StringField(validators=[Length(min=0, max=2000)])
    submit = SubmitField('Update', id ="updatePostBtn")

#Creates Create Post form to be used throughout code
class CreatePostForm(FlaskForm):
    title = StringField(validators=[DataRequired()], id="createTitle")
    description = StringField(validators=[DataRequired()], id="createDescription")
    date = DateField(default=datetime.utcnow)
    displayImg = StringField(validators=[Length(min=0, max=2048)], default="https://i1.sndcdn.com/avatars-000617661867-qpt7lq-original.jpg")
    submit = SubmitField('Create', id ="createPostBtn")