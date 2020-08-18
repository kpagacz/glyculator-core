import unittest
import tensorflow as tf 
import numpy as np 
import src.cleaner.config as config

from src.cleaner.Cleaner import Cleaner5, Cleaner

class TestCleaner(unittest.TestCase):
    def setUp(self):
        self.cleaner = Cleaner5()
        self.simple_dict = {
            "var" + str(i) : \
                np.random.uniform(low=0, high=350)  \
            for i in range(config.WINDOW_SIZE - 1)
        }

        self.many_cases_dict = {
            "var" + str(i) : \
                np.random.uniform(low=0, high=350, size=4)  \
            for i in range(config.WINDOW_SIZE - 1)
        }

        self.numeric_dict = {"numeric" : tf.convert_to_tensor([[[[ 71.61044579, 181.77008424, 176.40728705, 105.35931186,
          280.62201934,   1.75347145,  71.53847128, 280.79103081,
           50.51840917, 221.98328291,  70.91532786, 272.66580123,
          132.21352171, 323.91384077]]]])}


    def test_prepare_data_simple_shape(self):
        res_dict = self.cleaner._prepare_data(self.simple_dict, interval=5)

        self.assertTupleEqual(
            tuple1=(1, config.WINDOW_SIZE - 1),
            tuple2=tuple(res_dict["numeric"].shape)
        )

    def test_prepare_data_many_cases_shape(self):
        res_dict = self.cleaner._prepare_data(self.many_cases_dict, interval=5)

        self.assertTupleEqual(
            tuple1=(len(self.many_cases_dict["var0"]), config.WINDOW_SIZE - 1),
            tuple2=tuple(res_dict["numeric"].shape)
        )

    def test_model_exact_proba(self):
        """

        This was my sanity check, if the model loaded was indeed the model
        I have trained. I made this, because I encountered some warnings
        during loading weights in my Cleaner class - unresolved objects in weights
        and bias files. But it seems it is alright.

        """
        res_proba = float(self.cleaner.model.predict(self.numeric_dict))
        self.assertAlmostEqual(res_proba, 1138.01330566406)

    def test_predict_proba_shape_one_case(self):
        res_proba = self.cleaner.predict_proba(self.simple_dict, interval=5)
        self.assertTupleEqual(
            res_proba.shape,
            (1, )
        )

    def test_predict_proba_shape_many_cases(self):
        res_proba = self.cleaner.predict_proba(self.many_cases_dict, interval=5)
        self.assertTupleEqual(
            res_proba.shape,
            (4, )
        )

    def test_predict_sanity_check(self):
        all_300s = { "var" + str(i) : [300] for i in range(config.WINDOW_SIZE - 1)}
        res = self.cleaner.predict(all_300s, interval=5)
        print(res)


class testCleanerBase(unittest.TestCase):
    def test_predict_proba_error(self):
        with self.assertRaises(NotImplementedError):
            Cleaner().predict_proba()
    
    def test_predict_error(self):
        with self.assertRaises(NotImplementedError):
            Cleaner().predict()

    def test_set_up_model(self):
        with self.assertRaises(NotImplementedError):
            Cleaner().set_up_model()