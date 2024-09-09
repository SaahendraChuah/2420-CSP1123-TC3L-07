from flask import Flask , render_template , request , redirect   , url_for , send_from_directory
import jinja2
#from jinja2 import Environment,FileSystemLoader
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename,send_file
import os
from flask_login import UserMixin , LoginManager , login_user , logout_user , current_user , login_required
app=Flask(__name__)
login_manager=LoginManager()
login_manager.init_app(app)
directory= 'C:\\Users\\User\\OneDrive\\Desktop\\2420-CSP1123-TC3L-07\\static\\uploads\\'
if not os.path.exists(directory):
     os.makedirs(directory)
os.chmod(directory,0o777) 


#db2=SQLAlchemy(app)


#env=Environment(loader=jinja2.FileSystemLoader("templates/"))
#template=env.get_template("register.html")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database1.db"
app.config["SECRET_KEY"] = "happy_birthday" 
app.config["UPLOAD_PROFILE"] = os.path.join(os.getcwd(), "static/uploads/")
db1=SQLAlchemy(app)
bcrypt=Bcrypt(app)


class User(UserMixin,db1.Model):
       
       

       student_id=db1.Column(db1.String(100) , primary_key=True) # contains value that is immutable
       username=db1.Column(db1.String(100) , unique=True, nullable=False)
       email=db1.Column(db1.String(60) ,unique=True, nullable=False)
       password=db1.Column(db1.String(100) ,unique=True, nullable= False)
       phone_number=db1.Column(db1.String(20),unique=True, nullable=False)
       profile=db1.relationship('Profile' , backref='user', uselist=False)

       def __str__(self):
            
            return f"<User  {self.username}>"
       def get_id(self):
            return self.student_id
       
class Profile(db1.Model):
      id=db1.Column(db1.Integer, primary_key=True)
      user_name=db1.Column(db1.String(100) , db1.ForeignKey(User.username), nullable=False)
      profile_pic=db1.Column(db1.String(100), nullable=True)
      bio=db1.Column(db1.String(100) , nullable=True)




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
     

     
@app.route("/profile", methods=["GET" , "POST"])
def profile():
     if request.method == "POST":
         profile_pic=request.files["profilephoto"]
         bio=request.form["bio"]

         if profile_pic:
              filename=secure_filename(profile_pic.filename)  #securing the file
              profile_pic.save(os.path.join(app.config["UPLOAD_PROFILE"], filename) )
              existing_profile=Profile.query.filter_by(user_name=current_user.username).first()
              if existing_profile:
                   existing_profile.profile_pic = filename
                   existing_profile.bio = bio
              else:
                   new_profile=Profile(user_name=current_user.username,profile_pic=filename,bio=bio)
                   db1.session.add(new_profile)
                   
              db1.session.commit()
              return redirect(url_for('profile'))      
    
         else:
              existing_profile= Profile.query.filter_by(user_name=current_user.username).first()
              if existing_profile:
                   existing_profile.bio = bio
              else:    
                  new_profile=Profile(user_name=current_user.username,bio=bio)
                  db1.session.add(new_profile)
     
         db1.session.commit()
         return redirect(url_for('profile'))   
     else:
       return render_template("profile.html" , user=current_user)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
     return send_from_directory(app.config["UPLOAD_PROFILE"],filename)

@app.route("/bio" , methods=["POST"])
def bio():
     bio=request.form["bio"]
     if bio:
          pass

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
     return render_template("qrcode.html")


if __name__=="__main__":
    app.run(debug=True)