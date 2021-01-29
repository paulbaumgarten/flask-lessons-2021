from flask import Flask, request, render_template, send_file
from datetime import datetime
from werkzeug.utils import secure_filename
import os

# Create the object for our webserver
app = Flask(__name__)
app.config['SECRET_KEY'] = 'some random code here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Web server
@app.route('/')
def index():
    return send_file("session1page1.html")

@app.route('/page2', methods=['POST', 'GET'])
def page2():
    # Get a copy of the information received
    inf = dict(request.form)
    # Print it out so we can see it
    print(inf)
    # We can get individual fields this way
    person = inf['givenname']
    print(f"This person used the form: { person }") # Print a variable
    # Save file
    f = request.files['picture']
    filename = inf['givenname'] + "_" + inf['familyname'] + ".jpg"
    f.save('uploads/'+secure_filename(filename))
    inf['picture'] = filename
    # Calculate age
    if request.form['dateofbirth'] != "":
        dob = datetime.strptime(request.form['dateofbirth'], "%Y-%m-%d") # yyyy-mm-dd style of date from the browser
        today = datetime.now()
        age = today.year - dob.year
        if today.month < dob.month:
            age = age - 1
        elif today.month == dob.month:
            if today.day < dob.day:
                age = age - 1
        inf['age'] = age # Add 'age' to the information we will send in our reply
    else:
        inf['age'] = "unknown"
    # Send reply
    return render_template("session1page2.html", inf=inf)

@app.route('/photo/<filename>', methods=['POST', 'GET'])
def photo(filename):
    if os.path.exists("uploads/"+secure_filename(filename)):
        return send_file("uploads/"+secure_filename(filename))
    else:
        return "File not found",404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)

