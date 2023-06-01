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



# Database connection, we will use mySQL and localhost for now
import mysql.connector
pwd = None
with open("includes\database_pwd.txt") as f:
    pwd = f.read().strip()
db = mysql.connector.connect(
    host="localhost",
    user='root',
    passwd=pwd,
    database="testdatabase"
)

mycursor = db.cursor()

#Flask set-up
app = Flask(__name__)
app.secret_key = None
with open("includes\pyFlaskSecretKey.txt") as f:
    app.secret_key = f.read().strip()


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
    #print(request.method)
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        otp = request.form['otp']
        print(session)
        if "otp" not in session or session["otp"] != otp:
            return jsonify({"status": "failure", "message": "Wrong OTP, try again"})
        # Make a regular expression
        # for validating an Email
        if check(email) == False:
            return jsonify({"status": "failure", "message": "Invalid email format"})
        # Hash the password for security
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
        # Check if registered alr
        sqlFormula = "SELECT * FROM user_website WHERE email = %s"
        data = (email, )
        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchall()
        if len(myresult) > 0:
            return jsonify({"status": "success", "message": "You are registered already, proceed to login!"})

        sqlFormula = "INSERT INTO user_website (email, password) VALUES (%s, %s)"
        data = (email, hashed_password)
        mycursor.execute(sqlFormula, data)
        db.commit()
        mycursor.close()
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
        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchall()
        if len(myresult) == 0:
            return jsonify({"status" : "failure", "message" : "You have not registered"})
        if bcrypt.checkpw(password.encode("utf-8"), myresult[0][1].encode("utf-8")):
            session['email'] = email
            return jsonify({"status" : "success", "message" : "You have logged in!"})

        return jsonify({"status" : "failure", "message" : "Wrong password"}) 

    return render_template("login.html")

@app.route('/main')
def main():
    #Check if valid session
    if "email" in session:
        return render_template("main.html")
    return redirect("/")



if __name__ == '__main__':
    app.run(debug=True)
