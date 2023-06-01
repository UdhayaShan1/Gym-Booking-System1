from flask import Flask, render_template, request, jsonify
import bcrypt

import re


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

app = Flask(__name__)


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


@app.route('/register', methods=["POST", "GET"])
def register():
    #print(request.method)
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
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
            return jsonify({"status": "failure", "message": "You are registered already, proceed to login!"})

        sqlFormula = "INSERT INTO user_website (email, password) VALUES (%s, %s)"
        data = (email, hashed_password)
        mycursor.execute(sqlFormula, data)
        db.commit()
        mycursor.close()
        return jsonify({"status": "success", "message": "You are now registered"})

    return render_template("register.html")

@app.route('/login', methods=["POST", "GET"])
def login():
    email = request.form['email']
    password = request.form['password']
    



if __name__ == '__main__':
    app.run(debug=True)
