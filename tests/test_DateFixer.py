import unittest 
import pandas as pd 
import numpy as np 

import src.DateFixer as DateFixer
import src.configs as configs


class TestDateFixer(unittest.TestCase):
    def setUp(self):
        self.config_5 = configs.CleanConfig(interval=5)
        self.fixer_5 = DateFixer.DateFixer(self.config_5)
        self.variables_no = 14

    def test_prepare_timepoints_to_model(self):
        timepoints = pd.date_range("2020/08/11 12:00", "2020/08/11 14:00", freq="5min")
        res = self.fixer_5._prepare_timepoints_to_metronome(timepoints)

        should_be = {
            "var" + str(i) : [300] * (len(timepoints) - 14) for i in range(self.variables_no)
        }
        should_be["interval"] = 5

        self.assertDictEqual(
            d1=res,
            d2=should_be
        )

