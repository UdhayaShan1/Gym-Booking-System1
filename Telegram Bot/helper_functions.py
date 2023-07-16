#Package to store helper functions
import re
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