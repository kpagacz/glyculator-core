import unittest
from mock import Mock

import pandas as pd 
import numpy as np

from src.FileCleaner import FileCleaner
from src.utils import DT, GLUCOSE
import src.configs as configs

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
                    DT : ["2020-07-27 08:00:00", "2020-07-27 08:05:00"],
                    GLUCOSE : ["8", "8"],
                },
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
        should_be = should_be.drop(index=[2]).reset_index(drop=True)
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

    def test_fix_dates(self):
        long_df = pd.DataFrame({
            DT : pd.date_range("2020/08/18 19:00", "2020/08/18 22:00", freq="5min"),
            GLUCOSE : 37 * [80],
        })
        api_config = configs.CleanConfig(5, use_api="metronome")
        self.FileCleaner.set_clean_config(api_config)
        res = self.FileCleaner.fix_dates(long_df)
        
        np.testing.assert_allclose(
            res,
            np.array(37 * [1])
        )

    def test_fill_glucose_values_with_nearest(self):
        dates = pd.Series([
            "2020/08/18 12:00",
            "2020/08/18 12:05",
            "2020/08/18 12:10",
            "2020/08/18 12:11",
            "2020/08/18 12:15",
            "2020/08/18 12:20",
            "2020/08/18 12:25",
            "2020/08/18 12:29",
            "2020/08/18 12:30",
        ])
        dates = pd.to_datetime(dates)
        print(dates)

        glucose = pd.Series([1, 2, np.nan, 4, 5, 6, 7, 8, np.nan], dtype=np.float64)
        not_fixed = pd.DataFrame({DT : dates, GLUCOSE : glucose})
        not_fixed[GLUCOSE] = not_fixed[GLUCOSE].astype(np.float64)
        print(not_fixed)

        date_fixed = not_fixed.iloc[[0, 1, 2, 4, 5, 6, 8], :]
        print(date_fixed)

        fill_config = configs.CleanConfig(interval=5, use_api=False, fill_glucose_tolerance=2)
        self.FileCleaner.set_clean_config(fill_config)
        print(self.FileCleaner.clean_config.fill_glucose_tolerance)

        filled = self.FileCleaner._fill_glucose_values_with_nearest(date_fixed, not_fixed)
        print(filled)