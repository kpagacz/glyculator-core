import src.configs as configs
import unittest 



class TestCalcConfig(unittest.TestCase):
    def setUp(self):
        self.config = configs.CalcConfig(interval=5)
        self.not_int = "wrong type"
        self.negative = -7
        self.not_int_str = lambda x : x


    def test_set_interval(self):
        with self.assertRaises(ValueError):
            self.config.set_interval(self.not_int)

    def test_set_unit(self):
        with self.assertRaises(ValueError):
            self.config.set_unit(self.not_int)

    def test_set_excursion_threshold(self):
        with self.assertRaises(ValueError):
            self.config.set_excursion_threshold(self.not_int_str)

        with self.assertRaises(ValueError):
            self.config.set_excursion_threshold(self.negative)

        with self.assertRaises(ValueError):
            self.config.set_excursion_threshold(self.not_int)

        self.config.set_excursion_threshold(7)
        self.assertEqual(self.config.mage_excursion_threshold, 7)

    def test_set_mage_moving_average(self):
        with self.assertRaises(ValueError):
            self.config.set_mage_moving_average(self.not_int)

        with self.assertRaises(ValueError):
            self.config.set_mage_moving_average(self.negative)

    def test_set_mage_peak_distance(self):
        with self.assertRaises(ValueError):
            self.config.set_mage_peak_distance(self.not_int_str)

        with self.assertRaises(ValueError):
            self.config.set_mage_peak_distance(self.negative)