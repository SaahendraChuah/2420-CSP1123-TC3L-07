from flask import Flask , render_template , request , redirect , url_for , flash , session
import jinja2
#from jinja2 import Environment,FileSystemLoader
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from flask_login import UserMixin , LoginManager , login_user , logout_user , current_user,login_required
import qrcode
import base64
from io import BytesIO
from datetime import datetime
app=Flask(__name__)
login_manager=LoginManager()
login_manager.init_app(app)


#db2=SQLAlchemy(app)


#env=Environment(loader=jinja2.FileSystemLoader("templates/"))
#template=env.get_template("register.html")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database1.db"
app.config["SECRET_KEY"] = "happy_birthday" 
db1=SQLAlchemy(app)
bcrypt=Bcrypt(app)


class User(UserMixin,db1.Model):
       
       

       student_id=db1.Column(db1.String(100) , primary_key=True) # contains value that is immutable
       username=db1.Column(db1.String(100) , unique=True , nullable=False)
       email=db1.Column(db1.String(60) ,unique=True, nullable=False)
       password=db1.Column(db1.String(100) ,unique=True, nullable= False)
       phone_number=db1.Column(db1.String(20), nullable=False)


       def _str_(self):
            
            return f"<User  {self.username}>"
       def get_id(self):
            return self.student_id
       


class Message(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    sender_username = db1.Column(db1.String(100), db1.ForeignKey('user.username'), nullable=False)
    receiver_username = db1.Column(db1.String(100), db1.ForeignKey('user.username'), nullable=False)
    content = db1.Column(db1.Text, nullable=False)
    timestamp = db1.Column(db1.DateTime, default=db1.func.now())

    sender = db1.relationship('User' , foreign_keys=[sender_username], backref='sent_messages')
    receiver = db1.relationship('User', foreign_keys=[receiver_username], backref='received_messages')




class Profile(User,db1.Model):
     id = db1.Column(db1.Integer, primary_key=True)
     user_name = db1.Column(db1.String(100), db1.ForeignKey('user.username') , nullable=False)
     profile_pic = db1.Column(db1.String(100), nullable=False)
     bio = db1.Column(db1.String(100), nullable=True)


     def _str_ (self):
          return f"<Profile {self.user_name}>"







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
     



@app.route("/profilephoto")
def profilephoto():
     pass


#@app.route("/qrcode")
#def qrcode():
     #return render_template("qrcode.html")

@app.route("/qrcode")
def profile():
     user_name =current_user.username
     qr = qrcode.QRCode(version=1 , box_size=10, border=4)
     qr.add_data(user_name)
     qr.make(fit=True)
     img = qr.make_image(fill='black', back_color='blue')
     buf = BytesIO()
     img.save(buf , format='PNG')
     buf.seek(0)
     qr_code_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
     return render_template('profile.html' , qr_code_base64=qr_code_base64 , user=current_user)

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



if __name__=="__main__":
    app.run(debug=True)



     
















     















