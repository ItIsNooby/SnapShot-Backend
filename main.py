import threading
from flask import Flask, request, jsonify, session, render_template
from flask_sqlalchemy import SQLAlchemy
import socketio
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)
socketio = SocketIO(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    # Add other fields as needed

# Route to register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # Check if user already exists
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': 'Username already exists'}), 400

    # Create a new user
    new_user = User(username=username, password=password, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username, password=password).first()
    if user is None:
        return jsonify({'error': 'Invalid username or password'}), 401
    session['user_id'] = user.id
    return jsonify({'message': 'Logged in successfully'}), 200

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@socketio.on('connect')
def handle_connect():
    if 'user_id' not in session:
        return False
    user_id = session['user_id']
    user = User.query.get(user_id)
    if user is None:
        return False
    session['username'] = user.username
    emit('user_joined', {'username': user.username})
    join_room('chat')

@socketio.on('disconnect')
def handle_disconnect():
    if 'username' in session:
        emit('user_left', {'username': session['username']}, room='chat')
        leave_room('chat')
        session.pop('username', None)

@socketio.on('message')
def handle_message(data):
    if 'username' not in session:
        return False
    username = session['username']
    message = data.get('message')
    emit('message', {'username': username, 'message': message}, room='chat')

# this runs the application on the development server
if __name__ == "__main__":
    # db.init_app(app)
    # change name for testing
    from flask_cors import CORS
    cors = CORS(app, support_credentials=True)
    socketio.run(app, debug=True)
    app.run(debug=True, host="0.0.0.0", port="8086") 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)
socketio = SocketIO(app)

if __name__ == '__main__':
    socketio.run(app, debug=True)


