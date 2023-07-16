#Package to store helper functions
import re
import random
import string
from email.message import EmailMessage
import ssl
import smtplib

#Helper function to validate nusnet
def validnusNet(input_string):
    pattern = r'^e\d{7}$'  # Regex pattern to match "e" followed by 7 digits
    match = re.match(pattern, input_string)
    return match is not None


#Helper function to check valid room number format
def check_room_format(string):
    pattern = r"^\d{2}-\d{2}[a-zA-Z]?$"
    if re.match(pattern, string):
        return True
    else:
        return False
    
def dateValidator(date_string):
    # Regex pattern for "YYYY-MM-DD" with date <= 31
    pattern = r'^\d{4}-(0[1-9]|1[0-2])-([0-2][1-9]|3[0-1])$'  # Regex pattern for "YYYY-MM-DD" with day validation
    match = re.match(pattern, date_string)
    return match is not None

def timeValidator(time_string):
    pattern = r'^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$'
    match = re.match(pattern, time_string)
    return match is not None

# Generate a random OTP
async def generate_otp():
    otp = ''.join(random.choices(string.digits, k=4))
    return otp

# Send otp to user
async def send_otp(nusnet):
    email_receiver = nusnet+"@u.nus.edu"
    email_sender = "chad.ionos2@gmail.com"
    email_pw = None
    with open("includes\gmailPwd.txt") as f:
        email_pw = f.read().strip()
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em["Subject"] = "Your FitBook OTP"
    otp = await generate_otp()
    em.set_content("Your OTP is " + otp)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_pw)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
    return otp