import pandas as pd 
import numpy as np
import json 
import requests

from typing import Union

import logging

from src.configs import CleanConfig
import src.utils as utils
from src.cleaner.config import WINDOW_SIZE



# TODO (konrad.pagacz@gmail.com) expand docs
# TODO (konrad.pagacz@gmail.com) write unit tests with no integration with CleanConfig


class DateFixer(object):
    """Removes unnecessary timepoints from a CGM measurement.

    Attributes:
        clean_config (CleanConfig):
            configuration for cleaning

    """
    def __init__(self, clean_config: CleanConfig):
        self.clean_config = clean_config
        self.logger = logging.getLogger(__name__)
        self.variables_no_model = WINDOW_SIZE - 1
        self._cleaner = None

    def __call__(self, data: Union[pd.Series, np.ndarray, list], alternative_flagger=None, **kwargs):
        if(alternative_flagger is None):
            if(type(self.clean_config.use_api) == str):
                if(self.clean_config.use_api == "metronome"):
                    predictions = self._metronome_predict(data)
                elif (self.clean_config.use_api == False):
                    predictions = self._metronome_predict_local(data)
                else:
                    raise ValueError("Unsupported API type.")
        else:
            predictions = \
                alternative_flagger(data, **kwargs)
        
        self.logger.debug("DateFixer - __call__ - return:\n{}".format(predictions))

        return predictions


    def _metronome_predict(self, data: Union[pd.Series, np.ndarray, list]):
        prepared_timepoints_forward, prepared_timepoints_reverse = \
            self._prepare_timepoints_to_metronome(dates=data)
        forward_probas = self._calculate_clean_probas(prepared_timepoints_forward)
        reverse_probas = self._calculate_clean_probas(prepared_timepoints_reverse)

        overall_probas = self._merge_metronome_probabilities(forward_probas, reverse_probas)
        return self._probas_to_predictions(overall_probas)


    def _metronome_predict_local(self, data: Union[pd.Series, np.ndarray, list]):
        prepared_timepoints_forward, prepared_timepoints_reverse = \
            self._prepare_timepoints_to_metronome(dates=data)
        forward_probas = self._predict_local(prepared_timepoints_forward)
        reverse_probas = self._predict_local(prepared_timepoints_reverse)

        overall_probas = self._merge_metronome_probabilities(forward_probas, reverse_probas)
        return self._probas_to_predictions(overall_probas)


    def _prepare_timepoints_to_metronome(self, dates: pd.Series):
        """Transforms a series of dates to dictionary of
        variable name - list of values pairs.

        Dates in dates should be in a datetime format.
        This form of the input is accepted by a Cleaner class
        and Metronome API.

        Args:
            dates (pandas.Series):
                series of dates in datetime format

        Returns:
            dict:
                dictionary with keys: "var0", "var1" to "var13" and "interval"

        """
        differences = np.diff(dates, n=1)
        self.logger.debug("DateFixer - _prepare_timepoints_to_model - differences:\n{}".format(differences))

        differences = list(differences / np.timedelta64(1, "s"))

        # Creates list of differences
        # Under "var0" are values of var0 for all records
        # For more details look at the Metronome API
        forward = {
            "var" + str(i) : differences[i:-1 * (self.variables_no_model - 1) + i] for i in range(self.variables_no_model - 1)
        }
        forward["var13"] = differences[13:]
        forward["interval"] = self.clean_config.interval


        reverse = {
            "var" + str(i) : differences[self.variables_no_model - 1 - i: len(differences) - i] for i in range(self.variables_no_model)
        }
        reverse["interval"] = self.clean_config.interval

        self.logger.debug("DateFixer - _prepare_timepoints_to_model - return dict:\n{}\n{}".format(forward, reverse))
        return forward, reverse


    def _calculate_clean_probas(self, dates_records: dict):
        """Returns a boolean mask of necessary time points.

        Args:
            dates_records (dict):
                dictionary of variable : values pairs.
                Variables should be "var0", "var1", ... to
                "var13" and "interval". Values must be list-like
                and "interval" must be int.

        Returns:
            list:
                list of boolean values. Length of the list
                is equal to length of each of the value list
                from dates_records. 0 if not necessary time points,
                1 otherwise.

        """
        if(self.clean_config.use_api):
            # use api
            return self._predict_api(dates_records)
        else:
            # use local
            return self._predict_local(dates_records)


    def _predict_local(self, dates_records: dict):
        from src.cleaner.Cleaner import Cleaner5
        if(self._cleaner is None):
            self._cleaner = Cleaner5()

        interval = dates_records.pop("interval")
        probabilities = self._cleaner.predict_proba(dates_records, interval=interval)
        return probabilities


    def _predict_api(self, dates_records: dict):
        payload = json.dumps(dates_records)
        api_full_address = self.clean_config._construct_full_api_address()

        try:
            response = requests.post(api_full_address, json=payload, timeout=0.5)
            response.raise_for_status()
        except (requests.HTTPError, 
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError):
            self.logger.warning("DateFixer - _predict_api - HTTP or ConnectTimeout exception raised while connecting to Metronome API.")
            self.logger.warning("DateFixer - _predict_api - falling back onto local implementation of Metronome")
            return self._predict_local(dates_records)

        probas_and_preds = json.loads(response)
        return probas_and_preds["probabilities"]


    def _merge_metronome_probabilities(self, forward_probas: list, reverse_probas: list) -> np.ndarray:
        """Merges the probabilites from forward and reverse window approaches.


        Args:
            forward_probas:
                list of probabilities from a forward window approach
            reverse_probas:
                list of probabilties from a reverse window approach

        Returns:
            np.ndarray:
                array of probabilities of being a measurement from the interval
                pattern

        """

        # forward probas contain the probas of the same elements as reverse probas with a notable exception.
        # First variables_no_model probas of reverse_probas concern first variables_no_model elements of dates index
        # and last variables_no_model probas of forward_probas concern last variables_no_model elements of dates index
        merged = np.zeros(len(forward_probas) + self.variables_no_model)
        merged[:self.variables_no_model] = reverse_probas[:self.variables_no_model]
        merged[-1 * self.variables_no_model: ] = forward_probas[-1 * self.variables_no_model: ]
        to_average = np.array([forward_probas[: -1 * self.variables_no_model], reverse_probas[self.variables_no_model:]])
        merged[self.variables_no_model : -1 * self.variables_no_model ] = np.mean(to_average, axis=0)

        return merged


    def _probas_to_predictions(self, probas: Union[np.ndarray, pd.Series], threshold: float = 0.5):
        return probas >= threshold

