import unittest
from mock import Mock

import pandas as pd 
import numpy as np

from src.FileCleaner import FileCleaner
from src.utils import DT, GLUCOSE

class TestFileCleaner(unittest.TestCase):
    def setUp(self):
        self.FileCleaner = FileCleaner()

    def test_clean_file_nan_as_empty_string(self):
        test_df = pd.DataFrame(
            {
                DT: ["2020-07-27 08:00:00", "", "2020-07-27 08:05:00"],
                GLUCOSE: ["8", "8", "8"]
            }
        )

        res = self.FileCleaner._clean_file(test_df)
        other = pd.DataFrame(
                {
                    GLUCOSE : ["8", "8"]
                },
                index=["2020-07-27 08:00:00", "2020-07-27 08:05:00"],
            )

        self.assertTrue(
            res.equals(other),
            msg="\nCleaned DF: {} \nExpected DF: {}".format(res, other)
        )

    def test_clean_no_df_supplied(self):
        self.FileCleaner.clean_config = Mock()
        with self.assertRaises(RuntimeError):
            self.FileCleaner.tidy()

    def test_clean_no_clean_config(self):
        self.FileCleaner.untidy = Mock()
        with self.assertRaises(RuntimeError):
            self.FileCleaner.tidy()

    def test_set_untidy_non_df(self):
        with self.assertRaises(ValueError):
            self.FileCleaner.set_untidy("test")

    def test_set_untidy_df_example_1(self):
        test_df = pd.DataFrame({"Test": [1, 2]})
        self.FileCleaner.set_untidy(test_df)
        self.assertTrue(test_df.equals(self.FileCleaner.untidy))

    def test_set_clean_config_config_wrong_type(self):
        with self.assertRaises(ValueError):
            self.FileCleaner.set_clean_config("Test")

    