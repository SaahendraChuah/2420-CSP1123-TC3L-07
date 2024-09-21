from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit
from werkzeug.middleware.proxy_fix import ProxyFix
import jinja2

app=Flask(__name__)

app.config['SECRET_KEY'] = 'private_chat'
socketio = SocketIO(app)
app.wsgi_app = ProxyFix(app.wsgi_app)  # For handling proxy headers if needed


# Store users and their rooms
users = {}

@app.route("/chat")
def index():
    return render_template('privatechat.html')

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
    app.run(debug=True)
    socketio.run(app, debug=True)

