from flask import Flask , render_template , request , redirect   , url_for , send_from_directory , flash , session
import jinja2
#from jinja2 import Environment,FileSystemLoader
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename,send_file
import os
import urllib.parse
from urllib.parse import quote
import qrcode
import base64
from io import BytesIO
from flask_login import UserMixin , LoginManager , login_user , logout_user , current_user , login_required
from datetime import datetime
import uuid
app=Flask(__name__)
login_manager=LoginManager()
login_manager.init_app(app)
directory= 'C:\\Users\\User\\OneDrive\\Desktop\\2420-CSP1123-TC3L-07\\static\\uploads\\'
#if not os.path.exists(directory):
     #os.makedirs(directory)
#os.chmod(directory,0o777) 



app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database1.db"
app.config["SECRET_KEY"] = "happy_birthday" 
app.config["UPLOAD_PROFILE"] = os.path.join(os.getcwd(), "static/uploads/")
db1=SQLAlchemy(app)
bcrypt=Bcrypt(app)


class Friendship(db1.Model):
    id=db1.Column(db1.Integer, primary_key=True)
    user_username=db1.Column(db1.String(100),db1.ForeignKey('user.username'))
    friend_username=db1.Column(db1.String(100),db1.ForeignKey('user.username'))

    user_friend=db1.relationship('User' , foreign_keys=[user_username] , backref='initiated_friendships')
    friend=db1.relationship('User' , foreign_keys=[friend_username] , backref='received_friendships')

class User(UserMixin, db1.Model):
    student_id = db1.Column(db1.String(100), primary_key=True)  # contains value that is immutable
    username = db1.Column(db1.String(100), unique=True, nullable=False)
    email = db1.Column(db1.String(60), unique=True, nullable=False)
    password = db1.Column(db1.String(100), nullable=False)  
    phone_number = db1.Column(db1.String(20), unique=True, nullable=False)
    uuid=db1.Column(db1.String(36), unique=True, default=lambda:str(uuid.uuid4()), nullable=False)
    profile = db1.relationship('Profile', backref='user', uselist=False)
    Forum = db1.relationship('Forum', backref='user')
    Comments = db1.relationship('Comments', backref='user')
    #friendships=db1.relationship('Friendship' , foreign_keys=[Friendship.user_username],backref='user', lazy='dynamic')



    def __str__(self):
        return f"<User {self.username}>"

    def get_id(self):
        return self.student_id
    
    @property
    def friends(self):
        initiated_friends=[friendship.friend for friendship in self.initiated_friendships]
        received_friends=[friendship.user_friend for friendship in self.received_friendships]
        return set(initiated_friends + received_friends)
    
    
class Message(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    sender_username = db1.Column(db1.String(100), db1.ForeignKey('user.username'), nullable=False)
    receiver_username = db1.Column(db1.String(100), db1.ForeignKey('user.username'), nullable=False)
    content = db1.Column(db1.Text, nullable=False)
    timestamp = db1.Column(db1.DateTime, default=db1.func.now())

    sender = db1.relationship('User' , foreign_keys=[sender_username], backref='sent_messages')
    receiver = db1.relationship('User', foreign_keys=[receiver_username], backref='received_messages')

class Profile(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    user_name = db1.Column(db1.String(100), db1.ForeignKey('user.username'), nullable=False)
    profile_pic = db1.Column(db1.String(100), nullable=True)
    bio = db1.Column(db1.String(100), nullable=True)
    qrcode= db1.Column(db1.String(100) , nullable=False)

    def __str__(self):
        return f"<Profile {self.user_name}>"
    


class Forum(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    title = db1.Column(db1.String(100), nullable=False)
    content = db1.Column(db1.Text, nullable=False)
    username = db1.Column(db1.String(100), db1.ForeignKey('user.username'), nullable=False)
    forum_comments = db1.relationship('Comments', backref=db1.backref('comment_forum', lazy=True))

    def __str__(self):
        return f"<Forum {self.title}>"

class Comments(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    content = db1.Column(db1.Text, nullable=False)
    forum_id = db1.Column(db1.Integer, db1.ForeignKey('forum.id'), nullable=False)
    username = db1.Column(db1.String(100), db1.ForeignKey('user.username'), nullable=False)

    forum = db1.relationship('Forum', backref=db1.backref('comments', lazy=True))
    comment_user = db1.relationship('User', backref=db1.backref('user_comments', lazy=True))

    def __str__(self):
        return f"<Comment {self.content}>"



@login_manager.user_loader
def user_loading(user_id):
     return User.query.get(user_id)


with app.app_context():
     db1.create_all()
     
      

@app.route("/search")
def search():

          search_query=request.args.get('search')
          user=User.query.filter_by(username=search_query).first()
          if user:
               return redirect(url_for("view" , username=user.username))
          else:
               flash("User not found")
               return redirect(url_for("main"))
               
     
      
@app.route("/user/<username>")
@login_required
def view(username):
     user=User.query.filter_by(username=username).first_or_404()
     return render_template("view.html", user=user)

@app.route("/unauthorized")
def unauthorized():
     return "You are unauthorized to view this page" , 403

@app.route("/")
def test1():
     return "Hello"

@app.route("/check_db")
def check_db():
     users=User.query.all()
     return f"Users : {users}"


@app.route("/register" , methods=["GET" ,"POST"])
def register():
     if request.method=="POST":
          username_data=request.form["username"]
          id_data=request.form["id"]
          email_data=request.form["email"]
          password_data=request.form["password"]
          number_data=request.form["number"]
          secured_password=bcrypt.generate_password_hash(password_data).decode("utf-8")

          try:
           input_data=User(student_id=id_data , username=username_data , email=email_data , password=secured_password , phone_number=number_data)
           db1.session.add(input_data)
           db1.session.commit()

           return redirect("/login")
          
          except IntegrityError:
               db1.session.rollback()
               return ("You already have an existing account.")
               
               
     else:
          return render_template("register.html")


    

@app.route("/login" , methods = ["GET" , "POST"])
def login():
    if request.method == "POST":
         student_id_data = request.form["id"]
         username_data= request.form["username"]
         password_data= request.form["password"]

         
         user_register=User.query.filter_by(username=username_data).first()
         
         if user_register and bcrypt.check_password_hash(user_register.password,password_data):
              login_user(user_register)
              return redirect("/main")

         else:
              
              return redirect ("/login")
    else:
         
         return render_template("login.html")

@app.route("/main")    
def main():
     
     return render_template("main.html", user=current_user)




@app.route("/logout" , methods=["GET" , "POST"])
def logout():
       logout_user()
       return redirect(url_for('login'))
     


def generate_qr_code(user_uuid):
    unique_url=f"http://127.0.0.1:5000/add_friend.html?uuid={user_uuid}"
    qr=qrcode.make(unique_url)
    qr_filename=f"{user_uuid}_qrcode.png"
    qr_path=os.path.join(app.config["UPLOAD_PROFILE"],qr_filename)
    qr.save(qr_path)
    return qr_filename





@app.route("/add_friend.html", methods=["GET", "POST"])
def add_friend():
    
    if request.method == "POST":
        # Handle friend request logic here
        friend_username = request.form.get("friend_username")
        # Add the logic to add this user as a friend

    # Retrieve the user from the UUID passed in the URL
    uuid = request.args.get('uuid')
    qr_code_owner = User.query.filter_by(uuid=uuid).first_or_404()

    

    return render_template("add_friend.html", qr_code_owner=qr_code_owner)

    
   


@app.route("/profile", methods=["GET", "POST"])
@login_required


def profile():
    existing_profile = Profile.query.filter_by(user_name=current_user.username).first()

    
    if not existing_profile or not existing_profile.qrcode:  # ensures the qrcode exists for the user or not.If no qrcode,new qrcode will be generated
        qrcode_filename = generate_qr_code(current_user.uuid)
        if existing_profile:
            existing_profile.qrcode = qrcode_filename
        else:
            existing_profile = Profile(user_name=current_user.username, qrcode=qrcode_filename)
            db1.session.add(existing_profile)
        db1.session.commit()

    if request.method == "POST":
        profile_pic = request.files.get("profilephoto")
        bio = request.form.get("bio")

        if profile_pic:
            filename = secure_filename(profile_pic.filename)
            new_filename = f"{current_user.username}_{filename}"
            profile_pic.save(os.path.join(app.config["UPLOAD_PROFILE"], new_filename))

            if existing_profile:
                existing_profile.profile_pic = new_filename
                existing_profile.bio = bio
            else:
                existing_profile = Profile(user_name=current_user.username, profile_pic=new_filename, bio=bio)
                db1.session.add(existing_profile)
        else:
            if existing_profile:
                existing_profile.bio = bio
            else:
                existing_profile = Profile(user_name=current_user.username, bio=bio)
                db1.session.add(existing_profile)

        db1.session.commit()
        return redirect(url_for('profile'))

    return render_template("profile.html", user=current_user, profile=existing_profile)
    


@app.route("/uploads/<filename>")
def uploaded_file(filename):
     return send_from_directory(app.config["UPLOAD_PROFILE"],filename)



@app.route("/removepic" , methods=["POST"])
def  removepic():
       existing_profile=Profile.query.filter_by(user_name=current_user.username).first()
       if existing_profile:
            existing_profile.profile_pic=""
            db1.session.commit()
       else:
            print("Error occured")
       return redirect(url_for('profile'))







 



@app.route('/forum')
def forum():
    posts = Forum.query.all()
    return render_template('forum.html', posts=posts)

@app.route('/add_post', methods=['POST'])
@login_required
def add_post():
    title = request.form['title']
    content = request.form['content']
    new_post = Forum(title=title, content=content, username=current_user.username)
    db1.session.add(new_post)
    db1.session.commit()
    return redirect(url_for('forum'))

@app.route('/add_comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.form['comment']
    new_comment = Comments(content=content, forum_id=post_id, username=current_user.username)
    db1.session.add(new_comment)
    db1.session.commit()
    return redirect(url_for('forum'))


@app.route('/chat')
@login_required
def chat():
    users = User.query.all()
    selected_user = session.get('selected_user')
    if selected_user:
        messages = Message.query.filter(
            ((Message.sender_username == current_user.username) & (Message.receiver_username == selected_user)) |
            ((Message.sender_username == selected_user) & (Message.receiver_username == current_user.username))
        ).all()
    else:
        messages = []
    return render_template('chat.html', users=users, messages=messages, current_user=current_user, selected_user=selected_user)


@app.route('/select_user', methods=['POST'])
@login_required
def select_user():
    selected_user = request.form.get('selected_user')
    session['selected_user'] = selected_user
    return redirect(url_for('chat'))

@app.route('/send', methods=['POST'])
@login_required
def send():
    receiver_username = session.get('selected_user')
    message_text = request.form.get('message')
    if receiver_username and message_text:
        new_message = Message(sender_username=current_user.username, receiver_username=receiver_username, content=message_text)
        db1.session.add(new_message)
        db1.session.commit()
    return redirect(url_for('chat'))


if __name__ == '__main__':
    app.run(debug=True)
    










