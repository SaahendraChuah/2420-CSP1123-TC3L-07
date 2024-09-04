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


class Login_Register(UserMixin,db1.Model):
       
       

       student_id=db1.Column(db1.String(100) , primary_key=True) # contains value that is immutable
       username=db1.Column(db1.String(100) , nullable=False)
       email=db1.Column(db1.String(60) ,unique=True, nullable=False)
       password=db1.Column(db1.String(100) ,unique=True, nullable= False)
       phone_number=db1.Column(db1.String(20), nullable=False)

       def __str__(self):
            
            return f"<User  {self.username}>"
       def get_id(self):
            return self.student_id
       




@login_manager.user_loader
def user_loading(user_id):
     return Login_Register.query.get(user_id)


with app.app_context():
     db1.create_all()
     db1.drop_all()
     

    


@app.route("/")
def test1():
     return "Hello"

@app.route("/check_db")
def check_db():
     users=Login_Register.query.all()
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
           input_data=Login_Register(student_id=id_data , username=username_data , email=email_data , password=secured_password , phone_number=number_data)
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

         
         user_register=Login_Register.query.filter_by(username=username_data).first()
         
         if user_register and bcrypt.check_password_hash(user_register.password,password_data):
              login_user(user_register)
              return redirect("/main")
         else:
              
              return redirect ("/login")
    else:
         
         return render_template("login.html")

@app.route("/main")    
def main():
     return render_template("main.html")




@app.route("/logout" , methods=["GET" , "POST"])
def logout():
       logout_user()
       return redirect(url_for('login'))
     



from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory storage for blog posts
posts = []

@app.route('/chat')
def index():
    return render_template('chat.html', posts=posts)

@app.route('/add', methods=['POST'])
def add_post():
    title = request.form.get('title')
    content = request.form.get('content')
    if title and content:
        posts.append({'title': title, 'content': content})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)