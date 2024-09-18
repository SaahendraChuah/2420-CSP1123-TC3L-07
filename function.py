from flask import Flask , render_template , request , redirect   , url_for , session , jsonify
import jinja2

from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from flask_login import UserMixin , LoginManager , login_user , logout_user , current_user 
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.middleware.proxy_fix import ProxyFix
from jinja2 import Environment, FileSystemLoader
app=Flask(__name__)
login_manager=LoginManager()
login_manager.init_app(app)


#db2=SQLAlchemy(app)


#env=Environment(loader=jinja2.FileSystemLoader("templates/"))
#template=env.get_template("chat.html")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database1.db"
app.config["SECRET_KEY"] = "happy_birthday" 
db1=SQLAlchemy(app)
bcrypt=Bcrypt(app)


class User(UserMixin,db1.Model):
       
       

       student_id=db1.Column(db1.String(100) , primary_key=True) # contains value that is immutable
       username=db1.Column(db1.String(100) ,unique=True, nullable=False)
       email=db1.Column(db1.String(60) ,unique=True, nullable=False)
       password=db1.Column(db1.String(100) ,unique=True, nullable= False)
       phone_number=db1.Column(db1.String(20), nullable=False)
       Forum = db1.relationship('Forum' , backref="user" )
       Comments = db1.relationship('Comments' , backref="user"  )

       def __str__(self):
            
            return f"<User  {self.username}>"
       def get_id(self):
            return self.student_id
       
class Forum(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    title = db1.Column(db1.String(100), nullable=False)
    content = db1.Column(db1.Text, nullable=False)
    username = db1.Column(db1.String(100), db1.ForeignKey(User.username), nullable=False)
    forum_comments = db1.relationship('Comments', backref=db1.backref('comment_forum', lazy=True))

    def __str__(self):
        return f"<Forum {self.title}>"
     
class Comments(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    content = db1.Column(db1.Text, nullable=False)
    forum_id = db1.Column(db1.Integer, db1.ForeignKey(Forum.id), nullable=False)
    username = db1.Column(db1.String(100), db1.ForeignKey(User.username), nullable=False)

    forum = db1.relationship('Forum', backref=db1.backref('comments', lazy=True))
    comment_user = db1.relationship('User', backref=db1.backref('user_comments', lazy=True))

    def __str__(self):
        return f"<Comment {self.content}>"



@login_manager.user_loader
def user_loading(user_id):
     return User.query.get(user_id)


with app.app_context():
     db1.create_all()
     
     

@app.route("/search" , methods=["GET" , "POST"])
def search():
     if request.method == "POST":
          search_query=request.form.get("search")
          search_results=User.query.filter(User.username.contains(search_query)).all()
          return render_template("view.html" , user=search_results  )
     else:
          return render_template("main.html")
      
@app.route("/view")  
def view():
     return render_template("view.html") 


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
     


posts = []




@app.route("/qrcode")
def qrcode():
     return render_template("qrcode.html")

@app.route("/forum", endpoint="forum")
def index():
    forums = Forum.query.all()
    return render_template("forum.html", posts=forums, forum_url=url_for('forum'))

@app.route("/add_post", methods=["POST"])
def add_post():
    title = request.form["title"]
    content = request.form["content"]
    username = request.form["username"]
    user = User.query.filter_by(username=username).first()
    if user:
        forum = Forum(title=title, content=content, username=username)
        db1.session.add(forum)
        db1.session.commit()
        return redirect(url_for("forum"))
    return "Error: User not found", 404

@app.route("/add_comment/<int:forum_id>", methods=["POST"])
def add_comment(forum_id):
    content = request.form["content"]
    username = request.form["username"]
    user = User.query.filter_by(username=username).first()
    if user:
        forum = Forum.query.get(forum_id)
        if forum:
            comment = Comments(content=content, forum_id=forum_id, username=username, comment_user=user)
            db1.session.add(comment)
            db1.session.commit()
            return redirect(url_for("forum"))
    return "Error: User or Forum not found", 404

if __name__ == "__main__":
    app.run(debug=True)






if __name__=="__main__":

    app.run(debug=True)