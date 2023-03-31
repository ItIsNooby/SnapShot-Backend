from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Create a SQLite database in the instance folder
app.config['DATABASE'] = 'sqlite:///instance/sqlite.db'

def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

# Create a table for users in the database
def create_users_table():
    db = get_db()
    db.execute('CREATE TABLE IF NOT EXISTS logins (username TEXT, email TEXT, password TEXT)')
    db.commit()

# Initialize the database when the app starts
@app.before_first_request
def before_first_request():
    create_users_table()

# Endpoint for user registration
@app.route('/user', methods=['POST'])
def register_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    db = get_db()
    db.execute('INSERT INTO logins (username, email, password) VALUES (?, ?, ?)', (username, email, password))
    db.commit()
    return jsonify({'message': 'User created successfully'})

if __name__ == '__main__':
    app.run()