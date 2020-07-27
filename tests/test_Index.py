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

        self.mock_5_mg_config = Mock(spec=CalcConfig)
        self.mock_5_mg_config.unit = "mg"
        self.mock_5_mg_config.interval = 5

    # TODO (konrad.pagacz@gmail.com) write tests for indices for non nan array
    # TODO (konrad.pagacz@gmail.com) write tests for indices for nan array

    def test_mean_mg(self):
        mean = indices.GVMean(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(mean.calculate(), 3)

    def test_median_mg(self):
        median = indices.GVMedian(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(median.calculate(), 3)

    