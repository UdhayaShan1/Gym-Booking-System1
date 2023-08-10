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
from databaseconn import db, dbcreator
from blueprints.helper_functions import (generate_otp, 
                             check_string_format,
                             check,
                             check_email)

equipment_blueprint = Blueprint('equipment', __name__)

@equipment_blueprint.route("/equipmentpage")
def equipmentPage():
    return render_template("equipment/equipment.html")

@equipment_blueprint.route("/fetchequipmentweight")
def fetchEquipmentWeight():
    sqlFormulaWeights = "SELECT * FROM equipment WHERE weight IS NOT NULL"
    mycursor = db.cursor()
    mycursor.execute(sqlFormulaWeights)
    myresult = mycursor.fetchall()
    mycursor.close()
    dict_weight = {}
    for i in myresult:
        if i[1] not in dict_weight:
            dict_weight[i[1]] = {}
        else:
            if i[2] == 1:
                if i[3] not in dict_weight[i[1]]:
                    dict_weight[i[1]][i[3]] = 1
                else:
                    dict_weight[i[1]][i[3]] += 1
    #print(dict_weight)
    
    return jsonify(dict_weight)

@equipment_blueprint.route("/fetchequipmentothers")
def fetchEquipmentOthers():
    sqlFormulaWeights = "SELECT * FROM equipment WHERE weight IS NULL"
    mycursor = db.cursor()
    mycursor.execute(sqlFormulaWeights)
    myresult = mycursor.fetchall()
    dict_nonweight = {}
    #print(myresult)
    for i in myresult:
        dict_nonweight[i[1]] = [i[2], i[4]]
    mycursor.close()
    #print(dict_nonweight)
    return jsonify(dict_nonweight)

@equipment_blueprint.route("/fetchequipmentall")
def fetchEquipmentAll():
    sqlFormula = "SELECT name FROM equipment"
    db1 = dbcreator()
    mycursor = db1.cursor()
    mycursor.execute(sqlFormula)
    myresult = mycursor.fetchall()
    dp = {}
    print(myresult)
    for i in myresult:
        dp[i[0]] = 1
    mycursor.close()
    db1.close()
    print(dp)
    return jsonify(dp)

@equipment_blueprint.route("/equipmentreport", methods=["POST"])
def equipmentReport():
    feedback = request.form["feedback"]
    equipment = request.form["equipment"]
    print(feedback, equipment)
    return jsonify({"status" : "success"})
