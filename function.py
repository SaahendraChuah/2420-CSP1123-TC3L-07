from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlite3

app=Flask(__name__) #creates flask application object
app.config.from_mapping(SECRET_KEY="sqlite:/database.db")
database1=SQLAlchemy(app)

class Login_Register(database1.Model):
    
    Username=database1.Column(database1.Text, nullable=False) # does not accept any null values
    Student_Email=database1.Column(database1.Text, nullable=False)
    Password=database1.Column(database1.Password, nullable=False)
    Phone_Number=database1.Column(database1.Text, nullable=False)




if __name__== "main":
    app.run(debug=True) #shows us actual error when the code is run