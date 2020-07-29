import unittest
import logging
import logging.config
from mock import Mock

import yaml
import numpy as np
import pandas as pd 

import src.Index as indices
from src.utils import DT, GLUCOSE
from src.configs import CalcConfig

# TODO (konrad.pagacz@gmail.com) write tests for indices for non nan array
# TODO (konrad.pagacz@gmail.com) write tests for indices for nan array

class TestGVIndices(unittest.TestCase):
    def setUp(self):
        dates = pd.date_range(start="27-07-2020 12:00", end="29-07-2020 12:00", freq="5min"),
        
        # Logging setup
        # with open("logging_config.yaml", 'rt') as config:
        #     cfg = yaml.safe_load(config.read())
        #     logging.config.dictConfig(cfg)

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler)

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

        self.mock_5_mmol_config = Mock(spec=CalcConfig)
        self.mock_5_mmol_config.unit = "mmol"
        self.mock_5_mmol_config.interval = 5



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

    def test_mage_join_extremas_util(self):
        index = indices.GVmage(df=self.simple_df, calc_config=self.mock_5_mg_config)
        minimas = [1, 3, 5]
        maximas = [2, 4, 6]
        joined = [1]
        minimas_turn = False
        index._join_extremas_util(joined, minimas, maximas, 1, 0, minimas_turn)
        self.assertListEqual(
            list1=[1, 2, 3, 4, 5, 6],
            list2=joined
        )

    def test_mage_join_extremas_util_different_lengths_arrays(self):
        index = indices.GVmage(df=self.simple_df, calc_config=self.mock_5_mg_config)
        minimas = [1, 3, 5]
        maximas = [2, 4, 6, 7]
        joined = [1]
        minimas_turn = False
        index._join_extremas_util(joined, minimas, maximas, 1, 0, minimas_turn)
        self.assertListEqual(
            list1=[1, 2, 3, 4, 5, 6],
            list2=joined
        )

    def test_mage_join_extremas_util_maximas_first(self):
        index = indices.GVmage(df=self.simple_df, calc_config=self.mock_5_mg_config)
        minimas = [2, 4, 6]
        maximas = [1, 3, 5]
        joined = [1]
        minimas_turn = True
        index._join_extremas_util(joined, minimas, maximas, 0, 1, minimas_turn)
        self.assertListEqual(
            list1=[1, 2, 3, 4, 5, 6],
            list2=joined
        )

    def test_mage_join_extremas(self):
        index = indices.GVmage(df=self.simple_df, calc_config=self.mock_5_mg_config)
        minimas = [2, 4, 6]
        maximas = [1, 3, 5]
        self.assertListEqual(
            list1=[1, 2, 3, 4, 5, 6],
            list2=index._join_extremas(minimas, maximas)
        )

    def test_m100_mg_simple_df(self):
        index = indices.GVm100(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(first=1584.16375079, second=index.calculate())

    def test_m100_mmol_simple_df(self):
        index = indices.GVm100(df=self.simple_df, calc_config=self.mock_5_mmol_config)
        self.assertAlmostEqual(first=328.891245687168, second=index.calculate())

    def test_m100_mg_all_100(self):
        self.simple_df[GLUCOSE] = len(self.simple_df) * [100]
        index = indices.GVm100(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(first=index.calculate(), second=0)

    def test_m100_mmol_all_100_div_by_18(self):
        self.simple_df[GLUCOSE] = len(self.simple_df) * [100 / 18]
        index = indices.GVm100(df=self.simple_df, calc_config=self.mock_5_mmol_config)
        self.assertEqual(first=index.calculate(), second=0)

    def test_j_mg_simple_df(self):
        index = indices.GVj(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(first=index.calculate(), second=0.01948528137423856)

    def test_j_mg_simple_nan_df(self):
        index = indices.GVj(df=self.simple_nan_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(first=index.calculate(), second=0.01788460970176197)

    def test_hypoglycemia(self):
        index = indices.GVhypoglycemia(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(first=index.calculate(3), second=0.4)

    def test_hyperglycemia(self):
        index = indices.GVhyperglycemia(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(first=index.calculate(2), second=0.6)

    def test_grade_simple_df_mg(self):
        self.simple_df[GLUCOSE] = len(self.simple_df) * [90]
        index = indices.GVgrade(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(first=index.calculate(), second=1.85253450028268)

    def test_grade_simple_df_mmol(self):
        self.simple_df[GLUCOSE] = len(self.simple_df) * [4.96]
        index = indices.GVgrade(df=self.simple_df, calc_config=self.mock_5_mmol_config)
        self.assertAlmostEqual(first=index.calculate(), second=1.9530397248653468)

    def test_grade_high_glucose_mg(self):
        self.simple_df[GLUCOSE] = len(self.simple_df) * [200]
        index = indices.GVgrade(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(first=index.calculate(), second=2.80635255992405)

    def test_eA1c_simple_df(self):
        self.simple_df[GLUCOSE] = len(self.simple_df) * [100]
        index = indices.GVeA1c(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(first=index.calculate(), second=5.09752973287909)

    def test_time_in_range_simple_df(self):
        index = indices.GVtime_in_range(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(index.calculate(lower_bound=1, upper_bound=5), 0.6)

    def test_time_in_range_value_error(self):
        index = indices.GVtime_in_range(df=self.simple_df, calc_config=self.mock_5_mg_config)
        with self.assertRaises(ValueError):
            index.calculate(lower_bound=1, upper_bound="test")

    def test_time_in_range_value_error2(self):
        index = indices.GVtime_in_range(df=self.simple_df, calc_config=self.mock_5_mg_config)
        with self.assertRaises(ValueError):
            index.calculate(lower_bound="test", upper_bound=1)  

    def test_time_in_range_accept_floats(self):
        index = indices.GVtime_in_range(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(
            index.calculate(lower_bound=1.0, upper_bound=5.0),
            0.6
        )

    def test_time_in_hypo(self):
        index = indices.GVtime_in_hypo(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(
            first=index.calculate(threshold=3),
            second=10
        )

    def test_time_in_hypo_value_error(self):
        index = indices.GVtime_in_hypo(df=self.simple_df, calc_config=self.mock_5_mg_config)
        with self.assertRaises(ValueError):
            index.calculate(threshold="test")

    