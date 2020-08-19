import unittest

from src.configs import CleanConfig
import src.utils as utils


class TestCleanConfig(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_wrong_interval(self):
        with self.assertRaises(ValueError):
            CleanConfig(7, False)

    def test_interval_not_int(self):
        with self.assertRaises(ValueError):
            CleanConfig("test", False)

    def test_api_port_not_int(self):
        with self.assertRaises(ValueError):
            CleanConfig(5, False, api_port="test")

    def test_api_dates_not_bool_and_not_str(self):
        with self.assertRaises(ValueError):
            CleanConfig(5, use_api=8)

    def test_api_address_not_str(self):
        with self.assertRaises(ValueError):
            CleanConfig(5, False, api_address=4)

    def test_api_endpoint_not_str(self):
        with self.assertRaises(ValueError):
            CleanConfig(5, False, api_endpoint=5)

    def test_construct_full_api_address(self):
        test_address = "http://testaddress"
        test_port = 5000
        test_endpoint = "test/endpoint"
        expected = "http://testaddress:5000/test/endpoint"

        self.assertEqual(
            CleanConfig(5, use_api=False, api_port=test_port, api_address=test_address, 
                        api_endpoint=test_endpoint)._construct_full_api_address(),
            expected
        )

    def test_set_api_metronome(self):
        metronome_config = CleanConfig(interval=5, use_api="metronome")

        self.assertEqual(metronome_config.api_address, utils.METRONOME_ADDRESS)
        self.assertEqual(metronome_config.api_port, utils.METRONOME_PORT)
        self.assertEqual(metronome_config.api_endpoint, utils.METRONOME_ENDPOINT)