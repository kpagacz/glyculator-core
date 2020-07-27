import unittest
from mock import Mock

import numpy as np
import pandas as pd 

import src.Index as indices
from src.utils import DT, GLUCOSE
from src.configs import CalcConfig


class TestGVIndices(unittest.TestCase):
    def setUp(self):
        dates = pd.date_range(start="27-07-2020 12:00", end="29-07-2020 12:00", freq="5min"),

        self.non_nan_df = pd.DataFrame({
            DT : dates,
            GLUCOSE : np.random.uniform(100, 20, len(dates))
            })

        self.simple_df = pd.DataFrame({
            DT : pd.date_range(start="27-07-2020 12:00", end="27-07-2020 12:20", freq="5min"),
            GLUCOSE : [1, 2, 3, 4, 5]
        })

        self.simple_nan_df = pd.DataFrame({
            DT : pd.date_range(start="27-07-2020 12:00", end="27-07-2020 12:20", freq="5min"),
            GLUCOSE : [1, 2, 3, np.nan, 5]
        })

        self.mock_5_mg_config = Mock(spec=CalcConfig)
        self.mock_5_mg_config.unit = "mg"
        self.mock_5_mg_config.interval = 5

    # TODO (konrad.pagacz@gmail.com) write tests for indices for non nan array
    # TODO (konrad.pagacz@gmail.com) write tests for indices for nan array

    def test_mean_mg(self):
        mean = indices.GVMean(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(mean.calculate(), 3)

    def test_mean_nan_mg(self):
        mean = indices.GVMean(df=self.simple_nan_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(mean.calculate(), 2.75)

    def test_median_mg(self):
        median = indices.GVMedian(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(median.calculate(), 3)

    def test_median_nan_mg(self):
        index = indices.GVMedian(df=self.simple_nan_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(index.calculate(), 2.5)

    def test_variance_mg(self):
        index = indices.GVVariance(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(index.calculate(), 2)

    def test_variance_nan_mg(self):
        index = indices.GVVariance(df=self.simple_nan_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(index.calculate(), 2.1875)

    def test_nan_fraction(self):
        index = indices.GVNanFraction(df=self.simple_nan_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(index.calculate(), 1 / 5)

    def test_records_no_mg(self):
        index = indices.GVRecordsNo(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(index.calculate(), 5)

    def test_records_no_nan_mg(self):
        index = indices.GVRecordsNo(df=self.simple_nan_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(index.calculate(), 5)

    def test_std_mg(self):
        index = indices.GVstd(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(index.calculate(), 1.4142135623)     

    def test_std_nan_mg(self):
        index = indices.GVstd(df=self.simple_nan_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(index.calculate(), 1.479019945)

    def test_mage_moving_average_arr_not_series(self):
        index = indices.GVmage(df=self.simple_df, calc_config=self.mock_5_mg_config)
        arr = [1, 3, 4, 6, 7]
        window_size = 2
        with self.assertRaises(ValueError):
            index._moving_average(arr, window_size)

    def test_mage_moving_average_window_not_int(self):
        index = indices.GVmage(df=self.simple_df, calc_config=self.mock_5_mg_config)
        arr = pd.Series([1, 3, 4, 6, 7])
        window_size = "test"
        with self.assertRaises(ValueError):
            index._moving_average(arr, window_size)

    def test_mage_moving_average_simple_array(self):
        index = indices.GVmage(df=self.simple_df, calc_config=self.mock_5_mg_config)
        arr = pd.Series([1, 3, 4, 6, 7])
        window_size = 2
        self.assertTrue(np.array_equal(index._moving_average(arr, window_size),
            np.array([2, 3.5, 5, 6.5])))