from flask_wtf import FlaskForm
from flask_uploads import configure_uploads, UploadSet, IMAGES
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FileField
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
    email = StringField('Email', validators=[DataRequired(), email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login', id="submitbtn-login")

class ImgUpload(FlaskForm):
    upload = FileField('image', validators=[FileRequired(), FileAllowed(IMAGES,'Images only!')])