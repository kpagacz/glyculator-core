import src.configs as configs
import unittest


class TestReadConfig(unittest.TestCase):
    def setUp(self):
        self.config = configs.ReadConfig()
        self.not_int = "test"
        self.negative = -7

    def test_validate_non_negative(self):
        with self.assertRaises(ValueError):
            self.config.validateNonnegative(self.not_int)

        with self.assertRaises(ValueError):
            self.config.validateNonnegative(self.negative)

    def test_set_header_skip_error(self):
        with self.assertRaises(ValueError):
            self.config.set_header_skip(self.not_int)

        with self.assertRaises(ValueError):
            self.config.set_header_skip(self.negative)

    def test_set_date_column(self):
        with self.assertRaises(ValueError):
            self.config.set_date_column(self.not_int)

        with self.assertRaises(ValueError):
            self.config.set_date_column(self.negative)

    def test_set_date_time_columns(self):
        with self.assertRaises(ValueError):
            self.config.set_date_time_column(self.not_int)

        with self.assertRaises(ValueError):
            self.config.set_date_time_column(self.negative)

    def test_set_time_column(self):
        with self.assertRaises(ValueError):
            self.config.set_time_column(self.not_int)

        with self.assertRaises(ValueError):
            self.config.set_time_column(self.negative)

    def test_set_glucose_values_column(self):
        with self.assertRaises(ValueError):
            self.config.set_glucose_values_column(self.not_int)

        with self.assertRaises(ValueError):
            self.config.set_glucose_values_column(self.negative)

    def test_validate_logic(self):
        # No glucose column
        self.assertFalse(
            configs.ReadConfig(
                header_skip=0,
                date_time_column=0,
                date_column=0,
                time_column=0,
                glucose_values_column=None).validate(),
            msg="Expected False on missing glucose column number."
        )

        # No header skip
        self.assertFalse(
            configs.ReadConfig(
                header_skip=None,
                date_time_column=0,
                date_column=0,
                time_column=0,
                glucose_values_column=0).validate(),
            msg="Expected False on missing header skip number."
        )

        # No date-time but date and time ok
        self.assertTrue(
            configs.ReadConfig(
                header_skip=0,
                date_time_column=None,
                date_column=0,
                time_column=0,
                glucose_values_column=0).validate(),
            msg="Expected True on missing date-time column number."
        )

        # No date nor time but date time ok
        self.assertTrue(
            configs.ReadConfig(
                header_skip=0,
                date_time_column=0,
                date_column=None,
                time_column=None,
                glucose_values_column=0).validate(),
            msg="Expected True on missing date and time column number."
        )

        # No date-time and no date
        self.assertFalse(
            configs.ReadConfig(
                header_skip=0,
                date_time_column=None,
                date_column=None,
                time_column=0,
                glucose_values_column=0).validate(),
            msg="Expected False on missing date-time and date number."
        )


        # No date-time and no time
        self.assertFalse(
            configs.ReadConfig(
                header_skip=0,
                date_time_column=None,
                date_column=0,
                time_column=None,
                glucose_values_column=0).validate(),
            msg="Expected False on missing date-time and time column number."
        )

        # Everything ok
        self.assertTrue(
            configs.ReadConfig(
                header_skip=0,
                date_time_column=0,
                date_column=0,
                time_column=0,
                glucose_values_column=0).validate(),
            msg="Expected True on everything present."
        )