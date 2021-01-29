from flask import Flask, session, redirect, url_for, request, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from dataclasses import dataclass
import json

# Create the object for our webserver
app = Flask(__name__)
# SECRET_KEY is used to encrypt the content of user session data & cookies
app.config['SECRET_KEY'] = 'some random code here'
# Set up server based session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(app.root_path, "cache") # Store session data in a /cache folder
app.config['SESSION_FILE_THRESHOLD'] = 1000 # Allow up to 1000 sessions
Session(app)
# Set up the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///whatsthat.db'
db = SQLAlchemy(app)

# Database objects

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    displayName = db.Column(db.String(100))
    dateTime = db.Column(db.DateTime, default=datetime.utcnow)
    ip = db.Column(db.String(20))
    message = db.Column(db.String(500))
    def as_dict(self):
        return {"id": self.id, "displayName": self.displayName, "dateTime":self.dateTime.timestamp(), "message":self.message}

# Web server

@app.route('/')
def index():
    return redirect("/static/index.html")

@app.route('/signin', methods=["POST"])
def signin():
    name = request.values['signinname']
    if len(name) > 0:
        session['name'] = request.values['signinname']
        return redirect("/static/main.html")
    else:
        return redirect("/static/index.html")

@app.route('/whoami')
def whoami():
    if 'name' in session:
        return jsonify({'name': session['name']})
    else:
        return "Error: Not logged in"

@app.route('/newmessage', methods=["POST","GET"])
def newmessage():
    if 'message' in request.values and 'name' in session:
        new_message = Message(
            username=session['name'], 
            displayName=session['name'], 
            ip=request.remote_addr, 
            message=request.values['message'],
            dateTime=datetime.utcnow())
        db.session.add(new_message)
        db.session.commit()
        return jsonify({'result': 'ok'})
    else:
        return "Error: Not logged in, or no message received"
    
@app.route('/getmessages',methods=['GET'])
def getmessages():
    if 'since' in request.args:
        since = int(request.args['since'])
    else:
        since = 0
    msgs = Message.query.filter(Message.id > since).order_by(Message.dateTime.desc()).limit(100).all()
    reply = []
    for msg in msgs:
        reply.insert(0,msg.as_dict())
    return jsonify(reply)

if __name__ == '__main__':
    if not os.path.exists(app.config['SESSION_FILE_DIR']):
        os.mkdir(app.config['SESSION_FILE_DIR'])
    app.run(host="0.0.0.0", port=80, debug=True)

"""
# https://www.youtube.com/watch?v=Z1RJmh_OqeA
# https://github.com/jakerieger/FlaskIntroduction/blob/master/app.py
from app import db
db.create_all()
exit()
"""