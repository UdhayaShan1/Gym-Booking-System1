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
from blueprints.helper_functions import (generate_otp, 
                             check_string_format,
                             check,
                             check_email)


profile_blueprint = Blueprint('profile', __name__)

@profile_blueprint.route('/user_details')
def userdetails():
    if "email" not in session:
        return redirect("/")
    #print(session["email"][:8])
    sqlFormula = "SELECT * FROM user WHERE nusnet = %s"
    data = (session["email"][:8], )
    mycursor = db.cursor()
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    mycursor.close()
    if myresult == None:
            return jsonify({"email" :  session["email"], 
                    "name" : None, 
                    "roomNo" : None,
                    "spotterName" : None,
                    "spotterRoomNo" : None})
    return jsonify({"email" :  session["email"], 
                    "name" : myresult[3], 
                    "roomNo" : myresult[2],
                    "spotterName" : myresult[4],
                    "spotterRoomNo" : myresult[5]})

@profile_blueprint.route('/profile')
def profile():
    if "email" not in session:
        return redirect("/")
    return render_template("profile.html")

@profile_blueprint.route('/update_name', methods=["POST"])
def update_name():
    if request.method == "POST":
        name = request.form["name"]
        mycursor = db.cursor()
        sqlFormula = "UPDATE user SET name = %s WHERE nusnet = %s"
        data = (name, session["email"][0:8], )
        mycursor.execute(sqlFormula, data)
        db.commit()
        mycursor.close()
        return jsonify({"status" : "success", "message" : "Name updated"})
    return jsonify({"status" : "failure", "message" : "Error in submission, try again"})


@profile_blueprint.route('/update_room', methods=["POST"])
def update_room():
    if request.method == "POST":
        room = request.form["room"]
        if check_string_format(room) == False:
            return jsonify({"status" : "failure", "message" : "Invalid room number format, ensure it is XX-YY or XX-YYD"})
        mycursor = db.cursor()
        sqlFormula = "UPDATE user SET roomNo = %s WHERE nusnet = %s"
        data = (room, session["email"][0:8], )
        #print(data)
        mycursor.execute(sqlFormula, data)
        db.commit()
        mycursor.close()
        return jsonify({"status" : "success", "message" : "Room number updated"})
    return jsonify({"status" : "failure", "message" : "Error in submission, try again"})

@profile_blueprint.route('/update_spotter', methods=["POST"])
def update_spotter():
    if request.method == "POST":
        spotter = request.form["spotterName"]
        mycursor = db.cursor()
        sqlFormula = "UPDATE user SET spotterName = %s WHERE nusnet = %s"
        data = (spotter, session["email"][0:8], )
        mycursor.execute(sqlFormula, data)
        db.commit()
        mycursor.close()
        return jsonify({"status" : "success", "message" : "Spotter name updated"})
    return jsonify({"status" : "failure", "message" : "Error in submission, try again"})

@profile_blueprint.route('/update_spotter_room', methods=["POST"])
def update_spotterRoom():
    if request.method == "POST":
        spotterRoom = request.form["spotterRoom"]
        if check_string_format(spotterRoom) == False:
            return jsonify({"status" : "failure", "message" : "Invalid room number format, ensure it is XX-YY or XX-YYD"})
        mycursor = db.cursor()
        sqlFormula = "UPDATE user SET spotterRoomNo = %s WHERE nusnet = %s"
        data = (spotterRoom, session["email"][0:8], )
        mycursor.execute(sqlFormula, data)
        db.commit()
        mycursor.close()
        return jsonify({"status" : "success", "message" : "Spotter room number updated"})
    return jsonify({"status" : "failure", "message" : "Error in submission, try again"})