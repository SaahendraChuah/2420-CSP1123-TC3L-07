from flask import Flask
app=Flask(__name__) #creates flask application object


if __name__== "main":
    app.run(debug=True) #shows us actual error when the code is run















































































































































from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.middleware.proxy_fix import ProxyFix
from jinja2 import Environment, FileSystemLoader

app = Flask(__name__)
app.config['SECRET_KEY'] = 'private_chat'
socketio = SocketIO(app)
app.wsgi_app = ProxyFix(app.wsgi_app)  # For handling proxy headers if needed

env=Environment(loader=jinja2.FileSystemLoader("template/"))
template=env.get_template("chat.html")

# Store users and their rooms
users = {}

@app.route('/chat')
def index():
    return render_template('chat.html')

@socketio.on('connect')
def handle_connect():
    user = session.get('username')
    if user:
        users[user] = request.sid  # Store the user's session ID
        emit('user_list', list(users.keys()), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    user = session.get('username')
    if user in users:
        del users[user]
        emit('user_list', list(users.keys()), broadcast=True)

@socketio.on('set_username')
def handle_set_username(username):
    session['username'] = username
    users[username] = request.sid
    emit('user_list', list(users.keys()), broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    recipient = data['recipient']
    message = data['message']
    sender = session.get('username')
    
    if recipient in users:
        recipient_sid = users[recipient]
        emit('received_message', {'sender': sender, 'message': message}, room=recipient_sid)
    else:
        emit('message_error', {'error': 'Recipient not online'}, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)
