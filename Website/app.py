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
app.register_blueprint(auth_blueprint, url_prefix='')


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

@app.route('/user_details')
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
        sqlFormula = "UPDATE user SET name = %s WHERE nusnet = %s"
        data = (name, session["email"][0:8], )
        mycursor.execute(sqlFormula, data)
        db.commit()
        mycursor.close()
        return jsonify({"status" : "success", "message" : "Name updated"})
    return jsonify({"status" : "failure", "message" : "Error in submission, try again"})


@app.route('/update_room', methods=["POST"])
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

@app.route('/update_spotter', methods=["POST"])
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

@app.route('/update_spotter_room', methods=["POST"])
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

@app.route('/booking_page')
def booking_page():
    if "email" not in session:
        return redirect("/")
    return render_template("booking/booking.html")

@app.route('/fetch_dates', methods=["POST","GET"])
def fetch_dates():
    if request.method != "POST":
        return redirect("/")
    curr_date = datetime.now().date()
    dates = [curr_date + timedelta(days=i) for i in range(14)]
    dates_str = []
    for i in dates:
        dates_str.append(str(i))
    return jsonify(dates_str)

@app.route('/selected_date', methods=["POST","GET"])
def selected_date():
    if request.method != "POST":
        return redirect("/")
    session["date"] = request.form.get("date")
    return jsonify({"status" : "success", "message" : "Selected"})

@app.route('/booking_times')
def booking_times():
    if "date" not in session:
        return redirect("/")
    print(session)
    return render_template("booking/booking_times.html")

@app.route('/fetch_times')
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
    
@app.route('/selected_time', methods=["POST"])
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

@app.route('/profile_completed')
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


@app.route("/edit_bookings")
def edit_bookings():
    if "email" not in session:
        return redirect("/")
    return render_template("booking/viewbookings.html")

@app.route("/fetch_bookings", methods=["POST"])
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

@app.route("/unbook", methods=["POST"])
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

@app.route("/report", methods=["POST", "GET"])
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

@app.route("/viewreports")
def viewReports():
    if "email" not in session:
        return redirect("/")
    return render_template("reports/viewReports.html")

@app.route('/fetchreports', methods=["POST", "GET"])
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

@app.route("/selectedreport", methods = ["POST", "GET"])
def selectedReport():
    if request.method != "POST":
        return redirect("/")
    reportid = request.form.get("id")
    session["reportid"] = reportid
    return jsonify({"status" : "success"})


@app.route("/viewresponses")
def viewResponses():
    if "reportid" not in session:
        return redirect("/")
    return render_template("reports/viewResponses.html")

@app.route("/fetchresponses", methods = ["POST", "GET"])
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


@app.route("/equipmentpage")
def equipmentPage():
    return render_template("equipment/equipment.html")

@app.route("/fetchequipmentweight")
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

@app.route("/fetchequipmentothers")
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




if __name__ == '__main__':
    app.run(debug=True)