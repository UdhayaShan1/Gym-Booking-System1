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

booking_blueprint = Blueprint('booking', __name__)


@booking_blueprint.route('/booking_page')
def booking_page():
    if "email" not in session:
        return redirect("/")
    return render_template("booking/booking.html")

@booking_blueprint.route('/fetch_dates', methods=["POST","GET"])
def fetch_dates():
    if request.method != "POST":
        return redirect("/")
    curr_date = datetime.now().date()
    dates = [curr_date + timedelta(days=i) for i in range(14)]
    dates_str = []
    for i in dates:
        dates_str.append(str(i))
    return jsonify(dates_str)

@booking_blueprint.route('/selected_date', methods=["POST","GET"])
def selected_date():
    if request.method != "POST":
        return redirect("/")
    session["date"] = request.form.get("date")
    return jsonify({"status" : "success", "message" : "Selected"})

@booking_blueprint.route('/booking_times')
def booking_times():
    if "date" not in session:
        return redirect("/")
    print(session)
    return render_template("booking/booking_times.html")

@booking_blueprint.route('/fetch_times')
def fetch_times():
    curr_date = datetime.now().date()
    date_selected = datetime.strptime(session["date"], "%Y-%m-%d").date()
    mycursor = db.cursor()
    if curr_date == date_selected:
        current_time = datetime.now().time().strftime("%H:%M:%S")
        #print(current_time)
        sqlFormula = "SELECT * FROM booking_slots WHERE date = %s AND timeslot > %s"
        data = (str(curr_date), current_time, )

        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchall()
        print(myresult)
        if len(myresult) == 0:
            mycursor.close()
            return jsonify({"status" : "failure", "message" : "No more slots for the day"})
        else:
            dict = {}
            for i in myresult:
                dict[str(i[2])] = i[-3]
            print(dict)
            mycursor.close()
            return jsonify({"status" : "success", "result" : dict})
    else:
        sqlFormula = "SELECT * FROM booking_slots WHERE date = %s"
        data = (date_selected, )
        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchall()
        dict = {}
        for i in myresult:
            dict[str(i[2])] = i[3]
        mycursor.close()
        return jsonify({"status" : "success", "result" : dict})
    
@booking_blueprint.route('/selected_time', methods=["POST"])
def selected_time():
    if request.method != "POST":
        return redirect("/")
    mycursor = db.cursor()
    session["time"] = request.form.get("time")
    sqlFormula = "SELECT * FROM booking_slots WHERE assoc_nusnet = %s AND date = %s"
    data = (session["email"][0:8], session["date"], )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchall()
    if len(myresult) >= 3:
        mycursor.close()
        return jsonify({"status" : "failure", "message" : "You have booked the maximum slots for that day"})
    else:
        sqlFormula = "UPDATE booking_slots SET is_booked = 1, assoc_nusnet = %s WHERE timeslot = %s AND date = %s"
        data = (session["email"][0:8], session["time"], session["date"], )
        mycursor.execute(sqlFormula, data)
        db.commit()
        mycursor.close()
        return jsonify({"status" : "success", "message" : "Slot has been booked!"})

@booking_blueprint.route('/profile_completed')
def profile_completed():
    sqlFormula = sqlFormula = "SELECT * FROM user WHERE nusnet = %s AND roomNo IS NOT NULL AND name IS NOT NULL AND spotterName IS NOT NULL AND spotterRoomNo IS NOT NULL"
    data = (session["email"][0:8],  )
    mycursor = db.cursor()
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchall()
    mycursor.close()
    print(myresult)
    if len(myresult) != 0:
        return jsonify({"status" : "success"})
    else:
        return jsonify({"status" : "failure", "message" : "You have not completed your profile yet"})


@booking_blueprint.route("/edit_bookings")
def edit_bookings():
    if "email" not in session:
        return redirect("/")
    return render_template("booking/viewbookings.html")

@booking_blueprint.route("/fetch_bookings", methods=["POST"])
def fetch_bookings():
    if "email" not in session:
        return redirect("/")
    curr_date = datetime.now().date()
    curr_time = datetime.now().time().strftime("%H:%M")
    sqlFormula = "SELECT * FROM booking_slots WHERE is_booked = 1 AND assoc_nusnet = %s AND date = %s and timeslot > %s"
    data = (session["email"][0:8], curr_date, curr_time, )
    mycursor = db.cursor()
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchall()
    res = []
    for i in myresult:
        res.append(i)
    sqlFormula = "SELECT * FROM booking_slots WHERE is_booked = 1 AND assoc_nusnet = %s AND date > %s"
    data = (session["email"][0:8], curr_date, )
    mycursor = db.cursor()
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchall()
    for i in myresult:
        res.append(i)
    res2 = []
    for i in res:
        res2.append(str(i[1]) + " " + str(i[2]))
    #print(res2)
    return jsonify(res2)

@booking_blueprint.route("/unbook", methods=["POST"])
def unbook():
    if "email" not in session:
        return redirect("/")
    date = request.form.get("date")
    time = request.form.get("time")
    #print(time)
    sqlFormula = "UPDATE booking_slots SET is_booked = 0, assoc_teleId = %s, assoc_nusnet = %s WHERE date = %s AND timeslot = %s AND assoc_nusnet = %s"
    data = (None, None, date, time, session["email"][0:8], )
    mycursor = db.cursor()
    mycursor.execute(sqlFormula, data)
    db.commit()
    mycursor.close()
    return jsonify({"status" : "success", "message" : "Slot unbooked!"})