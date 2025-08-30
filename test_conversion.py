import unittest
import conversion

# class TestXSL(unittest.TestCase):
#     def test_stops(self):
#         print("stops")

#     def test_agency(self):
#         print("agency")

#     def test_routes(self):
#         print("routes")

#     def test_stop_times(self):
#         print("stop times")

#     def test_trips(self):
#         print("trips")

#     def test_calendar(self):
#         print("calendar")


# Test function extract_time_string
class TestTimeConvert(unittest.TestCase):

    def test_valid(self):
        # minimum hour
        t = conversion.extract_time_string("PT0H")
        self.assertEqual(t[0],"00:00:00")
        self.assertEqual(t[1], "")
        # maximum hour
        t = conversion.extract_time_string("PT59H")
        self.assertEqual(t[0],"59:00:00")
        self.assertEqual(t[1], "")
        # minimum minute
        t = conversion.extract_time_string("PT0M")
        self.assertEqual(t[0],"00:00:00")
        self.assertEqual(t[1], "")
        # maximum minute
        t = conversion.extract_time_string("PT59M")
        self.assertEqual(t[0],"00:59:00")
        self.assertEqual(t[1], "")
        # minimum second
        t = conversion.extract_time_string("PT0S")
        self.assertEqual(t[0],"00:00:00")
        self.assertEqual(t[1], "")
        # maximum second
        t = conversion.extract_time_string("PT59S")
        self.assertEqual(t[0],"00:00:59")
        self.assertEqual(t[1], "")
        # mid-range tests
        t = conversion.extract_time_string("PT12H")
        self.assertEqual(t[0],"12:00:00")
        self.assertEqual(t[1], "")
        t = conversion.extract_time_string("PT28M")
        self.assertEqual(t[0],"00:28:00")
        self.assertEqual(t[1], "")
        t = conversion.extract_time_string("PT40S")
        self.assertEqual(t[0],"00:00:40")
        self.assertEqual(t[1], "")
    
    def test_invalid_length(self):
        t = conversion.extract_time_string("")
        self.assertEqual(t[0],"00:00:00")
        self.assertEqual(t[1], "Time string invalid length")
        t = conversion.extract_time_string("PT555H")
        self.assertEqual(t[0],"00:00:00")
        self.assertEqual(t[1], "Time string invalid length")
        t = conversion.extract_time_string("PM")
        self.assertEqual(t[0],"00:00:00")
        self.assertEqual(t[1], "Time string invalid length")
    
    def test_invalid_numbers(self):
        # negative number is parsed as non-numeric
        t = conversion.extract_time_string("PT-1H")
        self.assertEqual(t[0],"00:00:00")
        self.assertEqual(t[1], "Time value not numeric")
        t = conversion.extract_time_string("PTabH")
        self.assertEqual(t[0],"00:00:00")
        self.assertEqual(t[1], "Time value not numeric")
        t = conversion.extract_time_string("PTaH")
        self.assertEqual(t[0],"00:00:00")
        self.assertEqual(t[1], "Time value not numeric")
        # too large
        t = conversion.extract_time_string("PT60H")
        self.assertEqual(t[0],"00:00:00")
        self.assertEqual(t[1], "Time value out of bounds")
        # invalid number but fails length check
        t = conversion.extract_time_string("PT999M")
        self.assertEqual(t[0],"00:00:00")
        self.assertEqual(t[1], "Time string invalid length")

    def test_invalid_prefix(self):
        t = conversion.extract_time_string("Pz12H")
        self.assertEqual(t[0],"12:00:00")
        self.assertEqual(t[1], "*Time string starts invalid")
        t = conversion.extract_time_string("Pt28M")
        self.assertEqual(t[0],"00:28:00")
        self.assertEqual(t[1], "*Time string starts invalid")
        t = conversion.extract_time_string("zT40S")
        self.assertEqual(t[0],"00:00:40")
        self.assertEqual(t[1], "*Time string starts invalid")
        t = conversion.extract_time_string("pT7H")
        self.assertEqual(t[0],"07:00:00")
        self.assertEqual(t[1], "*Time string starts invalid")
        t = conversion.extract_time_string("ab52M")
        self.assertEqual(t[0],"00:52:00")
        self.assertEqual(t[1], "*Time string starts invalid")
        t = conversion.extract_time_string("cd1S")
        self.assertEqual(t[0],"00:00:01")
        self.assertEqual(t[1], "*Time string starts invalid")

class TestTimeAddition(unittest.TestCase):
    def test_valid(self):
        t = conversion.add_time_string("00:00:00", "01:00:00")
        self.assertEqual(t[0], "01:00:00")
        self.assertEqual(t[1], "")
        t = conversion.add_time_string("10:00:00", "00:00:00")
        self.assertEqual(t[0], "10:00:00")
        self.assertEqual(t[1], "")
        t = conversion.add_time_string("07:24:00", "01:48:00")
        self.assertEqual(t[0], "09:12:00")
        self.assertEqual(t[1], "")
        t = conversion.add_time_string("07:24:02", "01:48:59")
        self.assertEqual(t[0], "09:13:01")
        self.assertEqual(t[1], "")
        # adding to midnight - in this format up to 71:59:59 is supported
        t = conversion.add_time_string("23:58:00", "00:04:00")
        self.assertEqual(t[0], "24:02:00")
        self.assertEqual(t[1], "")
        t = conversion.add_time_string("12:24:02", "23:59:59")
        self.assertEqual(t[0], "36:24:01")
        self.assertEqual(t[1], "")

    def test_invalid_format(self):
        # initial time bad format - should return 00:00:00 and an error
        t = conversion.add_time_string("000000", "01:00:00")
        self.assertEqual(t[0], "00:00:00")
        self.assertEqual(t[1], "Initial Time: Time string invalid length")
        t = conversion.add_time_string("201000", "01:00:00")
        self.assertEqual(t[0], "00:00:00")
        self.assertEqual(t[1], "Initial Time: Time string invalid length")
        # addition time bad format – should return initial time and an error
        t = conversion.add_time_string("00:00:00", "010000")
        self.assertEqual(t[0], "00:00:00")
        self.assertEqual(t[1], "Journey Time: Time string invalid length")
        t = conversion.add_time_string("20:10:00", "010000")
        self.assertEqual(t[0], "20:10:00")
        self.assertEqual(t[1], "Journey Time: Time string invalid length")
        # both error, should return initial time with two error messages
        t = conversion.add_time_string("000000", "010000")
        self.assertEqual(t[0], "00:00:00")
        self.assertEqual(t[1], "Initial Time: Time string invalid length; Journey Time: Time string invalid length")
        t = conversion.add_time_string("201000", "010000")
        self.assertEqual(t[0], "00:00:00")
        self.assertEqual(t[1], "Initial Time: Time string invalid length; Journey Time: Time string invalid length")

        # bad time delimeter – should process as expected but with an error message
        # just initial error
        t = conversion.add_time_string("00-00-00", "01:00:00")
        self.assertEqual(t[0], "01:00:00")
        self.assertEqual(t[1], "Initial Time: Time string incorrect delimeter")
        t = conversion.add_time_string("20-10-00", "04:08:00")
        self.assertEqual(t[0], "24:18:00")
        self.assertEqual(t[1], "Initial Time: Time string incorrect delimeter")
        # just addition error
        t = conversion.add_time_string("00:00:00", "01-00-00")
        self.assertEqual(t[0], "01:00:00")
        self.assertEqual(t[1], "Journey Time: Time string incorrect delimeter")
        t = conversion.add_time_string("20:10:00", "04-08-00")
        self.assertEqual(t[0], "24:18:00")
        self.assertEqual(t[1], "Journey Time: Time string incorrect delimeter")
        # both error
        t = conversion.add_time_string("00-00-00", "01-00-00")
        self.assertEqual(t[0], "01:00:00")
        self.assertEqual(t[1], "Initial Time: Time string incorrect delimeter; Journey Time: Time string incorrect delimeter")
        t = conversion.add_time_string("20-10-00", "04-08-00")
        self.assertEqual(t[0], "24:18:00")
        self.assertEqual(t[1], "Initial Time: Time string incorrect delimeter; Journey Time: Time string incorrect delimeter")

    def test_invalid_valies(self):
        # non-numeric values
        # initial
        t = conversion.add_time_string("a0:00:00", "01:00:00")
        self.assertEqual(t[0], "00:00:00")
        self.assertEqual(t[1], "Initial Time: Time value not numeric")
        t = conversion.add_time_string("ab:cd:ef", "04:08:00")
        self.assertEqual(t[0], "00:00:00")
        self.assertEqual(t[1], "Initial Time: Time value not numeric")

        # addition
        t = conversion.add_time_string("20:00:00", "0a:00:00")
        self.assertEqual(t[0], "20:00:00")
        self.assertEqual(t[1], "Journey Time: Time value not numeric")
        t = conversion.add_time_string("18:24:11", "ab:cd:ef")
        self.assertEqual(t[0], "18:24:11")
        self.assertEqual(t[1], "Journey Time: Time value not numeric")

        # both (but gets picked up as initial)
        t = conversion.add_time_string("a0:00:00", "01:b0:00")
        self.assertEqual(t[0], "00:00:00")
        self.assertEqual(t[1], "Initial Time: Time value not numeric; Journey Time: Time value not numeric")
        t = conversion.add_time_string("ab:cd:ef", "a4:b0:cd")
        self.assertEqual(t[0], "00:00:00")
        self.assertEqual(t[1], "Initial Time: Time value not numeric; Journey Time: Time value not numeric")

        
# class TestConversion(unittest.TestCase):
    

#     def test_stops_processing(self):
#         print("stops processing")

#     def test_stop_times_processing(self):
#         print("stop times processing")

#     def test_calendar_processing(self):
#         print("calendar processing")


# class TestUtilities(unittest.TestCase):
#     def test_time_string(self):
#         print("time string")

#     def test_add_time_string(self):
#         print("add time string")

#     def test_decode_days(self):
#         print("decode days")

#     def test_get_dates(self):
#         print("get dates")

#     def test_holidays(self):
#         print("holidays")

if __name__ == "__main__":
    unittest.main()


