from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, email

class RegistrationForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired(), email()])
    username = StringField(validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField(validators=[DataRequired(), Length(min=8)])
    confirmPassword = PasswordField(validators=[DataRequired(), EqualTo('password')])
    role = SelectField(choices=[('Standard User', 'Standard User'),('Administrator', 'Administrator')])
    submit = SubmitField('Confirm New User', id="submitbtn-register")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login', id="submitbtn-login")

    