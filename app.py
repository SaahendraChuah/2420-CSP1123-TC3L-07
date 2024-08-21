from flask import Flask
app=Flask(__name__) #creates flask application object




if __name__=="__main__":
         
     app.run(debug=True) #shows us actual error when the code is run

