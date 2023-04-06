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

import threading
# import "packages" from flask
from flask import render_template  # import render_template from "public" flask libraries
from flask import Flask, request, jsonify
import sqlite3

@app.route('/api/logins')
def phone():
    conn = sqlite3.connect('api/sqlite.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS logins (username TEXT, email TEXT, password TEXT)')
    c.execute("SELECT * FROM logins")
    rows = c.fetchall()
    conn.close()

    data = []
    for row in rows:
        data.append({
            "username": row[0],
            "email": row[1],
            "text": row[2],
        })

    return jsonify(data)

@app.route('/submit', methods=['POST'])
def submit():
    user_id = request.form['user_id']
    number = request.form['email']

    # Save the data to the database
    conn = sqlite3.connect('api/sqlite.db')
    c = conn.cursor()
    c.execute("INSERT INTO logins (username, email, password) VALUES (?, ?, ?)", (username, email, password))
    conn.commit()
    conn.close()

    return "Data has been submitted successfully."