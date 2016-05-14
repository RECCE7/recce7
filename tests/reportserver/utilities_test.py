import unittest
import sys
from reportserver.manager import utilities

# Unit tests for utililties.py

class Utilities_Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_validate_port_number(self):
        result = utilities.validate_port_number("200")
        self.assertEqual(200,result,"expected an integer of 200")

        result = utilities.validate_port_number("abc")
        self.assertEqual(None, result, "expected None")

        result = utilities.validate_port_number(str(sys.maxsize + 100))
        self.assertEqual(sys.maxsize + 100, result, "expected system maxsize + 100")

    def test_validate_time_period(self):
        result = utilities.validate_time_period(["days=1"])
        self.assertEqual(("days",1), result, "expected a tuple of days, 1")

        result = utilities.validate_time_period(["hours=10"])
        self.assertEqual(("hours", 10), result, "expected a tuple of hours, 10")

        result = utilities.validate_time_period(["minutes=10"])
        self.assertEqual(("minutes", 10), result, "expected a tuple of minutes, 10")

        result = utilities.validate_time_period(["weeks=10"])
        self.assertEqual(("weeks", 10), result, "expected a tuple of weeks, 10")

        result = utilities.validate_time_period(["days=1", "years=1"])
        self.assertEqual(("days", 1), result, "expected a tuple of days, 1")

        result = utilities.validate_time_period(["days=1", "weeks=10"])
        self.assertEqual(("days", 1), result, "expected a tuple of days, 1")

        result = utilities.validate_time_period(["weeks=10", "minutes=10"])
        self.assertEqual(("weeks", 10), result, "expected a tuple of weeks, 10")

        #the equal sign is missing...we should return None, None and give up.
        result = utilities.validate_time_period(["days1000"])
        self.assertEqual(("days", 1), result, "expected a tuple of days,1")

    def test_get_path_query_tokens(self):
        result = utilities.get_path_query_tokens("/v1/analytics/ports/23")
        answer = ( ["","v1","analytics","ports","23"],[] )
        self.assertSequenceEqual(answer, result, "expected: " + str(answer))

        result = utilities.get_path_query_tokens("/v1/analytics/ports/23?days=1")
        answer = (["", "v1", "analytics", "ports", "23"], ["days=1"])
        self.assertSequenceEqual(answer, result, "expected: " + str(answer))

        result = utilities.get_path_query_tokens("/v1/analytics/ports/23?days=1&minutes=100")
        answer = (["", "v1", "analytics", "ports", "23"], ["days=1","minutes=100"])
        self.assertSequenceEqual(answer, result, "expected: " + str(answer))

        result = utilities.get_path_query_tokens("/v1/analytics/ports/23?foo=bar&minutes=100")
        answer = (["", "v1", "analytics", "ports", "23"], ["foo=bar","minutes=100"])
        self.assertSequenceEqual(answer, result, "expected: " + str(answer))

        #the = sign is forgotten in the token
        result = utilities.get_path_query_tokens("/v1/analytics/ports/23?foobar")
        answer = (["", "v1", "analytics", "ports", "23"], ["foobar"])
        self.assertSequenceEqual(answer, result, "expected: " + str(answer))

    def test_setup_session_json(self):
        example_row = {'peerAddress': '127.0.0.1', 'user_input': 'hellow',
                       'session': 'f6cae8f0-5c61-4319-b357-1dcc20ab6fe4',
                       'localAddress': '127.0.0.1', 'input_type': 'username', 'ID': 1,
                       'eventDateTime': '2016-04-23T16:12:20.497293'}

        expected_json = {
            'begin_time': '2016-04-23T16:12:20.497293',
            'end_time': '2016-04-23T16:12:20.497293',
            'local_address': '127.0.0.1',
            'peer_address': '127.0.0.1',
            'session': 'f6cae8f0-5c61-4319-b357-1dcc20ab6fe4'
        }

        json_received = utilities.setup_session_json(example_row)

        self.assertEqual(json_received, expected_json)

    def test_get_date_delta(self):
        # one hour different
        test_iso_from = "1999-12-31T22:59:59"
        test_iso_to = "1999-12-31T23:59:59"
        expected_delta = "1:00:00"
        self.assertEqual(utilities.get_date_delta(test_iso_from, test_iso_to), expected_delta)

        # the same
        test_iso_from = "1999-12-31T22:59:59"
        test_iso_to = "1999-12-31T22:59:59"
        expected_delta = "0:00:00"
        self.assertEqual(utilities.get_date_delta(test_iso_from, test_iso_to), expected_delta)

        # seconds different
        test_iso_from = "1999-12-31T22:59:58"
        test_iso_to = "1999-12-31T22:59:59"
        expected_delta = "0:00:01"
        self.assertEqual(utilities.get_date_delta(test_iso_from, test_iso_to), expected_delta)

    def test_process_port_data_one_row(self):
        example_results = [{'peerAddress': '127.0.0.1', 'user_input': 'hello',
                            'session': 'f6cae8f0-5c61-4319-b357-1dcc20ab6fe4',
                            'localAddress': '127.0.0.1', 'input_type': 'username', 'ID': 1,
                            'eventDateTime': '2016-04-23T16:12:20.497293'}]

        json_expected = {
            'begin_time': '2016-04-23T16:12:20.497293',
            'end_time': '2016-04-23T16:12:20.497293',
            'local_address': '127.0.0.1',
            'peer_address': '127.0.0.1',
            'session': 'f6cae8f0-5c61-4319-b357-1dcc20ab6fe4',
            'duration': '0:00:00',
            'session_items': [{
                'peerAddress': '127.0.0.1',
                'user_input': 'hello',
                'session': 'f6cae8f0-5c61-4319-b357-1dcc20ab6fe4',
                'localAddress': '127.0.0.1',
                'input_type': 'username',
                'ID': 1,
                'eventDateTime': '2016-04-23T16:12:20.497293'
            }]
        }

        json_received = utilities.process_data(example_results)

        print("expected:" + str(json_expected))
        print("received:" + str(json_received))

        # self.assertListEqual(json_received['session_items'], json_expected['session_items'])
        self.assertEqual(len(json_received), 1)
        self.assertEqual(json_received[0]['begin_time'], json_expected['begin_time'])
        self.assertEqual(json_received[0]['end_time'], json_expected['end_time'])
        self.assertEqual(len(json_received[0]['session_items']), 1)
        self.assertDictEqual(json_received[0]['session_items'][0], json_expected['session_items'][0])

if __name__ == "__main__":
    unittest.main()