import unittest
from mock import Mock

import pandas as pd 
import numpy as np
import logging
import logging.config
import yaml

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

        # Logger setup
        # with open("logging_config.yaml", 'rt') as config:
        #     cfg = yaml.safe_load(config.read())
        #     logging.config.dictConfig(cfg)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.DEBUG)
        
        self.mock_config_5_false_api = Mock(spec=configs.CleanConfig)
        self.mock_config_5_false_api.interval = 5
        self.mock_config_5_false_api.use_api = False
        self.mock_config_5_false_api.fill_glucose_tolerance = 2


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

    def test_fix_dates_clean_config_int(self):
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

    def test_fill_glucose_values_with_nearest_clean_config_int(self):
        dates = pd.Series([
            "2020/08/18 12:00",
            "2020/08/18 12:01",
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

        glucose = pd.Series([np.nan, 1, 2, np.nan, 4, 5, 6, 7, 8, np.nan], dtype=np.float64)
        not_fixed = pd.DataFrame({DT : dates, GLUCOSE : glucose})
        not_fixed[GLUCOSE] = not_fixed[GLUCOSE].astype(np.float64)

        date_fixed = not_fixed.iloc[[0, 2, 3, 5, 6, 7, 9], :].copy()     

        fill_config = configs.CleanConfig(interval=5, use_api=False, fill_glucose_tolerance=2)
        self.FileCleaner.set_clean_config(fill_config)

        filled = self.FileCleaner._fill_glucose_values_with_nearest(date_fixed, not_fixed)
        
        expect = pd.DataFrame({
            DT : pd.date_range("2020-08-18 12:00:00", periods=7, freq="5min"),
            GLUCOSE : np.array([1,2,4,5,6,7,8], dtype=np.float),
        }, index=[0, 2, 3, 5, 6, 7, 9])

        self.assertTrue(filled.equals(expect))

    def test_fill_missing_dates_clean_config_int(self):
        dates = pd.Series([
            "2020/08/18 12:00",
            "2020/08/18 12:15",
            "2020/08/18 12:20",
            "2020/08/18 12:30",
        ])
        dates = pd.to_datetime(dates)
        glucose = pd.Series([0,1,2,3], dtype=np.float64)

        df = pd.DataFrame({DT : dates, GLUCOSE : glucose})

        # setup result of the method
        fill_config = configs.CleanConfig(interval=5, use_api=False, fill_glucose_tolerance=2)
        self.FileCleaner.set_clean_config(fill_config)
        filled = self.FileCleaner._fill_missing_dates(df)


        # setup expected result
        expect = pd.DataFrame({
            DT : pd.date_range("2020-08-18 12:00", periods=7, freq="5min"),
            GLUCOSE : [0.0, np.nan, np.nan, 1.0, 2.0, np.nan, 3.0],
        })

        self.assertTrue(filled.equals(expect), 
                        "\nMethod result:\n{}\nExpected:\n{}\n".format(filled, expect))

    def test_fill_missing_dates_shifted_clean_config_int(self):
        dates = pd.Series([
            "2020/08/18 12:00",
            "2020/08/18 12:16",
            "2020/08/18 12:21",
            "2020/08/18 12:31",
        ])
        dates = pd.to_datetime(dates)
        glucose = pd.Series([0,1,2,3], dtype=np.float64)
        df = pd.DataFrame({DT : dates, GLUCOSE : glucose})

        fill_config = configs.CleanConfig(interval=5, use_api=False, fill_glucose_tolerance=2)
        self.FileCleaner.set_clean_config(fill_config)

        filled = self.FileCleaner._fill_missing_dates(df)

        expect = pd.DataFrame({
            DT : pd.date_range("2020-08-18 12:00", periods=7, freq="5min"),
            GLUCOSE : [0.0, np.nan, np.nan, 1.0, 2.0, np.nan, 3.0]
        })

        self.assertTrue(filled.equals(expect),
                        "\nMethod result:\n{}\nExpected:\n{}\n".format(filled, expect))

    def test_tidy_simple_df_clean_config_int(self):
        # DF setup
        # couple of issues to solve in this dates
        dates = [
            "2020/08/18 12:00",
            "2020/08/18 12:05",
            "2020/08/18 12:05:01", # shift by 1sec 
            "2020/08/18 12:10:01",
            "2020/08/18 12:15:01",
            "2020/08/18 12:20:02", # another shift
            "2020/08/18 12:25:02",
            np.nan,                # nan
            "2020/08/18 12:30:02",
            "2020/08/18 12:35:02",
            "2020/08/18 12:35:57", # additional timepoints
            "2020/08/18 12:37:00",
            "2020/08/18 12:40:02",
            "2020/08/18 12:45:02",
            "2020/08/18 12:50:02",
            "2020/08/18 12:55:02",
            "2020/08/18 13:00:02",
            "2020/08/18 13:05:02",
            "2020/08/18 13:10:02",
            "2020/08/18 13:15:01",
            "2020/08/18 13:20:01",
            "2020/08/18 13:25",
            "2020/08/18 13:30",
            "2020/08/18 13:35",
            "2020/08/18 13:40",
            "2020/08/18 13:50",    # missing timepoint
            "2020/08/18 13:55",
            "2020/08/18 14:00",
            "2020/08/18 14:05",
            "2020/08/18 14:10",
            "2020/08/18 14:15",
            "2020/08/18 14:20",
            "2020/08/18 14:25",
            "2020/08/18 14:30",
            "2020/08/18 14:35",
            "2020/08/18 14:40",
        ]
        dates = pd.to_datetime(dates)

        glucose = np.array(len(dates) * [80], dtype=np.float)
        glucose[9] = np.nan

        df = pd.DataFrame({
            DT : dates,
            GLUCOSE : glucose,
        })

        # Clean config setup
        clean_config = configs.CleanConfig(interval=5, use_api="metronome",
                        fill_glucose_tolerance=2)
        cleaner = FileCleaner(df, clean_config)

        # Tidy!
        res = cleaner.tidy()

        # Expected setup
        expect_index = pd.date_range("2020-08-18 12:00", "2020-08-18 14:40", freq="5min")
        glucose = len(expect_index) * [80]
        glucose[7] = np.nan 
        glucose[21] = np.nan
        expect = pd.DataFrame({
            DT : expect_index,
            GLUCOSE : glucose,
        })

        self.assertTrue(res.equals(expect))
