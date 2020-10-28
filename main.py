from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, jsonify, request, make_response, session
from forms import *
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
from werkzeug.utils import secure_filename
import json, os, random, sqlite3


app = Flask(__name__)
app.config['SECRET_KEY'] = '6ce3cac9d9f1b9fd29ff5cfa9060401f'
app.config['UPLOADED_IMAGES_DEST'] = 'scripts/uploads/images'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['CELERY_BROKER_URL'] = ''
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
  imgPath = db.Column(db.String(2000), nullable=True)

  def __repr__(self):
    return f"Post('{self.title}', '{self.description}', '{self.date}', '{self.imgPath}')"

class Img(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.Text, nullable=False)
  imgType = db.Column(db.Text, nullable = False)
  post_id = db.Column(db.Integer, db.ForeignKey('Posts.id'), nullable=False)

  def __repr__(self):
    return f"Image('{self.imgPath}')"

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
    User.query.filter_by(id=userID).delete()
    db.session.commit()
    resp = make_response("", 204)
    flash('Successfully deleted user from system!','danger')
    return resp

@app.route("/editUser", methods=['GET','POST'])
def editUser():
  form = EditForm()
  if form.validate_on_submit():
    x = User.query.filter_by(id=form.id.data).first()
    x.name = form.name.data
    x.email = form.email.data
    x.username = form.username.data
    x.password = form.password.data
    x.role = form.role.data
    db.session.commit()
    flash(f'Account for {form.username.data} successfully updated!', 'success')
    return redirect(url_for('users'))
  return render_template('editUser.html', form=form)

#Add Interface
@app.route("/posts", methods=['GET','POST'])
def posts():
  all_posts = Posts.query.all()
  return render_template("listPosts.html", posts = all_posts)

#Add Interface
@app.route("/createPost", methods=['GET','POST'])
def createPost():
  form = CreatePostForm()
  if form.validate_on_submit():
    user_id = current_user.id
    post = Posts(title=form.title.data, description=form.description.data, imgPath=form.imgPath.data, user_id=user_id)
    db.session.add(post)
    db.session.commit()
    flash(f'Post created for {current_user.username}, you can view the post under my posts!', 'success')
    return redirect(url_for('posts'))
  return render_template('createPost.html', form=form)

#delete user
@app.route('/delete/<id>', methods = ['GET','POST'])
def delete(id):
  targetPost = Posts.query.get(id)
  db.session.delete(targetPost)
  db.session.commit()
  flash("Post Deleted Successfully!","success")
  return redirect(url_for('posts'))

#view/edit post
@app.route('/viewEditPost/<id>', methods=['GET','POST'])
def viewEditPost(id):
  form = EditPostForm()
  targetPost = Posts.query.get(id)
  if form.validate_on_submit():
    targetPost.title = form.title.data
    targetPost.description = form.description.data
    targetPost.imgPath = form.imgPath.data
    db.session.commit()
    flash(f'Post successfully updated!', 'success')
  return render_template('view&editPost.html', targetPost=targetPost, form=form)

@app.route('/uploadImg', methods=['GET','POST'])
def upload():
  pic = request.files['pic']
  if not pic:
    return 'No pic uploaded', 400
  filename = secure_filename(pic.filename)
  mimetype = pic.imgType
  img = Img(img.pic.read(), mimetype=mimetype, name=filename)
  db.session.add(img)
  db.session.commit()
  flash(f'Image uploaded!', 'success')
  return render_template('uploadImg.html', imgData = pic)

#Get Post Images
@app.route('/getImages/<imgId>', methods=['POST'])
def getImages(imgId):
  conn = sqlite3.connect('Users.db')
  cur = conn.cursor()
  cur.execute("SELECT * FROM Img where post_id == "+ imgId)
  imagedata = cur.fetchall()
  return render_template('test.html', imageData = imagedata)

#main page once logged in
@app.route("/main")
def main():
  return render_template('main.html')
