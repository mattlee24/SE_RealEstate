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
app.config['IMAGE_UPLOADS'] = 'C:/Users/Matt/Desktop/SE_RealEstate/static/uploads/images'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['ALLOWED_IMAGE_EXTENSIONS'] = ["PNG", "JPG", "JPEG", "GIF"]

db = SQLAlchemy(app)
bcrypt = Bcrypt(app) 
login_manager = LoginManager(app)
#images = UploadSet('images', IMAGES)
viewTimes = 0

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

def allowed_image(filename):
  if not "." in filename:
    return False
  ext = filename.rsplit(".",1)[1]
  if ext.upper() in app.config['ALLOWED_IMAGE_EXTENSIONS']:
    return True
  else:
    return False

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  email = db.Column(db.String, nullable=False) 
  username = db.Column(db.String(20), unique=True, nullable=False)
  password = db.Column(db.String(60), nullable=False)
  role = db.Column(db.String, nullable=False)
  post_user = db.relationship('Posts', backref='author', lazy=True)
  avatar = db.Column(db.String(2048), nullable=True, default="https://s3.amazonaws.com/37assets/svn/765-default-avatar.png")
  rating = db.Column(db.Integer, nullable=False, default=1)
  comment_user = db.relationship('Comment', backref='author', lazy=True)

  def __repr__(self):
    return f"User('{self.name}', '{self.email}', '{self.username}', '{self.password}', '{self.role}','{self.avatar}', '{self.rating}')"

class Posts(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(30), nullable=False)
  description = db.Column(db.String(500), nullable=True) 
  date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  rating = db.Column(db.Integer, nullable=False, default=1)
  displayImg = db.Column(db.String(2048), nullable=False, default="https://i1.sndcdn.com/avatars-000617661867-qpt7lq-original.jpg")
  comment_post = db.relationship('Comment', backref='poster', lazy=True)
  img_post = db.relationship('Img', backref='imager', lazy=True)

  def __repr__(self):
    return f"Post('{self.title}', '{self.description}', '{self.date}', '{self.avatar}', '{self.rating}')"

class Img(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  imgPath = db.Column(db.String, nullable=False)
  post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

class Comment(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(50), nullable=False)
  content = db.Column(db.String(500), nullable=False)
  rating = db.Column(db.Integer, nullable=False)
  commentType = db.Column(db.String(4), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

  def __repr__(self):
    return f"Comment('{self.title}', '{self.content}', '{self.rating}')"

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
@app.route("/myposts", methods=['GET','POST'])
def posts():
  my_posts = Posts.query.filter_by(user_id=current_user.id)
  return render_template("myposts.html", posts=my_posts)

#Add Interface
@app.route("/createPost", methods=['GET','POST'])
def createPost():
  form = CreatePostForm()
  if form.validate_on_submit():
    user_id = current_user.id
    post = Posts(title=form.title.data, description=form.description.data, displayImg=form.displayImg.data, user_id=user_id)
    db.session.add(post)
    db.session.commit()
    flash(f'Post created for {current_user.username}, you can view the post under my posts!', 'success')
    return redirect(url_for('main'))
  return render_template('createPost.html', form=form)

#delete post
@app.route('/delete/<id>', methods = ['GET','POST'])
def delete(id):
  targetPost = Posts.query.get(id)
  db.session.delete(targetPost)
  db.session.commit()
  flash("Post Deleted Successfully!","success")
  return redirect(url_for('main'))

#view post
@app.route('/viewPost/<id>', methods=['GET','POST'])
def viewPost(id):
  targetPost = Posts.query.get(id)
  return render_template('viewPost.html', targetPost=targetPost)

#edit post
@app.route('/EditPost/<id>', methods=['GET','POST'])
def viewEditPost(id):
  form = EditPostForm()
  targetPost = Posts.query.get(id)
  if form.validate_on_submit():
    targetPost.title = form.title.data
    targetPost.description = form.description.data
    targetPost.imgPath = form.imgPath.data
    db.session.commit()
    flash(f'Post successfully updated!', 'success')
  return render_template('myposts.html', targetPost=targetPost, form=form)

@app.route('/uploadImg/<id>', methods=['GET','POST'])
def upload(id):
  
  if request.method == "POST":
    if request.files:
      image = request.files["imageFile"]
      filename = image.filename
      
      if image.filename == "":
        print("Image must have a filename!")
        return redirect(request.url)

      if not allowed_image(image.filename):
        print("That image extension is not allowed!")
        return redirect(request.url)

      else:
        filename = secure_filename(image.filename)
        
      pathing="static/uploads/images"+filename
      image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
      
      img = Img(name=filename, imgPath=pathing, post_id=id)
      db.session.add(img)
      db.session.commit()
      flash(f'Image uploaded!', 'success')
      return redirect(url_for('main'))

  return render_template('uploadImg.html')

#Get Post Images
@app.route('/getImages/<id>', methods=['GET','POST'])
def getImages(id):
  conn = sqlite3.connect('Users.db')
  cur = conn.cursor()
  cur.execute("SELECT * FROM Img where post_id == "+ imgId)
  imagedata = cur.fetchall()
  return render_template('test.html', imageData = imagedata)

#main page once logged in
@app.route("/main", methods=['GET','POST'])
def main():
  all_posts = Posts.query.all()
  return render_template("listPosts.html", posts = all_posts)
