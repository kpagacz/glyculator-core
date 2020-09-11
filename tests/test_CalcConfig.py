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

    def test_set_tir_range_not_tuple(self):
        with self.assertRaises(ValueError):
            self.config.set_tir_range("test")

    def test_set_tir_range_first_not_float(self):
        with self.assertRaises(ValueError):
            self.config.set_tir_range(("test", 1))

    def test_set_tir_range_second_not_float(self):
        with self.assertRaises(ValueError):
            self.config.set_tir_range((1, "test"))

    def test_set_tir_range_first_greater_than_second(self):
        with self.assertRaises(ValueError):
            self.config.set_tir_range((2, 1))