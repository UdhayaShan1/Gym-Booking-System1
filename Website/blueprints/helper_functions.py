import re, string, random
# Generate a random OTP
def generate_otp():
    otp = ''.join(random.choices(string.digits, k=4))
    return otp

#Room number validation
def check_string_format(string):
    pattern = r"^\d{2}-\d{2}[a-zA-Z]?$"
    if re.match(pattern, string):
        return True
    else:
        return False
    
def check(email):
    # pass the regular expression
    # and the string into the fullmatch() method
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, email):
        return True
    return False

#Use regular expressions to check if email follows NUS format
def check_email(email):
    pattern = r'^e\d{7}@u\.nus\.edu$'  # Regex pattern for the email format
    match = re.match(pattern, email)
    return match is not None