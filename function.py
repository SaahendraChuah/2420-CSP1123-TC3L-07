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
              next_url=request.args.get('next')
              if next_url:
                  return redirect(next_url)
              else:
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
     

def generate_qrcode(username):
    base_url = "https://b445-2001-e68-7000-1-89e2-7a21-5154-98bc.ngrok-free.app/login_qrcode"
    user_profile_url = f"{base_url}?next=/add_friend/&username={username}"
    return f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={user_profile_url}"






@app.route("/add_friend/", methods=["GET", "POST"])
def add_friend():
    username = request.args.get('username')
    if request.method == "POST":
        # Add friend logic here
        return "Friend added!"
    return render_template("add_friend.html", username=username)

    

@app.route("/login_qrcode", methods=["GET", "POST"])
def login_qrcode():
    if request.method == "POST":
        # Simulate login process
        session['logged_in'] = True
        next_url = request.args.get('next')
        username = request.args.get('username')
        print(f"Next URL in login_qrcode: {next_url}")  # Debugging line
        print(f"Username in login_qrcode: {username}")  # Debugging line
        if next_url:
            return redirect(next_url)
        else:
            return redirect(url_for('add_friend'))
    else:
        return render_template("login_qrcode.html")
      


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        profile_pic = request.files["profilephoto"]
        bio = request.form["bio"]

        if profile_pic:
            filename = secure_filename(profile_pic.filename)  # securing the file
            new_filename = f"{current_user.username}_{filename}"
            profile_pic.save(os.path.join(app.config["UPLOAD_PROFILE"], new_filename))
            existing_profile = Profile.query.filter_by(user_name=current_user.username).first()
            if existing_profile:
                existing_profile.profile_pic = new_filename
                existing_profile.bio = bio
            else:
                qrcode_url = generate_qrcode(current_user.username)
                new_profile = Profile(user_name=current_user.username, profile_pic=new_filename, bio=bio, qrcode=qrcode_url)
                db1.session.add(new_profile)
        else:
            existing_profile = Profile.query.filter_by(user_name=current_user.username).first()
            if existing_profile:
                existing_profile.bio = bio
            else:
                qrcode_url = generate_qrcode(current_user.username)
                new_profile = Profile(user_name=current_user.username, bio=bio, qrcode=qrcode_url)
                db1.session.add(new_profile)

        db1.session.commit()
        return redirect(url_for('profile'))
    else:
        existing_profile = Profile.query.filter_by(user_name=current_user.username).first()
        if existing_profile:
            qrcode_url = existing_profile.qrcode
        else:
            qrcode_url = generate_qrcode(current_user.username)
        
        friends=current_user.friends
        return render_template("profile.html", user=current_user, qrcode_url=qrcode_url , friends=friends)


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


@app.route("/qrcode")
def qrcode():
     pass




 



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
    app.run(host="0.0.0.0",port=5000,debug=True)
    










