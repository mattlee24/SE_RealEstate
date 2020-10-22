from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, jsonify, request, make_response, session
from forms import *
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
import json, os, random, sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = '6ce3cac9d9f1b9fd29ff5cfa9060401f'
app.config['UPLOADED_IMAGES_DEST'] = 'scripts/uploads/images'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app) 
login_manager = LoginManager(app)
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  email = db.Column(db.String, nullable=False) 
  username = db.Column(db.String(20), unique=True, nullable=False)
  password = db.Column(db.String(60), nullable=False)
  role = db.Column(db.String, nullable=False)
  post_user = db.relationship('Posts', backref='author', lazy=True)
  

  def __repr__(self):
    return f"User('{self.name}', '{self.email}', '{self.username}', '{self.password}', '{self.role}')"

class Posts(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(30), nullable=False)
  description = db.Column(db.String(500), nullable=False) 
  date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  imgPath = db.Column(db.String(500), nullable=True)

  def __repr__(self):
    return f"Post('{self.title}', '{self.description}', '{self.date}', '{self.imgPath}'"

class UserRating(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  user_rating = db.Column(db.Integer, nullable=False)
  user_rating_description = db.Column(db.String(200), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  
  def __repr__(self):
    return f"UserRating('{self.user_rating_id}','{self.user_rating}','{self.user_rating_description}','{self.user_id}')"

class PostsRating(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  post_rating = db.Column(db.Integer, nullable=False)
  post_rating_description = db.Column(db.String(200), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

  def __repr__(self):
    return f"PostsRating('{self.post_rating}', '{self.post_rating_description}', '{self.user_id}')"

@app.route("/", methods=['GET','POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user and user.password == form.password.data:
      login_user(user)
      return redirect(url_for('main'))
    else:
      flash('Login uncessfull, please check username and password!', 'danger')
  return render_template('login.html', form=form)

@app.route("/logout")
def logout():
  flash('Logout Successful', 'success')
  logout_user()
  return redirect(url_for('login'))

@app.route("/register", methods=['GET','POST'])
def register():
  form = RegistrationForm()
  if form.validate_on_submit():
    if current_user.is_authenticated:
      user = User(name=form.name.data, email=form.email.data, username=form.username.data, password=form.password.data, role=form.role.data)
      db.session.add(user)
      db.session.commit()
      flash(f'Account created for {form.username.data}, they can now log in!', 'success')
      return redirect(url_for('login'))
    else:
      user = User(name=form.name.data, email=form.email.data, username=form.username.data, password=form.password.data, role=form.role.data)
      db.session.add(user)
      db.session.commit()
      flash(f'Account created for {form.username.data}, they can now log in!', 'success')
      return redirect(url_for('login'))
  return render_template('register.html', form=form)

@app.route("/users", methods=['GET','POST','DELETE'])
def users():
  conn = sqlite3.connect('users.db')
  cur = conn.cursor()
  cur.execute("SELECT * FROM User")
  data = cur.fetchall()
  return render_template('users.html', data=data)

@app.route("/deleteUser", methods=['GET','POST','DELETE'])
def deleteUser():
    reqobj = json.loads(request.data)
    userID = reqobj['IDofUser']
    x = User.query.filter_by(id=userID).delete()
    db.session.commit()
    resp = make_response("", 204)
    flash('Successfully deleted user from system!','danger')
    return resp

#Add Interface
@app.route("/posts", methods=['GET','POST'])
def posts():
  all_posts = Posts.query.all()
  return render_template("posts.html", posts = all_posts)

#Add Interface
@app.route("/addPost", methods=['POST'])
def addPost():
  if request.method == 'POST':
    title = request.form['title']
    description = request.form['description']
    date = request.date['date']
    img = request.imgPath['imgPath']

    my_post = Posts(title, description, date, img)
    db.session.add(my_post)
    db.session.commit()
    return redirect(url_for('/'))

@app.route("/main")
def main():
  return render_template('main.html')
