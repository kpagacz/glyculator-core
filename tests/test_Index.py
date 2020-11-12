import unittest
import logging
import logging.config
from mock import Mock

import yaml
import numpy as np
import pandas as pd 

import glyculator.Index as indices
from glyculator.utils import DT, GLUCOSE
from glyculator.configs import CalcConfig

# TODO (konrad.pagacz@gmail.com) write tests for indices for non nan array
# TODO (konrad.pagacz@gmail.com) write tests for indices for nan array

# logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler()])
logger = logging.getLogger()

class TestGVIndices(unittest.TestCase):
    def setUp(self):
        dates = pd.date_range(start="27-07-2020 12:00", end="29-07-2020 12:00", freq="5min"),
        
        # Logging setup
        # with open("logging_config.yaml", 'rt') as config:
        #     cfg = yaml.safe_load(config.read())
        #     logging.config.dictConfig(cfg)

        self.logger = logger

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
        self.mock_5_mg_config.mage_excursion_threshold = "sd"
        self.mock_5_mg_config.mage_moving_average_window_size = 9
        self.mock_5_mg_config.mage_peak_distance = 10

        self.mock_5_mmol_config = Mock(spec=CalcConfig)
        self.mock_5_mmol_config.unit = "mmol"
        self.mock_5_mmol_config.interval = 5


    def test_auc_simple_df_mg(self):
        # test on a df with all 1s
        self.simple_df[GLUCOSE] = len(self.simple_df) * [1]
        index = indices.GVauc(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(index.calculate(standardize=True), 5)

    def test_auc_simple_df_no_stand(self):
        # test on a df with all 1s
        self.simple_df[GLUCOSE] = len(self.simple_df) * [1]
        index = indices.GVauc(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(index.calculate(standardize=False), 20)

    def test_hypo_events_count_threshold_not_int(self):
        index = indices.GVhypo_events_count(df=self.simple_df, calc_config=self.mock_5_mg_config)
        with self.assertRaises(ValueError):
            index.calculate(threshold="test")

    def test_hypo_events_count_threshold_duration_not_int(self):
        index = indices.GVhypo_events_count(df=self.simple_df, calc_config=self.mock_5_mg_config)
        with self.assertRaises(ValueError):
            index.calculate(threshold=0, threshold_duration="test")

    def test_hypo_events_count_simple_df(self):
        self.simple_df[GLUCOSE] = [1, 1, 3, 2, 2]
        index = indices.GVhypo_events_count(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(index.calculate(threshold=3, threshold_duration=10), 2)

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

    def test_cv(self):
        index = indices.GVCV(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(0.4714045207910317, index.calculate())

    def test_cv_nan(self):
        index = indices.GVCV(df=self.simple_nan_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(0.5378254348272379, index.calculate())

    def test_std_mg(self):
        index = indices.GVstd(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(index.calculate(), 1.4142135623)     

    def test_std_nan_mg(self):
        index = indices.GVstd(df=self.simple_nan_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(index.calculate(), 1.479019945)

    def test_mage_runtime_error(self):
        # integration test in fact
        self.simple_df = pd.DataFrame({
            DT : pd.date_range(start="27-07-2020 12:00", periods=50, freq="5min"),
            GLUCOSE : 50 * [100]
        })
        index = indices.GVmage(df=self.simple_df, calc_config=self.mock_5_mg_config)
        with self.assertRaises(RuntimeError):
            index.calculate()

    def test_mage_basic_df(self):
        # integration test in fact
        self.simple_df = pd.DataFrame({
            DT : pd.date_range(start="27-07-2020 12:00", periods=50, freq="5min"),
            GLUCOSE : 50 * [100]
        })
        self.simple_df.iloc[10, 1] = 50
        self.simple_df.iloc[20, 1] = 50
        self.simple_df.iloc[30, 1] = 300
        self.simple_df.iloc[40, 1] = 200
        index = indices.GVmage(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(
            first=index.calculate(),
            second=0
        )

    def test_mage_basic_df_2(self):
        # integration test in fact
        self.simple_df = pd.DataFrame({
            DT : pd.date_range(start="27-07-2020 12:00", periods=50, freq="5min"),
            GLUCOSE : 50 * [100]
        })
        self.simple_df.iloc[10, 1] = 50
        self.simple_df.iloc[20, 1] = 50
        self.simple_df.iloc[30, 1] = 300
        self.simple_df.iloc[40, 1] = 200
        self.mock_5_mg_config.mage_excursion_threshold = "half_sd"
        index = indices.GVmage(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(
            first=index.calculate(),
            second=25
        )

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

    def test_mage_join_extremas_maximas_first(self):
        index = indices.GVmage(df=self.simple_df, calc_config=self.mock_5_mg_config)
        minimas = [2, 4, 6]
        maximas = [1, 3, 5]
        self.assertListEqual(
            list1=[1, 2, 3, 4, 5, 6],
            list2=index._join_extremas(minimas, maximas)
        )

    def test_mage_join_extremas_minimas_first(self):
        index = indices.GVmage(df=self.simple_df, calc_config=self.mock_5_mg_config)
        minimas = [1, 3, 5]
        maximas = [2, 4, 6]
        self.assertListEqual(
            list1=[1, 2, 3, 4, 5, 6],
            list2=index._join_extremas(minimas, maximas)
        )

    def test_mage_join_extremas_minimas_doubled(self):
        index = indices.GVmage(df=self.simple_df, calc_config=self.mock_5_mg_config)
        minimas = [1, 3, 5]
        maximas = [2, 6]
        self.assertListEqual(
            list1=[1, 2, 3, 6],
            list2=index._join_extremas(minimas, maximas),
            msg="_join_extremas returned: {}, expected: {}".format(
                index._join_extremas(minimas, maximas),
                [1, 2, 3, 6],
            )
        )

    def test_modd_all_values_are_the_same(self):
        # Mean of daily differences should obviously return 0 for a measurement
        # made up of all the same values
        dates = pd.date_range("12:00 2020/09/11", periods=500, freq="5min")
        values = np.repeat(100, repeats=500)
        test_df = pd.DataFrame({GLUCOSE : values}, index=dates)
        index = indices.GVmodd(df=test_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(
            0,
            index.calculate(),
            msg="Returned: {}. Expected 0".format(index.calculate()),
        )

    def test_conga_all_values_the_same(self):
        # Variance should obviously be 0 for a measurement
        # made up of all the same values
        dates = pd.date_range("12:00 2020/09/11", periods=500, freq="5min")
        values = np.repeat(100, repeats=500)
        test_df = pd.DataFrame({GLUCOSE : values}, index=dates)
        index = indices.GVcongaX(df=test_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(
            0,
            index.calculate(2),
            msg="Returned: {}. Expected 0".format(index.calculate(2)),
        )

    def test_custom_conga_call(self):
        # Variance should obviously be 0 for a measurement
        # made up of all the same values
        dates = pd.date_range("12:00 2020/09/11", periods=500, freq="5min")
        values = np.repeat(100, repeats=500)
        test_df = pd.DataFrame({GLUCOSE : values}, index=dates)
        index = indices.GVcongaX(calc_config=self.mock_5_mg_config)
        index.df = test_df
        self.assertEqual(
            0,
            index(df=test_df, hours=2),
            msg="Returned: {}. Expected 0".format(index.calculate(2)),
        )

    def test_conga_calculate_hours_not_int(self):
        index = indices.GVcongaX(df=self.simple_df, calc_config=self.mock_5_mg_config)
        with self.assertRaises(ValueError):
            index.calculate(hours="not int")

    def test_conga_call_on_not_pandas(self):
        index = indices.GVcongaX(df=self.simple_df, calc_config=self.mock_5_mg_config)
        with self.assertRaises(ValueError):
            indices.GVcongaX.__call__(index, df="not pandas", hours=7)

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

    def test_modd_simple_examples(self):
        same_values = pd.DataFrame(
            {
                DT : pd.date_range(start="10/11/2020 12:00", periods=3 * 256, freq="5min"),
                GLUCOSE : 3 * 256 * [100],
            }
        )

        index = indices.GVmodd(df=same_values, calc_config=self.mock_5_mg_config)
        self.assertEqual(
            index.calculate(),
            0,
            msg="Expected 0 for the array of all equal values. Returned: {}\n".format(index.calculate())
        )


    def test_j_mg_simple_df(self):
        index = indices.GVj(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(first=index.calculate(), second=0.01948528137423856)

    def test_j_mg_simple_nan_df(self):
        index = indices.GVj(df=self.simple_nan_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(first=index.calculate(), second=0.01788460970176197)

    def test_hypoglycemia(self):
        index = indices.GVhypoglycemia(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(first=index.calculate(3), second=0.4)

    def test_hypoglycemia_wrong_threshold_type(self):
        index = indices.GVhypoglycemia(df=self.simple_df, calc_config=self.mock_5_mg_config)
        with self.assertRaises(ValueError):
            index.calculate("test")

    def test_hypoglycemia_custom_call(self):
        index = indices.GVhypoglycemia(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(
            index(df=self.simple_df, threshold=3),
            index.calculate(3)
        )

    def test_hypoglycemia_call_not_dataframe(self):
        index = indices.GVhypoglycemia(df=self.simple_df, calc_config=self.mock_5_mg_config)
        with self.assertRaises(ValueError):
            index("test", threshold=7)

    def test_hyperglycemia(self):
        index = indices.GVhyperglycemia(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(first=index.calculate(2), second=0.6)

    def test_hyperglycemia_wrong_threshold_type(self):
        index = indices.GVhyperglycemia(df=self.simple_df, calc_config=self.mock_5_mg_config)
        with self.assertRaises(ValueError):
            index.calculate("test")

    def test_hyperglycemia_custom_call(self):
        index = indices.GVhyperglycemia(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(
            index.calculate(2),
            index(df=self.simple_df, threshold=2)
        )     

    def test_hyperglycemia_call_not_dataframe(self):
        index = indices.GVhyperglycemia(df=self.simple_df, calc_config=self.mock_5_mg_config)
        with self.assertRaises(ValueError):
            index(df="test", threshold=7)

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

    def test_grade_hypo(self):
        self.simple_df[GLUCOSE] = len(self.simple_df) * [60]
        index = indices.GVgrade_hypo(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(first=index.calculate(), second=1)  

    def test_grade_hypo_mmol(self):
        self.simple_df[GLUCOSE] = len(self.simple_df) * [2]
        index = indices.GVgrade_hypo(df=self.simple_df, calc_config=self.mock_5_mmol_config)
        self.assertAlmostEqual(first=index.calculate(), second=1)  

    def test_grade_hyper(self):
        self.simple_df[GLUCOSE] = len(self.simple_df) * [200]
        index = indices.GVgrade_hyper(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(first=index.calculate(), second=1)      

    def test_grade_hyper_mmol(self):
        self.simple_df[GLUCOSE] = len(self.simple_df) * [15]
        index = indices.GVgrade_hyper(df=self.simple_df, calc_config=self.mock_5_mmol_config)
        self.assertAlmostEqual(first=index.calculate(), second=1)      

    def test_eA1c_simple_df(self):
        self.simple_df[GLUCOSE] = len(self.simple_df) * [100]
        index = indices.GVeA1c(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(first=index.calculate(), second=5.09752973287909)

    def test_eA1c_mmol_equal_mg(self):
        self.simple_df[GLUCOSE] = len(self.simple_df) * [100]
        simple_df_mmol = self.simple_df.copy()
        simple_df_mmol[GLUCOSE] = simple_df_mmol[GLUCOSE] / 18.02
        index_mg = indices.GVeA1c(df=self.simple_df, calc_config=self.mock_5_mg_config)
        index_mmol = indices.GVeA1c(df=simple_df_mmol, calc_config=self.mock_5_mmol_config)
        self.assertAlmostEqual(index_mg.calculate(), index_mmol.calculate(),
            msg="\neA1c based on mg: {}. eA1c based on mmol: {}\n".format(index_mg.calculate(), index_mmol.calculate()))

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

    def test_mean_hypo_event_duration_threshold_error(self):
        index = indices.GVmean_hypo_event_duration(df=self.simple_df, calc_config=self.mock_5_mg_config)
        with self.assertRaises(ValueError):
            index.calculate(threshold="wrong_type")
            
    def test_mean_hypo_event_duration_records_duration(self):
        index = indices.GVmean_hypo_event_duration(df=self.simple_df, calc_config=self.mock_5_mg_config)
        with self.assertRaises(ValueError):
            index.calculate(threshold=0, records_duration="wrong_type")

    def test_mean_hypo_event_duration_1(self):
        self.simple_df = pd.DataFrame({
            DT : pd.date_range(start="27-07-2020 12:00", periods=8, freq="5min"),
            GLUCOSE : [10, 10, 10, 0, 0, 0, 0, 10]
        })
        index = indices.GVmean_hypo_event_duration(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(
            first=index.calculate(threshold=9, records_duration=15),
            second=20
        )

    def test_mean_hypo_event_duration_2(self):
        self.simple_df = pd.DataFrame({
            DT : pd.date_range(start="27-07-2020 12:00", periods=8, freq="5min"),
            GLUCOSE : [10, 10, 10, 0, 0, 0, 10, 10]
        })
        index = indices.GVmean_hypo_event_duration(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(
            first=index.calculate(threshold=9, records_duration=15),
            second=15
        )

    def test_mean_hypo_event_duration_no_hypo(self):
        self.simple_df = pd.DataFrame({
            DT : pd.date_range(start="27-07-2020 12:00", periods=8, freq="5min"),
            GLUCOSE : [10, 10, 10, 0, 0, 10, 10, 10]
        })
        index = indices.GVmean_hypo_event_duration(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertEqual(
            first=index.calculate(threshold=9, records_duration=15),
            second=0
        )

    def test_lbgi(self):
        index = indices.GVlbgi(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(
            first=567.362808824868,
            second=index.calculate()
        )

    def test_hbgi(self):
        index = indices.GVhbgi(df=self.simple_df, calc_config=self.mock_5_mg_config)
        self.assertAlmostEqual(
            first=0,
            second=index.calculate()
        )

class TestBaseGVIndex(unittest.TestCase):
    def setUp(self):
        dates = pd.date_range(start="27-07-2020 12:00", end="29-07-2020 12:00", freq="5min"),
        
        # Logging setup
        # with open("logging_config.yaml", 'rt') as config:
        #     cfg = yaml.safe_load(config.read())
        #     logging.config.dictConfig(cfg)

        self.logger = logging.getLogger(__name__)

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

    def test_calculate_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            indices.GVIndex(df=self.simple_df, calc_config=self.mock_5_mg_config).calculate()

    def test_set_df_not_pandas(self):
        with self.assertRaises(ValueError):
            indices.GVIndex(df="test", calc_config=self.mock_5_mg_config)

    def test_call_df_not_pandas(self):
        with self.assertRaises(ValueError):
            test_ind = indices.GVIndex(df=self.simple_df, calc_config=self.mock_5_mg_config)
            indices.GVIndex.__call__(test_ind, df="test")

    def test_set_calc_config_not_calcconfig(self):
        with self.assertRaises(ValueError):
            indices.GVIndex(df=self.simple_df, calc_config="wrong_class")

    def test_call_self_calculate_on_call(self):
        with self.assertRaises(NotImplementedError):
            base_index = indices.GVIndex(calc_config=self.mock_5_mg_config)
            base_index(self.simple_df)
