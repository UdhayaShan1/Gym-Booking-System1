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

reports_blueprint = Blueprint('reports', __name__)

@reports_blueprint.route("/report", methods=["POST", "GET"])
def report():
    if request.method == "POST":
        feedback = request.form.get('feedback')
        print(feedback)
        sqlFormula = "INSERT INTO reports (report, nusnet) VALUES (%s, %s)"
        data = (feedback, str(session['email'])[0:8])
        mycursor = db.cursor()
        mycursor.execute(sqlFormula, data)
        db.commit()
        mycursor.close()
        return jsonify({"status" : "success", "message" : "Entered feedback!"})
    else:
        if "email" in session:
            return render_template("reports/report.html")
        return redirect("/")

    """
    file = request.files['photo']
    user_folder = os.path.join("photos/", str(session['email'])[0:8])
    os.makedirs(user_folder, exist_ok=True)
    file.save("photos/str(session['email'])[0:8]/file.jpg")
    """

@reports_blueprint.route("/viewreports")
def viewReports():
    if "email" not in session:
        return redirect("/")
    return render_template("reports/viewReports.html")

@reports_blueprint.route('/fetchreports', methods=["POST", "GET"])
def fetchReports():
    if request.method != "POST":
        return redirect("/")
    sqlFormula = "SELECT * FROM reports WHERE nusnet = %s"
    data = (session['email'][0:8], )
    mycursor = db.cursor()
    mycursor.execute(sqlFormula , data)
    myresult = mycursor.fetchall()
    mycursor.close()
    res = []
    for i in myresult:
        res.append([i[0], i[-2], i[-1]])
    print(res)
    return jsonify(res)

@reports_blueprint.route("/selectedreport", methods = ["POST", "GET"])
def selectedReport():
    if request.method != "POST":
        return redirect("/")
    reportid = request.form.get("id")
    session["reportid"] = reportid
    return jsonify({"status" : "success"})


@reports_blueprint.route("/viewresponses")
def viewResponses():
    if "reportid" not in session:
        return redirect("/")
    return render_template("reports/viewResponses.html")

@reports_blueprint.route("/fetchresponses", methods = ["POST", "GET"])
def fetchResponses():
    if request.method != "POST" or "reportid" not in session:
        return redirect("/")
    sqlFormula = "SELECT * FROM reports_response WHERE reportId = %s"
    data = (session["reportid"], )
    mycursor = db.cursor()
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchall()
    res = []
    for i in myresult:
        res.append(i[-1])
    mycursor.close()
    return jsonify(res)