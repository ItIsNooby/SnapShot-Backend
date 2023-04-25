from flask import Flask, render_template, jsonify, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import threading
# import "packages" from flask

import sqlite3

from flask_cors import CORS
# import "packages" from "this" project
from __init__ import app, db  # Definitions initialization

# setup App pages
from projects.projects import app_projects # Blueprint directory import projects definition
from model.users import initUsers
from api.user import user_api

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = generate_password_hash(password)
        self.email = email

    def check_password(self, password):
        return check_password_hash(self.password, password)

@app.route('/')  # connects default URL to index() function
def index():
    return render_template("index.html")

@app.route('/stub')  # connects /stub/ URL to stub() function
def stub():
    return render_template("stub.html")

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': 'Username already exists'}), 400

    user = User(username, password, email)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 200

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401

    session['user_id'] = user.id
    session['username'] = user.username

    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)

    return render_template('login.html')

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

if __name__ == '__main__':
    # db.create_all()
    socketio.run(app, debug=True)
