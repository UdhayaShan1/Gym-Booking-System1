from flask import Flask, render_template, request, jsonify, session, redirect, Blueprint
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
from flask_login import LoginManager, login_user, current_user, login_required, UserMixin, logout_user
import mysql.connector
from flask_session import Session
from datetime import datetime, timedelta
from databaseconn import db
from helper_functions import (generate_otp, 
                             check_string_format,
                             check,
                             check_email)


auth_blueprint = Blueprint('auth', __name__)





@auth_blueprint.route('/send_otp', methods=["POST"])
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



@auth_blueprint.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        otp = request.form['otp']
        if check_email(email.lower()) == False:
            return jsonify({"status" : "failure", "message" : "Use NUS email only"})
        if "otp" not in session or session["otp"] != otp:
            return jsonify({"status": "failure", "message": "Wrong OTP, try again"})
        if check(email) == False:
            return jsonify({"status": "failure", "message": "Invalid email format"})
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        sqlFormula = "SELECT * FROM user_website WHERE email = %s"
        data = (email.lower(), )
        mycursor = db.cursor()
        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchall()
        mycursor.close()
        if len(myresult) > 0:
            return jsonify({"status": "success", "message": "You are registered already, proceed to login!"})

        sqlFormula_insert = "INSERT INTO user_website (email, password, nusnet) VALUES (%s, %s, %s)"
        data = (email.lower(), hashed_password, email.lower()[:8])
        print(data)
        mycursor = db.cursor()
        mycursor.execute(sqlFormula_insert, data)
        db.commit()
        
        sqlFormula_checkTele = "SELECT * from user WHERE nusnet = %s"
        sqlFormula_insert = "INSERT INTO user (nusnet) VALUES (%s)"
        data = (email.lower()[0:8], )
        mycursor.execute(sqlFormula_checkTele, data)
        myresult = mycursor.fetchone()
        print(myresult)
        if myresult != None:
            mycursor.close()
            return jsonify({"status": "success", "message": "You are now registered"})
        else:
            mycursor.execute(sqlFormula_insert, data)
            mycursor.close()
            db.commit()
            return jsonify({"status": "success", "message": "You are now registered"})
    return render_template("register.html")


@auth_blueprint.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form['email'].lower()
        print(email)
        if check_email(email) == False:
            return jsonify({"status" : "failure", "message" : "Invalid NUS email format"})
        password = request.form['password']
        sqlFormula = "SELECT * FROM user_website WHERE email = %s"
        data = (email, )
        mycursor = db.cursor()
        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchall()
        mycursor.close()
        print(myresult)
        if len(myresult) == 0:
            return jsonify({"status" : "failure", "message" : "You have not registered"})
        if bcrypt.checkpw(password.encode("utf-8"), myresult[0][1].encode("utf-8")):
            session.clear()
            session['email'] = email
            return jsonify({"status" : "success", "message" : "You have logged in!"})

        return jsonify({"status" : "failure", "message" : "Wrong password"}) 
    if "email" in session:
        return redirect("/main")
    return render_template("login.html")


@auth_blueprint.route("/send_otp_forgot", methods=["POST"])
def send_otp_forgot():
    email_receiver = request.form['email']
    if check_email(email_receiver) == False:
        return jsonify({"status" : "failure", "message" : "Invalid NUSNET email format"})
    session["recoveryEmail"] = email_receiver
    sqlFormula = "SELECT * FROM user_website WHERE email = %s"
    data = (email_receiver, )
    mycursor = db.cursor()
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    mycursor.close()
    if myresult == None:
        return jsonify({"status" : "failure", "message" : "Not registered"})
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
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
    return jsonify({"status" : "success", "message" : "sent"})