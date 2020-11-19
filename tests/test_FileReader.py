from datetime import datetime

import unittest
from unittest.mock import patch, Mock

import pandas as pd

from glyculator import FileReader
from glyculator.utils import DATE, TIME, DT, GLUCOSE
from glyculator.configs import ReadConfig

import logging
import logging.config
import yaml

class TestFileReader(unittest.TestCase):
    def setUp(self):
        self.FileReader = FileReader()

        # Logging setup
        with open("logging_config.yaml", "rt") as file:
            cfg = yaml.safe_load(file)
            logging.config.dictConfig(cfg)

        
        # Mock config
        self.mock_config = Mock(spec=ReadConfig)
        self.mock_config.header_skip = 0
        self.mock_config.date_time_column = 0
        self.mock_config.date_column = 0
        self.mock_config.time_column = 0
        self.mock_config.glucose_values_column = 0

    def test_validate_file_type_not_accepted(self):
        self.FileReader.extension = "test"
        self.assertFalse(self.FileReader.validate_file_type(),
            "Expected extension not to be in accepted.")

    def test_validate_file_type_accepted_csv(self):
        self.FileReader.extension = "csv"
        self.assertTrue(self.FileReader.validate_file_type())
    
    def test_validate_file_type_accepted_tsv(self):
        self.FileReader.extension = "tsv"
        self.assertTrue(self.FileReader.validate_file_type())

    def test_validate_file_type_accepted_txt(self):
        self.FileReader.extension = "txt"
        self.assertTrue(self.FileReader.validate_file_type())

    def test_validate_file_type_delimited_csv(self):
        self.FileReader.extension = "csv"
        self.FileReader.validate_file_type()
        self.assertTrue(self.FileReader.delimited)

    def test_validate_file_type_delimited_tsv(self):
        self.FileReader.extension = "tsv"
        self.FileReader.validate_file_type()
        self.assertTrue(self.FileReader.delimited)

    def test_validate_file_type_delimited_txt(self):
        self.FileReader.extension = "txt"
        self.FileReader.validate_file_type()
        self.assertTrue(self.FileReader.delimited)

    def test_merge_date_and_time_not_lists(self):
        test_dict1 = {
            TIME: "test",
            DATE: []
        }
        
        test_dict2 = {
           TIME: [],
           DATE: "test" 
        }

        with self.assertRaises(ValueError):
            self.FileReader.merge_date_and_time(test_dict1)

        with self.assertRaises(ValueError):
            self.FileReader.merge_date_and_time(test_dict2)

    def test_set_config(self):
        self.FileReader.set_config(self.mock_config)
        self.assertEqual(
            self.FileReader.read_config,
            self.mock_config
        )

    def test_set_config_wrong_argument(self):
        with self.assertRaises(ValueError):
            self.FileReader.set_config("TEST")

    def test_substring_extension(self):
        self.FileReader.set_file_name("test_name.test")
        self.FileReader.substring_extension()
        self.assertEqual(self.FileReader.extension, "test")

    def test_substring_extension_none(self):
        self.FileReader.set_file_name(None)
        self.FileReader.substring_extension()
        self.assertEqual(self.FileReader.extension, None)

    def test_substring_extension_on_init(self):
        new_reader = FileReader("test.ext")
        self.assertEqual(new_reader.extension, "ext")

    def test_read_file_no_config_exception(self):
        self.FileReader.read_config = None
        with self.assertRaises(TypeError):
            self.FileReader.read_file()

    def test_read_file_no_file_name_exception(self):
        self.FileReader.read_config = "mock"
        self.FileReader.file_name = None
        with self.assertRaises(TypeError):
            self.FileReader.read_file()

    def test_read_file_bad_extension_exception(self):
        self.FileReader.read_config = "mock"
        self.FileReader.file_name = "Mock"
        self.FileReader.extension = "test"
        with self.assertRaises(ValueError):
            self.FileReader.read_file()

    @patch("os.path")
    def test_read_file_not_found_exception(self, mock_path):
        mock_path.isfile.return_value = False
        self.FileReader.read_config = "mock"
        self.FileReader.file_name = "Mock"
        self.FileReader.extension = "csv"
        with self.assertRaises(FileNotFoundError):
            self.FileReader.read_file()

    @patch("os.path")
    def test_read_file_config_validation_false(self, mock_path):
        mock_path.isfile.return_value = True
        mock_read_config = Mock()
        mock_read_config.validate.return_value = False
        self.FileReader.read_config = mock_read_config
        self.FileReader.file_name = "Mock"
        self.FileReader.extension = "csv"
        with self.assertRaises(ValueError):
            self.FileReader.read_file()

    @patch("os.path")
    def test_read_file_delimited_call(self, mock_path):
        # os.path mock config
        mock_path.isfile.return_value = True

        # self.read_config mock config
        mock_read_config = Mock()
        mock_read_config.validate.return_value = True
        self.FileReader.read_config = mock_read_config
        
        # self.read_delimited() mock config
        mock_read_delimited = Mock()
        self.FileReader.read_delimited = mock_read_delimited

        self.FileReader.file_name = "Mock"
        self.FileReader.extension = "csv"
        try:
            self.FileReader.read_file()
        except:
            pass
        finally:
            self.FileReader.read_delimited.assert_called()

    def test_read_file_delimited_set_to_true(self):
        self.FileReader.read_config = "Mock"
        self.FileReader.file_name = "test"
        self.FileReader.extension = "csv"
        try:
            self.FileReader.read_file()
        except:
            pass
        self.assertTrue(expr=self.FileReader.delimited, msg="Failed to set \
            delimited to True in read_file() via validate_file_type()")

    def test_read_file_delimited_stays_false(self):
        self.FileReader.read_config = "Mock"
        self.FileReader.file_name = "test"
        self.FileReader.extension = "xlsx"
        try:
            self.FileReader.read_file()
        except:
            pass
        self.assertFalse(expr=self.FileReader.delimited,
         msg="delimited set to true in read_file() when extenstion is xlsx")       
        
    def test_merge_date_and_time(self):
        now = datetime.now()
        test_dict = {
            TIME : [now],
            DATE : [now]
        }

        res = self.FileReader.merge_date_and_time(test_dict)
        self.assertEqual(res,
            {
                TIME : [now],
                DATE : [now],
                DT : [now],
            }
        )

    def test_lists_to_dict_dt_provided(self):
        data = [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]
        # mock setup
        self.mock_config.date_time_column = 0
        self.mock_config.glucose_values_column = 1
        self.FileReader.read_config = self.mock_config
        
        res = self.FileReader.lists_to_dict(data)
        
        self.assertDictEqual(
            d1={'date-time': [0, 5], 'glucose': [1, 6], 'date': [], 'time': []},
            d2=res
        )

    def test_lists_to_dict_no_dt(self):
        data = [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]
        # mock setup
        self.mock_config.date_time_column = None
        self.mock_config.date_column = 0
        self.mock_config.time_column = 1
        self.mock_config.glucose_values_column = 2
        self.FileReader.read_config = self.mock_config

        res = self.FileReader.lists_to_dict(data)

        self.assertDictEqual(
            d1={'date-time': [], 'glucose': [2, 7], 'date': [0, 5], 'time': [1, 6]},
            d2=res
        )

    def test_read_excel_example_1(self):
        file_name = "tests/test_files/excel-example1.xlsx"
        self.mock_config.date_time_column = 0
        self.mock_config.date_column = 2
        self.mock_config.time_column = 3
        self.mock_config.glucose_values_column = 1
        self.mock_config.header_skip = 2
        self.FileReader.read_config = self.mock_config
        self.FileReader.file_name = file_name

        res = self.FileReader.read_excel()
        expected = [['ID', '', '', ''], 
                    ['dt', 'glucose', 'date', 'time'], 
                    [datetime(2019, 8, 9, 8, 0), 78.0, '', ''], 
                    [datetime(2019, 8, 9, 8, 5), 80.0, '', ''], 
                    [datetime(2019, 8, 9, 8, 10), 83.0, '', ''], 
                    [datetime(2019, 8, 9, 8, 15), 79.0, '', '']]

        self.assertListEqual(
            res,
            expected
        )

    def test_read_excel_example_2(self):
        file_name = "tests/test_files/excel-example2.xlsx"
        self.mock_config.date_time_column = None
        self.mock_config.date_column = 2
        self.mock_config.time_column = 3
        self.mock_config.glucose_values_column = 1
        self.mock_config.header_skip = 2
        self.FileReader.read_config = self.mock_config
        self.FileReader.file_name = file_name

        res = self.FileReader.read_excel()
        expected = [['ID', '', '', ''], 
                    ['dt', 'glucose', 'date', 'time'], 
                    ['', 78.0, datetime(2019, 8, 9, 0, 0), datetime(1899, 12, 31, 8, 0)], 
                    ['', 80.0, datetime(2019, 8, 9, 0, 0), datetime(1899, 12, 31, 8, 5)],
                    ['', 83.0, datetime(2019, 8, 9, 0, 0), datetime(1899, 12, 31, 8, 10)], 
                    ['', 79.0, datetime(2019, 8, 9, 0, 0), datetime(1899, 12, 31, 8, 15)]]

        self.assertListEqual(
            res,
            expected
        )

    def test_read_excel_example_3(self):
        file_name = "tests/test_files/excel-example3.xlsx"
        self.mock_config.date_time_column = 0
        self.mock_config.date_column = 2
        self.mock_config.time_column = 3
        self.mock_config.glucose_values_column = 1
        self.mock_config.header_skip = 2
        self.FileReader.read_config = self.mock_config
        self.FileReader.file_name = file_name

        res = self.FileReader.read_excel()
        expected = [['ID', '', '', ''], 
                    ['dt', 'glucose', 'date', 'time'], 
                    [datetime(2019, 8, 9, 8, 0), 78.0, '', ''], 
                    [datetime(2019, 8, 9, 8, 5), 80.0, '', ''], 
                    ['', 83.0, '', ''], 
                    [datetime(2019, 8, 9, 8, 15), 79.0, '', '']]

        self.assertListEqual(
            res,
            expected
        )  

    def test_read_delimited_example_1(self):
        file_name = "tests/test_files/csv-example1.csv"
        self.mock_config.date_time_column = 0
        self.mock_config.date_column = 2
        self.mock_config.time_column = 3
        self.mock_config.glucose_values_column = 1
        self.mock_config.header_skip = 2
        self.FileReader.read_config = self.mock_config
        self.FileReader.file_name = file_name

        res = self.FileReader.read_delimited()
        expected = [['ID', '', '', ''], 
                    ['dt', 'glucose', 'date', 'time'], 
                    [datetime(2019, 8, 9, 8, 0), 78.0, '', ''], 
                    [datetime(2019, 8, 9, 8, 5), 80.0, '', ''], 
                    [datetime(2019, 8, 9, 8, 10), 83.0, '', ''], 
                    [datetime(2019, 8, 9, 8, 15), 79.0, '', '']]

        self.assertListEqual(
            res,
            expected,
            msg="List not equal:\n{}\n{}".format(res, expected)
        )  

    def test_read_delimited_example_2(self):
        file_name = "tests/test_files/csv-example2.csv"
        self.mock_config.date_time_column = None
        self.mock_config.date_column = 2
        self.mock_config.time_column = 3
        self.mock_config.glucose_values_column = 1
        self.mock_config.header_skip = 2
        self.FileReader.read_config = self.mock_config
        self.FileReader.file_name = file_name

        res = self.FileReader.read_delimited()
        expected = [['ID', '', '', '', '', ''], 
                    ['dt', 'glucose', 'date', 'time', '', ''], 
                    ['', 78.0, datetime(2019, 8, 9, 0, 0), datetime(1900, 1, 1, 8, 0), '', ''], 
                    ['', 80.0, datetime(2019, 8, 9, 0, 0), datetime(1900, 1, 1, 8, 5), '', ''], 
                    ['', 83.0, datetime(2019, 8, 9, 0, 0), datetime(1900, 1, 1, 8, 10), '', ''], 
                    ['', 79.0, datetime(2019, 8, 9, 0, 0), datetime(1900, 1, 1, 8, 15), '', '']]

        self.assertListEqual(
            res,
            expected,
            msg="List not equal:\n{}\n{}".format(res, expected)
        )

    def test_read_delimited_example_3(self):
        file_name = "tests/test_files/csv-example3.csv"
        self.mock_config.date_time_column = None
        self.mock_config.date_column = 2
        self.mock_config.time_column = 3
        self.mock_config.glucose_values_column = 1
        self.mock_config.header_skip = 2
        self.FileReader.read_config = self.mock_config
        self.FileReader.file_name = file_name

        res = self.FileReader.read_delimited()
        expected = [['ID', '', '', '', '', ''], 
                    ['dt', 'glucose', 'date', 'time', '', ''], 
                    ['', 78.0, datetime(2019, 8, 9, 0, 0), datetime(1900, 1, 1, 8, 0), '', ''], 
                    ['', 80.0, datetime(2019, 8, 9, 0, 0), datetime(1900, 1, 1, 8, 5), '', ''], 
                    ['', 83.0, datetime(2019, 8, 9, 0, 0), datetime(1900, 1, 1, 8, 10), '', ''], 
                    ['', 79.0, datetime(2019, 8, 9, 0, 0), datetime(1900, 1, 1, 8, 15), '', '']]

        self.assertListEqual(
            res,
            expected,
            msg="List not equal:\nRES\n{}\nEXPECTED\n{}".format(res, expected)
        )

    def test_read_file_excel_example_1(self):
        file_name = "tests/test_files/excel-example1.xlsx"
        self.mock_config.date_time_column = 0
        self.mock_config.date_column = 2
        self.mock_config.time_column = 3
        self.mock_config.glucose_values_column = 1
        self.mock_config.header_skip = 2
        self.mock_config.validate = Mock(return_value=True)
        self.FileReader.read_config = self.mock_config
        self.FileReader.file_name = file_name
        self.FileReader.validate_file_type = Mock(return_value=True)

        res = self.FileReader.read_file()
        expected = pd.DataFrame({
            DT : pd.date_range("2019-08-09 08:00:00", periods=4, freq="5min"),
            GLUCOSE : [78.0, 80.0, 83.0, 79.0],
        })
        
        self.assertTrue(res.equals(expected),
                        msg="Expected data frames to be equal: RES\n{}\nEXPECTED\n{}".format(res, expected))

    def test_read_file_excel_example_2(self):
        file_name = "tests/test_files/excel-example2.xlsx"
        self.mock_config.date_time_column = None
        self.mock_config.date_column = 2
        self.mock_config.time_column = 3
        self.mock_config.glucose_values_column = 1
        self.mock_config.header_skip = 2
        self.mock_config.validate = Mock(return_value=True)
        self.FileReader.read_config = self.mock_config
        self.FileReader.file_name = file_name
        self.FileReader.validate_file_type = Mock(return_value=True)

        res = self.FileReader.read_file()
        expected = pd.DataFrame({
            DT : pd.date_range("2019-08-09 08:00:00", periods=4, freq="5min"),
            GLUCOSE : [78.0, 80.0, 83.0, 79.0],
        })
        
        self.assertTrue(res.equals(expected),
                        msg="Expected data frames to be equal: RES\n{}\nEXPECTED\n{}".format(res, expected))

    def test_read_excel_example_empty(self):
        file_name = "tests/test_files/excel-example-empty.xlsx"
        self.mock_config.date_time_column = None
        self.mock_config.date_column = 2
        self.mock_config.time_column = 3
        self.mock_config.glucose_values_column = 1
        self.mock_config.header_skip = 2
        self.mock_config.validate = Mock(return_value=True)
        self.FileReader.read_config = self.mock_config
        self.FileReader.file_name = file_name
        self.FileReader.validate_file_type = Mock(return_value=True)

        with self.assertRaises(RuntimeError):
            self.FileReader.read_excel()

    def test_read_file_csv_example_1(self):  
        file_name = "tests/test_files/csv-example1.csv"
        self.mock_config.date_time_column = 0
        self.mock_config.date_column = 2
        self.mock_config.time_column = 3
        self.mock_config.glucose_values_column = 1
        self.mock_config.header_skip = 2
        self.mock_config.validate = Mock(return_value=True)
        self.FileReader.read_config = self.mock_config
        self.FileReader.file_name = file_name
        self.FileReader.delimited = True
        self.FileReader.validate_file_type = Mock(return_value=True)

        res = self.FileReader.read_file()
        expected = pd.DataFrame({
            DT : pd.date_range("2019-08-09 08:00:00", periods=4, freq="5min"),
            GLUCOSE : [78.0, 80.0, 83.0, 79.0],
        })
        
        self.assertTrue(res.equals(expected),
                        msg="Expected data frames to be equal: RES\n{}\nEXPECTED\n{}".format(res, expected))

