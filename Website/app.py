from flask import Flask, render_template, request, jsonify, session, redirect
import bcrypt
import re
import base64
import os
import os.path
import smtplib
from email.message import EmailMessage
import ssl
import random
import string
#from flask_login import LoginManager, login_user, current_user, login_required, UserMixin, logout_user
import mysql.connector
from flask_session import Session
from datetime import datetime, timedelta
from databaseconn import db
from blueprints.helper_functions import (generate_otp, 
                             check_string_format,
                             check,
                             check_email)


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

#Register blueprints
from blueprints.auth import auth_blueprint
from blueprints.profile import profile_blueprint
from blueprints.booking import booking_blueprint
from blueprints.reports import reports_blueprint
from blueprints.equipment import equipment_blueprint
app.register_blueprint(auth_blueprint, url_prefix='')
app.register_blueprint(profile_blueprint, url_prefix='')
app.register_blueprint(booking_blueprint, url_prefix='')
app.register_blueprint(reports_blueprint, url_prefix='')
app.register_blueprint(equipment_blueprint, url_prefix='')

@app.route('/')
def home():
    return render_template("index.html")

# Define a function for
# for validating an Email

@app.route("/send_otp_changepwd")
def send_otp_changepwd():
    print(session)
    if "email" not in session:
        return redirect("/")
    email_sender = "chad.ionos2@gmail.com"
    email_password = None
    with open("includes\gmailPwd.txt") as f:
        email_password = f.read().strip()
    subject = "OTP"
    otp = generate_otp()
    body = "Your OTP is " + otp;
    session["recoveryOtp"] = otp
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = session["email"]
    session["recoveryEmail"] = session["email"]
    em['Subject'] = subject
    em.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, session["email"], em.as_string())
    return jsonify({"status" : "success", "message" : "sent"})

@app.route("/change_pwd")
def change_pwd():
    if "recoveryEmail" not in session:
        return redirect("/")
    return render_template("changePwd.html")

@app.route("/send_newpwd", methods=["POST"])
def send_newpwd():
    if "recoveryEmail" not in session:
        return redirect("/")
    otp = request.form.get("otp")
    pwd = request.form.get("pwd")
    if otp != session["recoveryOtp"]:
        return jsonify({"status" : "failure", "message" : "OTP does not match"})
    hashed_password = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
    sqlFormula = "UPDATE user_website SET password = %s WHERe nusnet = %s"
    data = (hashed_password, session["recoveryEmail"][0:8], )
    mycursor = db.cursor()
    mycursor.execute(sqlFormula, data)
    db.commit()
    mycursor.close()
    #To start with clean slate(email, otp, recoveryemail, recoveryOtp all inside dictionary idk if makes sense) and to check if user knows his pwd
    session.clear()
    return jsonify({"status" : "success", "message" : "Password changed for your account! Please attempt to login to check"})

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

if __name__ == '__main__':
    app.run(debug=True)