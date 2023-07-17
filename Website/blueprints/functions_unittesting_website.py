#For unittesting of website helper functions
import unittest
import random
import re
import string
from blueprints.helper_functions import (generate_otp, 
                             check_string_format,
                             check,
                             check_email)

class TestGenerateOTP(unittest.TestCase):
    def test_generate_otp(self):
        otp = generate_otp()
        self.assertEqual(len(otp), 4)  # Check if OTP length is 4
        self.assertTrue(otp.isdigit())  # Check if OTP contains only digits

class TestCheckStringFormat(unittest.TestCase):
    def test_check_string_format(self):
        self.assertTrue(check_string_format("12-34"))  # Valid format
        self.assertTrue(check_string_format("12-34D"))  # Valid format with letter
        self.assertFalse(check_string_format("123-45"))  # Invalid format - too many digits
        self.assertFalse(check_string_format("12-345"))  # Invalid format - too many digits
        self.assertFalse(check_string_format("1234"))  # Invalid format - no hyphen

class TestCheck(unittest.TestCase):
    def test_check(self):
        self.assertTrue(check("test@example.com"))  # Valid email format
        self.assertTrue(check("test123@example.co.uk"))  # Valid email format
        self.assertFalse(check("test@@example.com"))  # Invalid email format - double @ symbol
        self.assertFalse(check("test.example.com"))  # Invalid email format - missing @ symbol
        self.assertFalse(check("test@example"))  # Invalid email format - missing domain

class TestCheckEmail(unittest.TestCase):
    def test_check_email(self):
        self.assertTrue(check_email("e1234567@u.nus.edu"))  # Valid NUS email format
        self.assertFalse(check_email("e1234567@nus.edu"))  # Invalid NUS email format - wrong domain
        self.assertFalse(check_email("e1234567@u.nus"))  # Invalid NUS email format - missing domain

if __name__ == '__main__':
    unittest.main()
