import unittest 
import pandas as pd 
import numpy as np 
import json
import mock
import requests


import src.DateFixer as DateFixer
import src.configs as configs
from src.cleaner.config import WINDOW_SIZE
import src.utils as utils

def logDict(dictionary):
    for key, value in dictionary.items():
        print("{} : {}".format(key, value))


class TestDateFixer(unittest.TestCase):
    def setUp(self):
        self.config_5 = configs.CleanConfig(interval=5, use_api=False)
        self.api_config_5 = configs.CleanConfig(interval=5, use_api="metronome")
        self.fixer_5 = DateFixer.DateFixer(self.config_5)
        self.variables_no = WINDOW_SIZE - 1

    def test_prepare_timepoints_to_model(self):
        timepoints = pd.date_range("2020/08/11 12:00", "2020/08/11 14:00", freq="5min")
        res_forward, res_reverse = self.fixer_5._prepare_timepoints_to_metronome(timepoints)
        should_be = {
            "var" + str(i) : [300] * (len(timepoints) - self.variables_no) for i in range(self.variables_no)
        }
        should_be["interval"] = 5

        self.assertDictEqual(
            d1=res_forward,
            d2=should_be
        )

        self.assertDictEqual(
            d1=res_reverse,
            d2=should_be
        )

    def test_prepare_timpoints_to_model_complicated(self):
        # length 13
        timepoints = pd.date_range("2020/08/11 12:00", "2020/08/11 13:00", freq="5min")
        # length 10
        timepoints2 = pd.date_range("2020/08/11 13:03", "2020/08/11 13:30", freq="3min")
        union = timepoints.union(timepoints2)
        
        differences = 12 * [300] + 10 * [180]

        res_forward, res_reverse = self.fixer_5._prepare_timepoints_to_metronome(union)

        forward = {
            "var" + str(i) : differences[i:-1 * (self.variables_no - 1) + i] for i in range(self.variables_no - 1)
        }
        forward["var13"] = differences[13:]
        forward["interval"] = 5

        reverse = {
            "var" + str(i) : differences[self.variables_no - 1 - i: len(differences) - i] for i in range(self.variables_no)
        }
        reverse["interval"] = 5

        self.assertDictEqual(
            forward,
            res_forward
        )

        self.assertDictEqual(
            reverse,
            res_reverse
        )

    def test_predict_local_sanity_check(self):
        d_to_predict = {
            "var" + str(i) : [300] for i in range(self.variables_no)
        }
        d_to_predict["interval"] = self.config_5.interval

        res = self.fixer_5._predict_local(d_to_predict)
        
        for el in res:
            self.assertGreater(el, 0.5)

    def test_merge_metronome_probabilities(self):
        l1 = 19 * [10]
        l2 = 19 * [20]
        res = self.fixer_5._merge_metronome_probabilities(l1, l2)

        expected = [20] * self.variables_no + \
                   [15] * max(len(l1) - self.variables_no, 0) + \
                   [10] * self.variables_no

        self.assertTrue(type(res) == np.ndarray,
                        "Expected result to be a numpy array")

        np.testing.assert_allclose(res, expected)

    def test_probas_to_predictions(self):
        probas = np.array([0.8, 0.1])
        predictions = self.fixer_5._probas_to_predictions(probas)
        np.testing.assert_allclose(predictions, np.array([1,0]))

    def test_metronome_predict_all_5_minutes(self):
        dates = pd.date_range("2020/08/18 15:00", "2020/08/18 20:00", freq="5min")
        res = self.fixer_5._metronome_predict(dates)
        expect = np.array([1] * len(dates))

        np.testing.assert_allclose(res, expect)

    def test_metronome_predict_local_all_5_minutes(self):
        dates = pd.date_range("2020/08/18 15:00", "2020/08/18 20:00", freq="5min")
        self.api_config_5.set_use_api(False)
        res = self.fixer_5._metronome_predict_local(dates)
        expect = np.array([1] * len(dates))

        np.testing.assert_allclose(res, expect,
                                   err_msg="\nMethod result:\n{}\nExpected:\n{}\n".format(res, expect))     

    @mock.patch("json.loads")
    @mock.patch("requests.post")
    def test_predict_api_calls(self, mocked_post, mocked_json):
        api_config = configs.CleanConfig(interval=5, use_api="metronome")
        fixer = DateFixer.DateFixer(api_config)
        mocked_post.raise_for_status = mock.Mock()

        example_dict = {"key" : "test"}
        call_res = fixer._predict_api(example_dict)
        

        self.assertTrue(call_res)
        mocked_post.assert_called_once_with(api_config._construct_full_api_address(),
                                            json=json.dumps(example_dict),
                                            timeout=0.5)

    @mock.patch("requests.Response.raise_for_status", side_effect=requests.HTTPError("ERROR!"))
    @mock.patch("json.loads")
    @mock.patch("requests.post", return_value=requests.Response())
    def test_predict_api_fallback_on_local(self, mocked_post, mocked_json, mocked_raise):
        api_config = configs.CleanConfig(interval=5, use_api="metronome")
        fixer = DateFixer.DateFixer(api_config)
        fixer._predict_local = mock.Mock()

        example_dict = {"key" : "test"}
        fixer._predict_api(example_dict)

        fixer._predict_local.assert_called_once()

    def test_call_with_wrong_api_name(self):
        wrong_api_config = configs.CleanConfig(interval=5, use_api="wrong_api_name")
        array = np.array(80 * [7])

        fixer = DateFixer.DateFixer(wrong_api_config)

        with self.assertRaises(ValueError):
            fixer(array)

    def test_call_alternative_flagger(self):
        array = np.array([1,2,3,4])
        mocked_flagger = mock.Mock()

        self.fixer_5(data=array, alternative_flagger=mocked_flagger)

        mocked_flagger.assert_called_once_with(array)