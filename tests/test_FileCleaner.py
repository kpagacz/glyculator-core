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
                DT: ["test", "", "test"],
                GLUCOSE: ["8", "8", "8"]
            }
        )

        res = self.FileCleaner.clean_file(test_df)
        other = pd.DataFrame(
                {
                    DT : ["test", "test"],
                    GLUCOSE : ["8", "8"]
                }
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

    