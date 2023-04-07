import threading
from flask import Flask, request, jsonify
import sqlite3

# import "packages" from flask
from flask import render_template  # import render_template from "public" flask libraries

# import "packages" from "this" project
from __init__ import app,db  # Definitions initialization
from model.jokes import initJokes
from model.users import initUsers
from model.players import initPlayers


# setup APIs
from api.covid import covid_api # Blueprint import api definition
from api.joke import joke_api # Blueprint import api definition
from api.user import user_api # Blueprint import api definition
from api.player import player_api


# setup App pages
from projects.projects import app_projects # Blueprint directory import projects definition

# register URIs
app.register_blueprint(joke_api) # register api routes
app.register_blueprint(covid_api) # register api routes
app.register_blueprint(user_api) # register api routes
app.register_blueprint(player_api)
app.register_blueprint(app_projects) # register app pages

@app.errorhandler(404)  # catch for URL not found
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.route('/')  # connects default URL to index() function
def index():
    return render_template("index.html")

@app.route('/stub/')  # connects /stub/ URL to stub() function
def stub():
    return render_template("stub.html")

app = Flask(__name__)

# Create SQLite database and table
conn = sqlite3.connect('api/sqlite.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS logins
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              email TEXT NOT NULL,
              password TEXT NOT NULL);''')
conn.commit()
conn.close()

# Route for login
@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']
    # Connect to SQLite database and check if user exists
    conn = sqlite3.connect('api/sqlite.db')
    c = conn.cursor()
    c.execute("SELECT * FROM logins WHERE email = ? AND password = ?", (email, password))
    user = c.fetchone()
    conn.close()
    if user:
        # Return a JWT token or any other authentication token
        return jsonify({'token': 'YOUR_TOKEN_HERE'})
    else:
        return jsonify({'message': 'Invalid email or password'})

# Route for signup
@app.route('/signup', methods=['POST'])
def signup():
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']
    # Connect to SQLite database and insert user data
    conn = sqlite3.connect('api/sqlite.db')
    c = conn.cursor()
    c.execute("INSERT INTO logins (name, email, password) VALUES (?, ?, ?)", (name, email, password))
    conn.commit()
    conn.close()
    # Return a JWT token or any other authentication token
    return jsonify({'token': 'YOUR_TOKEN_HERE'})

@app.before_first_request
def activate_job():  # activate these items 
    # db.init_app(app)
    initJokes()
    initUsers()
    initPlayers()

# this runs the application on the development server
if __name__ == "__main__":
    # change name for testing
    from flask_cors import CORS
    cors = CORS(app)
    app.run(debug=True, host="0.0.0.0", port="8086")
