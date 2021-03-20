
#==== IMPORTS =====================================================================

from flask import Flask, session, redirect, url_for, request, jsonify, send_file, render_template
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from datetime import datetime
from dataclasses import dataclass
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import json
import uuid

#==== SETUP =====================================================================

# Create and configure Flask object
app = Flask(__name__)
app.config['SECRET_KEY'] = 'some random code here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 2**20 # 16 MB maximum upload
app.config['ALLOWED_EXTENSIONS'] = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

# Sessions setup
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(app.root_path, "cache") # Store session data in a /cache folder
app.config['SESSION_FILE_THRESHOLD'] = 1000 # Allow up to 1000 sessions
Session(app)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///whatsthat.db'
db = SQLAlchemy(app)
from models import *    # Import models.py
db.create_all()
db.session.commit()

# BCrypt for safe password hashing
bcrypt = Bcrypt(app)

#==== ROUTES =====================================================================

@app.route('/')
def index():
    return redirect("/static/login.html")

@app.route('/register', methods=["POST"])
def user_register():
    error = ""
    # Was an avatar uploaded?
    if request.files['avatar'].filename != '':
        f = request.files['avatar']
        avatar = secure_filename(str(uuid.uuid4()))
        f.save(app.root_path + '/photos/' + avatar)
    else:
        avatar = ""
    # bcrypt the password for safe storage
    pw_hash = bcrypt.generate_password_hash(request.values['password'])
    # Create the user object
    user = User(userid=request.values['userid'], 
        displayName=request.values['displayName'], 
        password=pw_hash, 
        email=request.values['email'], 
        avatar=avatar)
    # Try and save it to the database
    try:
        db.session.add(user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        # There was an error. The userid already exists.
        print(e)
        info = dict()
        info['title'] = "Unable to register"
        info['description'] = "That userid already exists"
        info['next'] = "/static/register.html"
        return render_template('error.html', error=info)
    return redirect("/static/login.html")

#==== MAIN =====================================================================

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)

