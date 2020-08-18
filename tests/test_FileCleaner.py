import unittest
from mock import Mock

import pandas as pd 
import numpy as np

from src.FileCleaner import FileCleaner
from src.utils import DT, GLUCOSE

class TestFileCleaner(unittest.TestCase):
    def setUp(self):
        self.FileCleaner = FileCleaner()
        self.simple_df = pd.DataFrame({
            DT : pd.date_range(start="2020-07-29 12:00", end="2020-07-29 12:25", freq="5min"),
            GLUCOSE : np.random.uniform(low=50, high=150, size=6)
        })

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

    def test_clean_file_simple_df(self):
        self.simple_df.iloc[2, 0] = ""
        self.simple_df.iloc[3, 1] = ""
        cleaned = self.FileCleaner._clean_file(self.simple_df)
        should_be = self.simple_df
        should_be.iloc[3, 1] = np.nan
        should_be = should_be.drop(index=[2]).set_index(DT, drop=True)
        should_be[GLUCOSE] = should_be[GLUCOSE].astype(np.float64)
        pd.testing.assert_frame_equal(
            left=cleaned,
            right=should_be,
            check_exact=False,
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

    def test_tidy_no_dataframe(self):
        with self.assertRaises(RuntimeError):
            self.FileCleaner.clean_config = Mock()
            self.FileCleaner.tidy()

    def test_tidy_no_clean_config(self):
        with self.assertRaises(RuntimeError):
            self.FileCleaner.clean_config = Mock()
            self.FileCleaner.tidy()
    
    def test_replace_empty_strings_with_nans_error_replacing(self):
        mock_df = Mock()
        mock_df.replace.side_effect = Exception
        with self.assertRaises(RuntimeError):
            self.FileCleaner._replace_empty_strings_with_nans(mock_df)

    def test_replace_empty_strings_with_nans(self):
        test_df = pd.DataFrame({"var1": ["", 1, 2], "var2" : [1, "", 2]})
        replaced = self.FileCleaner._replace_empty_strings_with_nans(test_df)
        self.assertTrue(replaced.equals(
            pd.DataFrame({"var1": [np.nan, 1, 2], "var2" : [1, np.nan, 2]})
        ))