from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, jsonify, request, make_response, session, json
from forms import *
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
from werkzeug.utils import secure_filename
from os import path
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
  password = db.Column(db.String(100), nullable=False)
  role = db.Column(db.String, nullable=False)
  post_user = db.relationship('Posts', backref='author', lazy=True)
  avatar = db.Column(db.String(2048), nullable=True, default="https://s3.amazonaws.com/37assets/svn/765-default-avatar.png")
  bio = db.Column(db.String(500), nullable = False, default="No description has been given for this profile.")
  rating = db.Column(db.Integer, nullable=False, default=1)
  message_from = db.relationship('Messages', backref='author', lazy=True)

  def __repr__(self):
    return f"User('{self.name}', '{self.email}', '{self.username}', '{self.password}', '{self.role}','{self.avatar}', '{self.rating}', '{self.bio}')"

class Posts(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(30), nullable=False)
  description = db.Column(db.String(500), nullable=True) 
  date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  rating = db.Column(db.Integer, nullable=True, default=1)
  displayImg = db.Column(db.String(2048), nullable=True, default="https://i1.sndcdn.com/avatars-000617661867-qpt7lq-original.jpg")
  post_comment = db.relationship('Comment', backref='posterPost', lazy=True)
  img_post = db.relationship('Img', backref='imager', lazy=True)
  timesViewed = db.Column(db.Integer, nullable=True, default=0)

  def __repr__(self):
    return f"Post('{self.title}', '{self.description}', '{self.date}', '{self.rating}')"

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
  date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  posted_by = db.Column(db.Integer, nullable=False)
  post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)

  def __repr__(self):
    return f"Post Comment('{self.title}', '{self.content}', '{self.rating}', '{self.date}', '{self.posted_by}')"

class Messages(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  to_user_id = db.Column(db.Integer, nullable=False)
  description = db.Column(db.String(500), nullable=False)

  def __repr__(self):
    return f"Message('{self.user_id}', '{self.to_user_id}', '{self.description}')"

@app.route("/", methods=['GET','POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    exists = db.session.query(db.session.query(User).filter_by(email=form.email.data).exists()).scalar()
    if exists == True:
      pw_checker = bcrypt.check_password_hash(user.password, form.password.data)
      if pw_checker == True:
        login_user(user)
        global user_password
        user_password = form.password.data
        return redirect(url_for('main'))
      else:
        flash('Login uncessfull, please check email and password!', 'danger')
    else:
        flash('Login uncessfull, please check email and password!', 'danger')
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
    password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    user = User(name=form.name.data, email=form.email.data, username=form.username.data, password=password, role=form.role.data)
    db.session.add(user)
    db.session.commit()
    if user.id != 1:
      defMessage = Messages(user_id=1, to_user_id=user.id, description="Hello " + user.name + " and welcome to our web appliction. This is a default message; if you wish to speak to someone live, please respond to this message in whatever way you deem fit. Thank you! To message another user, please select the chat icon next to their name and begin typing a message.")
      db.session.add(defMessage)
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

@app.route("/deleteUser/<id>", methods=['GET','POST','DELETE'])
def deleteUser(id):
    targetUser = User.query.get(id)
    targetPostMessages = Messages.query.filter_by(user_id=id)
    for message in targetPostMessages:
      db.session.delete(message)
    targetPostMessages2 = Messages.query.filter_by(to_user_id=id)
    for message in targetPostMessages2:
      db.session.delete(message)
    db.session.delete(targetUser)
    db.session.commit()
    
    flash('Successfully deleted user from system!','success')
    return redirect(url_for('users'))

@app.route("/editUser", methods=['GET','POST'])
def editUser():
  form = EditForm()
  if form.validate_on_submit():
    x = User.query.filter_by(id=form.id.data).first()
    x.name = form.name.data
    x.email = form.email.data
    x.username = form.username.data
    x.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    x.role = form.role.data
    db.session.commit()
    flash(f'Account for {form.username.data} successfully updated!', 'success')
    return redirect(url_for('users'))
  return render_template('editUser.html', form=form)

@app.route("/updateProfile/<id>", methods=['GET','POST'])
def updateProfile(id):
  if request.method == "POST":
    x = User.query.filter_by(id=id).first()
    x.name = request.form['name']
    x.username = request.form['username']
    x.email = request.form['email']
    x.password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
    db.session.commit()
    global user_password
    user_password = request.form['password']
    flash(f'Account successfully updated!', 'success')
    return redirect(url_for('profile', id=id))
    
@app.route("/updateBio/<id>", methods=['GET','POST'])
def updateBio(id):
  if request.method == "POST":
    x = User.query.filter_by(id=id).first()
    x.bio = request.form['bio']
    db.session.commit()
    flash(f'Account bio successfully updated!', 'success')
    return redirect(url_for('profile', id=id))

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
  targetPostImgs = Img.query.filter_by(post_id=id)
  for img in targetPostImgs:
    db.session.delete(img)
  db.session.delete(targetPost)
  db.session.commit()
  flash("Post Deleted Successfully!","success")
  return redirect(url_for('main'))

#view post
@app.route('/viewPost/<id>', methods=['GET','POST'])
def viewPost(id):
  targetPost = Posts.query.get(id)
  postImages = Img.query.filter_by(post_id=id)
  targetPost.timesViewed = targetPost.timesViewed + 1
  db.session.commit()
  return render_template('viewPost.html', targetPost=targetPost, postImages=postImages, postID=id)

#edit post
@app.route('/EditPost/<id>', methods=['GET','POST'])
def viewEditPost(id):
  form = EditPostForm()
  targetPost = Posts.query.get(id)
  if form.validate_on_submit():
    targetPost.title = form.title.data
    targetPost.description = form.description.data
    db.session.commit()
    flash(f'Post successfully updated!', 'success')
  return render_template('editPost.html', targetPost=targetPost, form=form, postID=id)

#report post
@app.route('/ReportPost/<id>', methods=['GET','POST'])
def reportPost(id):
  reportedPost = Posts.query.get(id)
  print(reportedPost)
  defMessage = "POST REPORTED! TITLE: "+str(reportedPost.title)+" DESCRIPTION: "+str(reportedPost.description)+" Please take a look at the post and delete or send message to post author to edit."
  message = Messages(user_id=current_user.id, to_user_id=1, description=defMessage)
  db.session.add(message)
  db.session.commit()
  flash(f'Post successfully reported!', 'success')
  return redirect(url_for('main'))

#upload image
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
        
      if os.path.exists('/static/uploads/images/'+filename):
        randomizer = random.randint(1111,9999999)
        image.save(os.path.join(app.config["IMAGE_UPLOADS"], str(randomizer)+filename))
        filename = str(randomizer)+filename
      else:
        randomizer = random.randint(1111,9999999)
        image.save(os.path.join(app.config["IMAGE_UPLOADS"], str(randomizer)+filename))
        filename = str(randomizer)+filename

      pathing="static/uploads/images/"+filename
      img = Img(name=filename, imgPath=pathing, post_id=id)
      db.session.add(img)
      db.session.commit()
      flash(f'Image uploaded!', 'success')
      return redirect(url_for('main'))

  return render_template('uploadImg.html')

#view user
@app.route("/profile/<id>", methods=['GET','POST'])
def profile(id):
  targetUser = User.query.get(id)
  return render_template('profile.html', targetUser=targetUser, user_ID=id, user_password=user_password)

#messaging-view
@app.route("/messaging/<id>", methods=['GET','POST'])
def messaging(id):
  conn = sqlite3.connect('users.db')
  cur = conn.cursor()
  cur.execute("SELECT * FROM Messages WHERE user_id="+str(current_user.id)+" and to_user_id="+str(id)+" or user_id="+str(id)+" and to_user_id="+str(current_user.id))
  data = cur.fetchall()
  userTo = User.query.get(id)
  userFrom = User.query.get(current_user.id)
  userFromAvatar = userFrom.avatar
  userToAvatar = userTo.avatar
  if request.method == "POST":
    messageRecieved = request.form['message']
    message = Messages(user_id=current_user.id, to_user_id=id, description=messageRecieved)
    db.session.add(message)
    db.session.commit()
    return redirect(url_for('messaging', id=id))
  return render_template('chat.html', usertosend=id, data=data, profileID=current_user.id, userFromAvatar=userFromAvatar, userToAvatar=userToAvatar)

#list Post comments
@app.route("/listPostComments/<postId>", methods=['GET','POST'])
def listPostComments(postId):
  poster = Posts.query.get(id)
  conn = sqlite3.connect('users.db')
  cur = conn.cursor()
  cur.execute("SELECT * FROM Comment WHERE post_id="+str(postId))
  allComments = cur.fetchall()
  return render_template("listPostComments.html", comments=allComments, postId=postId)

#create a post comment
@app.route("/createPostComment/<postId>", methods=['GET','POST'])
def createPostComment(postId):
  targetPost = Posts.query.get(postId)
  if request.method=="POST":
    title = request.form['title']
    content = request.form['content']
    posted_by = request.form['postedBy']
    post_id = postId
    user_id = request.form['user']
    rating = 1
    comment = User(title=title, content=content, rating=rating, post_id=post_id, posted_by = posted_by)
    db.session.add(comment)
    db.session.commit()
    flash(f'Comment successfully posted!', 'success')
    return redirect(url_for('createPostComment', postId=post_id))
  return render_template('createPostComment.html', targetPost=targetPost)

#main page once logged in
@app.route("/main", methods=['GET','POST'])
def main():
  all_posts = Posts.query.all()
  print(all_posts)
  return render_template("listPosts.html", posts = all_posts)