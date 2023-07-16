import unittest
from main import validnusNet, check_room_format, dateValidator, timeValidator

class NUSNetValidationTests(unittest.TestCase):
    def test_valid_nusnet(self):
        nusnet = 'e1234567'
        self.assertTrue(validnusNet(nusnet))

    def test_invalid_nusnet(self):
        nusnet = 'invalid_nusnet'
        self.assertFalse(validnusNet(nusnet))

    def test_empty_string(self):
        nusnet = ''
        self.assertFalse(validnusNet(nusnet))

    def test_short_string(self):
        nusnet = 'e12345'
        self.assertFalse(validnusNet(nusnet))

    def test_long_string(self):
        nusnet = 'e123456789'
        self.assertFalse(validnusNet(nusnet))

class RoomFormatValidationTests(unittest.TestCase):
    def test_valid_room_format(self):
        room = '11-12F'
        self.assertTrue(check_room_format(room))

    def test_invalid_room_format(self):
        room = '11/12'
        self.assertFalse(check_room_format(room))

    def test_invalid_room_format_no_suffix(self):
        room = '11-12'
        self.assertTrue(check_room_format(room))

    def test_invalid_room_format_invalid_suffix(self):
        room = '11-12G'
        self.assertFalse(check_room_format(room))

    def test_empty_string(self):
        room = ''
        self.assertFalse(check_room_format(room))


class DateValidatorTests(unittest.TestCase):
    def test_valid_date_format(self):
        date_string = '2023-07-16'
        self.assertTrue(dateValidator(date_string))

    def test_invalid_date_format(self):
        date_string = '2023/07/16'
        self.assertFalse(dateValidator(date_string))

    def test_invalid_date_string(self):
        date_string = '2023-07-32'
        self.assertFalse(dateValidator(date_string))

    def test_invalid_date_length(self):
        date_string = '2023-07'
        self.assertFalse(dateValidator(date_string))

    def test_empty_date_string(self):
        date_string = ''
        self.assertFalse(dateValidator(date_string))

class TimeValidatorTests(unittest.TestCase):
    def test_valid_time_format(self):
        time_string = '09:00:00'
        self.assertTrue(timeValidator(time_string))

    def test_invalid_time_format(self):
        time_string = '9:00:00'
        self.assertFalse(timeValidator(time_string))

    def test_invalid_time_string(self):
        time_string = '25:00:00'
        self.assertFalse(timeValidator(time_string))

    def test_invalid_time_length(self):
        time_string = '09:00'
        self.assertFalse(timeValidator(time_string))

    def test_empty_time_string(self):
        time_string = ''
        self.assertFalse(timeValidator(time_string))



if __name__ == '__main__':
    unittest.main()


