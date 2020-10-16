from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, jsonify, request, make_response, session
#from forms import RegistrationForm, LoginForm, EditForm
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
import json, os, random, sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = '6ce3cac9d9f1b9fd29ff5cfa9060401f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app) 
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

class User(db.Model, UserMixin):
  user_id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  email = db.Column(db.String, nullable=False) 
  username = db.Column(db.String(20), unique=True, nullable=False)
  password = db.Column(db.String(60), nullable=False)
  role = db.Column(db.String, nullable=False)
  user_rating = db.Column(db.Integer, db.ForeignKey('UserRating.user_rating_id'), nullable=False)

  def __repr__(self):
    return f"User('{self.name}', '{self.email}', '{self.username}', '{self.password}', '{self.role}', '{self.user_rating}')"

class Posts(db.Model):
  post_id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
  title = db.Column(db.String(30), nullable=False)
  description = db.Column(db.String(500), nullable=False) 
  date = db.Column(db.DateTime, nullable=False)
  post_rating = db.Column(db.Integer, db.ForeignKey('PostsRating.post_rating_id'), nullable=False)
  user_rating_id = db.Column(db.Integer, db.ForeignKey('UserRating.user_rating_id'), nullable=False)

  def __repr__(self):
    return f"Post('{self.title}', '{self.description}', '{self.date}', '{self.post_rating}')"

class UserRating(db.Model):
  user_rating_id = db.Column(db.Integer, primary_key=True)
  user_rating = db.Column(db.Integer, nullable=False)
  user_rating_description = db.Column(db.String(200), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)

  def __repr__(self):
    return f"UserRating('{self.user_rating}', '{self.user_rating_description}', '{self.user_id}')"

class PostsRating(db.Model):
  post_rating_id = db.Column(db.Integer, primary_key=True)
  post_rating = db.Column(db.Integer, nullable=False)
  post_rating_description = db.Column(db.String(200), nullable=False)
  post_id = db.Column(db.Integer,  db.ForeignKey('Posts.post_id'), nullable=False)

  def __repr__(self):
    return f"PostsRating('{self.post_rating}', '{self.post_rating_description}', '{self.post_id}')"



@app.route("/")
def login():
  return render_template('login.html')

@app.route("/register")
def register():
  return render_template('register.html')

@app.route("/main")
def main():
  return render_template('main.html')
