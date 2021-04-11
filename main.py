
#==== IMPORTS =====================================================================

from flask import Flask, session, redirect, request, jsonify, send_file, render_template
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from datetime import datetime
import os

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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
from models import *    # Import models.py
db.create_all()
db.session.commit()

#==== ROUTES =====================================================================

def errorMessage(title, description, goto):
    inf = { 'title': title, 'description': description, 'next': goto}
    return render_template('error.html', error=inf)

@app.route('/')
def index():
    return redirect("/static/login.html")

@app.route('/favicon.ico')
def favicon():
    return send_file("./static/favicon.ico")

@app.route('/login', methods=["POST"])
def user_login():
    print("/login: "+request.values['userid'])
    uid = User.query.filter_by(userid = request.values['userid']).one_or_none()
    # Did we get a user?
    if uid is None:
        return errorMessage('Invalid login','No username provided', '/static/login.html')
    # Does the password match?
    pw_attempt = request.values['password']
    if uid.password != pw_attempt:
        return errorMessage('Invalid login','Password incorrect', '/static/login.html')
    # Create the session
    session['userid'] = uid.userid
    session['displayName'] = uid.displayName
    session['avatar'] = uid.avatar
    print("/login: USER LOGGED IN: ",uid)
    return redirect("/static/main.html")

@app.route('/register', methods=["POST"])
def user_register():
    error = ""
    if request.invitecode == "special":
        # Was an avatar uploaded?
        if request.files['avatar'].filename != '':
            f = request.files['avatar']
            dot = f.filename.rfind(".")
            extension = f.filename[dot:].lower()
            avatar = request.values['email'].replace("@","_at_") + extension
            f.save(app.root_path + '/photos/' + avatar)
        else:
            avatar = ""
        user = User(userid=request.values['userid'], 
            displayName=request.values['displayName'], 
            password=request.values['password'], # WARNING THIS IS NOT SECURE
            email=request.values['email'], 
            avatar=avatar)
        try:
            db.session.add(user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            print(e)
            return errorMessage("Unable to register", error, "/static/register.html")
        return redirect("/static/login.html")

@app.route('/whoami')
def whoami():
    if 'displayName' in session:
        return jsonify({'displayName': session['displayName']})
    else:
        return "Error: Not logged in"

@app.route('/newmessage', methods=["POST","GET"])
def new_message():
    if 'message' in request.values and 'name' in session:
        new_message = Message(
            userid=session['userid'], 
            displayName=session['displayName'], 
            ip=request.remote_addr, 
            message=request.values['message'],
            dateTime=datetime.utcnow())
        db.session.add(new_message)
        db.session.commit()
        return jsonify({'result': 'ok'})
    else:
        return "Error: Not logged in, or no message received"
    
@app.route('/getmessages',methods=['GET'])
def get_messages():
    if 'since' in request.args:
        since = int(request.args['since'])
    else:
        since = 0
    msgs = Message.query.filter(Message.id > since).order_by(Message.dateTime.desc()).limit(100).all()
    reply = []
    for msg in msgs:
        reply.insert(0,msg.as_dict())
    return jsonify(reply)

@app.route('/getavatar/<userid>', methods=['GET'])
def get_avatar(userid):
    user = User.query.filter(User.userid == userid).one_or_none()
    if user is not None and user.avatar != "":
        return send_file(app.root_path + '/photos/' + user.avatar)
    else:
        return send_file(app.root_path + '/static/avatar_placeholder.png')

#==== MAIN =====================================================================

if __name__ == '__main__':
    if not os.path.exists(app.config['SESSION_FILE_DIR']):
        os.mkdir(app.config['SESSION_FILE_DIR'])
    if not os.path.exists(app.root_path + "/photos"):
        os.mkdir(app.root_path + "/photos")
    app.run(host="0.0.0.0", port=80, debug=True)

