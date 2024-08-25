from flask import Flask , render_template , request , redirect 
import jinja2
from jinja2 import Environment,FileSystemLoader
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import functions #to access the sql functions 
import flask_login
app=Flask(__name__)

env=Environment(loader=jinja2.FileSystemLoader("templates/"))
template=env.get_template("register.html")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database1.db"
db1=SQLAlchemy(app)
class Login_Register(db1.Model):
       student_id=db1.Column(db1.String(100) , primary_key=True) # contains value that is immutable
       username=db1.Column(db1.String(100) , nullable=False)
       email=db1.Column(db1.String(60) ,unique=True, nullable=False)
       password=db1.Column(db1.String(100) ,unique=True, nullable= False)
       phone_number=db1.Column(db1.String(20), nullable=False)

       def __str__(self):
            return f"<User  {self.username}>"
       

with app.app_context():
     db1.create_all()
    


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
          
          input_data=Login_Register(student_id=id_data , username=username_data , email=email_data , password=password_data , phone_number=number_data)
          db1.session.add(input_data)
          db1.session.commit()
          return redirect("/login")
     else:
          return render_template("register.html")


    

@app.route("/login" , methods = ["GET" , "POST"])
def login():
    return render_template("login.html")

@app.route("/logout" , methods=["GET" , "POST"])
def logout():
     return render_template("login.html")

#need to work on jinja


if __name__=="__main__":
    app.run(debug=True)