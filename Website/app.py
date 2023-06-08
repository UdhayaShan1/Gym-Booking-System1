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
from datetime import datetime, timedelta


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

#Use regular expressions to check if email follows NUS format
def check_email(email):
    pattern = r'^e\d{7}@u\.nus\.edu$'  # Regex pattern for the email format
    match = re.match(pattern, email)
    return match is not None


@app.route('/register', methods=["POST", "GET"])
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


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form['email'].lower()
        print(email)
        if check(email) == False:
            return jsonify({"status" : "failure", "message" : "Invalid email format"})
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

#Room number validation
def check_string_format(string):
    pattern = r"^\d{2}-\d{2}[a-zA-Z]?$"
    if re.match(pattern, string):
        return True
    else:
        return False

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

if __name__ == '__main__':
    app.run(debug=True)