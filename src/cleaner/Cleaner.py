import numpy as np
import os
import logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL
logging.getLogger('tensorflow').setLevel(logging.FATAL)
import tensorflow as tf
import functools

import src.cleaner.config as config

class Cleaner(object):
    def predict_proba(self):
        raise NotImplementedError

    def predict(self):
        raise NotImplementedError

    def set_up_model(self):
        raise NotImplementedError


class Cleaner5(Cleaner):
    """Wrapper around keras model.
    
    Makes predictions about CGM time points
    being a part of regular 5 minutes interspersed
    measurement.

    """
    def __init__(self):
        self.model = self.set_up_model()
        self._probabilities = None

    def predict_proba(self, data: dict, interval: int) -> np.ndarray:
        """Returns model probability predictions.

        As a side-effects sets _probabilities output.

        Arguments:
            data (dict):
                Dict with one key - "numeric" and 
                tensor as its value.
            interval (int):
                Number of minutes designating the temporal pattern.

        Returns:
            np.ndarray:
                Array of model probability predictions

        """
        data = self._prepare_data(data, interval)
        probabilities = np.array(tf.sigmoid(self.model.predict(data))).flatten()
        self._probabilities = probabilities

        return probabilities
        
    def predict(self, data: dict, interval: int) -> np.ndarray:
        """Returns model class predictions.

        Arguments:
            data (dict):
                Dict with one key - "numeric" and 
                tensor as its value.
            interval (int):
                Number of minutes designating the temporal pattern.

        Returns:
            np.ndarray:
                Array of model class predictions.

        """
        probas = self.predict_proba(data, interval)
        predictions = (probas > config.PREDICTIONS_THRESHOLD).astype(np.int64)

        return predictions

    def _prepare_data(self, data: dict, interval: int) -> dict:
        """Prepares data to input into the model

        Arguments:
            data (dict): 
                Dictionary of variable - values pairs.
            interval (int):
                Number of minutes designating the temporal pattern.

        Returns:
            dict:
                Dict with one key - "numeric" and value
                tf.Tensor of shape (<cases number>, 14).
                This is the shape accepted by the keras model as input.

        """
        all_values = []
        for var_name in config.NUMERIC_FEATURES:
            all_values.append(data[var_name])

        matrix = np.array(all_values).reshape((config.WINDOW_SIZE - 1, -1)).transpose()

        # Normalizing the input to 5 minutes, so model will work on
        # other interval
        coefficient = 5 / interval 
        matrix = matrix * coefficient

        tensor = tf.convert_to_tensor(matrix)
        return_dict = {"numeric" : tensor}

        return return_dict

    def set_up_model(self):
        """Sets up model.

        Sets up the architecture and loads weights.

        Returns:
            tensorflow.keras.Model
                Set up model.

        """
        MIN = 0
        MAX = 350
        def min_max_scale_numeric_data(data, min_, max_):
            return (data - min_) / max_ - min_

        SCALER = functools.partial(min_max_scale_numeric_data, min_ = MIN, max_ = MAX)

        numeric_column = tf.feature_column.numeric_column("numeric", normalizer_fn=SCALER, shape=[len(config.NUMERIC_FEATURES)])
        numeric_columns = [numeric_column]

        model_densev2 = tf.keras.Sequential([
            tf.keras.layers.DenseFeatures(numeric_columns),
            tf.keras.layers.Dense(2048, activation="relu"),
            tf.keras.layers.Dense(2048, activation="relu"),
            tf.keras.layers.Dense(1024, activation="relu"),
            tf.keras.layers.Dense(1024, activation="relu"),
            tf.keras.layers.Dense(512, activation="relu"),
            tf.keras.layers.Dense(512, activation="relu"),
            tf.keras.layers.Dense(256, activation="relu"),
            tf.keras.layers.Dense(256, activation="relu"),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(1)
        ])

        model_dense = model_densev2

        # For some reason loading weights in this class produces warnings
        # about weights and biases in some places not being loaded for different
        # versions of Tensorflow.
        # I have checked whether the results of this class's model
        # are similar to the one I trained (also made one test for it)
        # and it seems they are the same, so I don't exactly know
        # what is going on. For now I leave it with expect_partial() 
        # to suppress the warnings.
        # Konrad
        model_dense.load_weights("src/cleaner/model/DenseComplicatedv2").expect_partial()
        return model_dense
