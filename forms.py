from datetime import datetime
from flask_wtf import FlaskForm
from flask_uploads import configure_uploads, UploadSet, IMAGES
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FileField, DateField
from wtforms.validators import *
from flask_wtf.file import FileField, FileAllowed, FileRequired

class RegistrationForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired(), email()])
    username = StringField(validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField(validators=[DataRequired(), Length(min=8)])
    confirmPassword = PasswordField(validators=[DataRequired(), EqualTo('password')])
    role = SelectField(choices=[('Standard User', 'Standard User'),('Administrator', 'Administrator')], default="Standard User")
    submit = SubmitField('Confirm New User', id="submitbtn-register")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), email()], id="loginemail")
    password = PasswordField('Password', validators=[DataRequired()], id="loginpass")
    submit = SubmitField('Login', id="submitbtn-login")

class EditForm(FlaskForm):
    id = IntegerField(validators=[DataRequired()], id="IntegerField")
    name = StringField(validators=[DataRequired()], id="editName")
    email = StringField(validators=[DataRequired(), email()], id="editEmail")
    username = StringField(validators=[DataRequired(), Length(min=2, max=20)], id="editUsername")
    password = PasswordField(validators=[DataRequired(), Length(min=8)])
    confirmPassword = PasswordField(validators=[DataRequired(), EqualTo('password')])
    role = SelectField(choices=[('Standard User', 'Standard User'),('Administrator', 'Administrator')], id="editRole")
    submit = SubmitField('Update', id="updatebtn")

class EditPostForm(FlaskForm):
    title = StringField(validators=[DataRequired()], id="editTitle")
    description = StringField(validators=[DataRequired(), Length(max=800)], id="editDescription")
    imgPath = StringField(validators=[Length(min=0, max=2000)])
    submit = SubmitField('Update', id ="updatePostBtn")

class CreatePostForm(FlaskForm):
    title = StringField(validators=[DataRequired()], id="createTitle")
    description = StringField(validators=[DataRequired()], id="createDescription")
    date = DateField(default=datetime.utcnow)
    imgPath = StringField(validators=[Length(min=0, max=2000)], default="https://i1.sndcdn.com/avatars-000617661867-qpt7lq-original.jpg")
    submit = SubmitField('Create', id ="createPostBtn")

class ImgUpload(FlaskForm):
    upload = FileField('image', validators=[FileRequired(), FileAllowed(IMAGES,'Images only!')])