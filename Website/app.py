from flask import Flask, render_template, request, jsonify, session, redirect
import bcrypt
import re
import base64
import os.path
import smtplib
from email.message import EmailMessage
import ssl
import random
import string
from flask_login import LoginManager, login_user, current_user, login_required, UserMixin, logout_user
import mysql.connector
from flask_session import Session


# Database connection, we will use mySQL and localhost for now
import mysql.connector
pwd = None
with open("includes\database_pwd.txt") as f:
    pwd = f.read().strip()
db = mysql.connector.connect(
    host="localhost",
    user='root',
    passwd=pwd,
    database="testdatabase",
    connect_timeout=30
)


#Flask set-up
app = Flask(__name__)
app.secret_key = None
with open("includes\pyFlaskSecretKey.txt") as f:
    app.secret_key = f.read().strip()

app.config["SESSION_TYPE"] = "filesystem"  # Use filesystem-based session storage
app.config["SESSION_PERMANENT"] = False  # Session expires when the user closes the browser
app.config["SESSION_USE_SIGNER"] = True  # Enable secure session signing
app.config["SESSION_COOKIE_SECURE"] = True  # Transmit session cookies over HTTPS only
app.config["SESSION_COOKIE_HTTPONLY"] = True  # Set session cookies as HttpOnly
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Set SameSite attribute for session cookies

Session(app)

@app.route('/')
def home():
    return render_template("index.html")

# Define a function for
# for validating an Email


def check(email):
    # pass the regular expression
    # and the string into the fullmatch() method
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, email):
        return True
    return False

# Generate a random OTP
def generate_otp():
    otp = ''.join(random.choices(string.digits, k=4))
    return otp


@app.route('/send_otp', methods=["POST"])
def send_otp():
    email_receiver = request.form['email']
    sqlFormula = "SELECT * FROM user_website WHERE email = %s"
    data = (email_receiver, )
    mycursor = db.cursor()
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    mycursor.close()
    if myresult != None:
        return jsonify({"status" : "failure", "message" : "Already registered"})

    if check(email_receiver) == False:
        return jsonify({"status" : "failure", "message" : "Invalid email format, use XXX email only"})
    email_sender = "chad.ionos2@gmail.com"
    email_password = None
    with open("includes\gmailPwd.txt") as f:
        email_password = f.read().strip()
    subject = "OTP"
    otp = generate_otp()
    body = "Your OTP is " + otp;
    session["otp"] = otp
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
    return jsonify({"status" : "success", "message" : "sent"})

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        otp = request.form['otp']
        print(session)
        if "otp" not in session or session["otp"] != otp:
            return jsonify({"status": "failure", "message": "Wrong OTP, try again"})
        if check(email) == False:
            return jsonify({"status": "failure", "message": "Invalid email format"})
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        sqlFormula = "SELECT * FROM user_website WHERE email = %s"
        data = (email, )
        mycursor = db.cursor()
        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchall()
        mycursor.close()
        if len(myresult) > 0:
            return jsonify({"status": "success", "message": "You are registered already, proceed to login!"})

        # Establish a new connection and cursor
        db_new = mysql.connector.connect(
            host="localhost",
            user='root',
            passwd=pwd,
            database="testdatabase",
            connect_timeout=30
        )
        cursor = db_new.cursor()

        sqlFormula = "INSERT INTO user_website (email, password) VALUES (%s, %s)"
        data = (email, hashed_password)
        cursor.execute(sqlFormula, data)
        db_new.commit()

        # Close the cursor and database connection
        cursor.close()
        db_new.close()

        return jsonify({"status": "success", "message": "You are now registered"})

    return render_template("register.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form['email']
        if check(email) == False:
            return jsonify({"status" : "failure", "message" : "Invalid email format"})
        password = request.form['password']
        sqlFormula = "SELECT * FROM user_website WHERE email = %s"
        data = (email, )
        mycursor = db.cursor()
        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchall()
        mycursor.close()
        #print(session)
        if len(myresult) == 0:
            return jsonify({"status" : "failure", "message" : "You have not registered"})
        if bcrypt.checkpw(password.encode("utf-8"), myresult[0][1].encode("utf-8")):
            session.clear()
            session['email'] = email
            return jsonify({"status" : "success", "message" : "You have logged in!"})

        return jsonify({"status" : "failure", "message" : "Wrong password"}) 

    return render_template("login.html")

@app.route('/main')
def main():
    print(session)
    #Check if valid session
    if "email" in session:
        return render_template("main.html")
    return redirect("/")

@app.route('/logout', methods = ["POST"])
def logout():
    session.clear()
    return jsonify({"status" : "success", "message" : "You have logged out"})

@app.route('/user_details')
def userdetails():
    if "email" not in session:
        return redirect("/")
    sqlFormula = "SELECT * FROM user_website WHERE email = %s"
    data = (session["email"], )
    mycursor = db.cursor()
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    mycursor.close()
    return jsonify({"email" :  session["email"], 
                    "name" : myresult[2], 
                    "roomNo" : myresult[3],
                    "spotterName" : myresult[4],
                    "spotterRoomNo" : myresult[5]})

@app.route('/profile')
def profile():
    if "email" not in session:
        return redirect("/")
    return render_template("profile.html")

@app.route('/update_name', methods=["POST"])
def update_name():
    if request.method == "POST":
        name = request.form["name"]
        mycursor = db.cursor()
        sqlFormula = "UPDATE user_website SET name = %s WHERE email = %s"
        data = (name, session["email"], )
        mycursor.execute(sqlFormula, data)
        db.commit()
        mycursor.close()
        return jsonify({"status" : "success", "message" : "Name updated"})
    return jsonify({"status" : "failure", "message" : "Error in submission, try again"})

@app.route('/update_room', methods=["POST"])
def update_room():
    if request.method == "POST":
        room = request.form["room"]
        mycursor = db.cursor()
        sqlFormula = "UPDATE user_website SET roomNo = %s WHERE email = %s"
        data = (room, session["email"], )
        print(data)
        mycursor.execute(sqlFormula, data)
        db.commit()
        mycursor.close()
        return jsonify({"status" : "success", "message" : "Room number updated"})
    return jsonify({"status" : "failure", "message" : "Error in submission, try again"})

@app.route('/update_spotter', methods=["POST"])
def update_spotter():
    if request.method == "POST":
        spotter = request.form["spotterName"]
        mycursor = db.cursor()
        sqlFormula = "UPDATE user_website SET spotterName = %s WHERE email = %s"
        data = (spotter, session["email"], )
        mycursor.execute(sqlFormula, data)
        db.commit()
        mycursor.close()
        return jsonify({"status" : "success", "message" : "Spotter name updated"})
    return jsonify({"status" : "failure", "message" : "Error in submission, try again"})

@app.route('/update_spotter_room', methods=["POST"])
def update_spotterRoom():
    if request.method == "POST":
        spotterRoom = request.form["spotterRoom"]
        mycursor = db.cursor()
        sqlFormula = "UPDATE user_website SET spotterRoomNo = %s WHERE email = %s"
        data = (spotterRoom, session["email"], )
        mycursor.execute(sqlFormula, data)
        db.commit()
        mycursor.close()
        return jsonify({"status" : "success", "message" : "Spotter room number updated"})
    return jsonify({"status" : "failure", "message" : "Error in submission, try again"})



if __name__ == '__main__':
    app.run(debug=True)