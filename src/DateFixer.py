import pandas as pd 
import numpy as np
import json 
import requests

from typing import Union

import logging

from src.configs import CleanConfig
import src.utils as utils

# TODO (konrad.pagacz@gmail.com) create docs
# TODO (konrad.pagacz@gmail.com) write tests for DateFirxer
# TODO (konrad.pagacz@gmail.com) implement the functions


class DateFixer(object):
    """Removes unnecessary timepoints from a CGM measurement.

    Attributes:
        clean_config (CleanConfig):
            configuration for cleaning

    """
    def __init__(self, clean_config: CleanConfig):
        self.clean_config = clean_config
        self.logger = logging.getLogger(__name__)
        self.variables_no_model = 14

    def __call__(self, data: Union[pd.Series, np.ndarray, list], **kwargs):
        alternative_flagger = kwargs.pop("flag_fn", None)
        if(alternative_flagger is None):
            prepared_timepoints = \
                self._prepare_timepoints_to_metronome(dates=data)
            necessary_timepoints_mask = \
                self._flag_necessary_time_points(prepared_timepoints)
        else:
            necessary_timepoints_mask = \
                alternative_flagger(pd.Series(data.index))
        

        pass

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
        # Under "var0" are all the values of var0
        # For more details look at the Metronome API
        prepared = {
            "var" + str(i) : differences[i:-1 * (self.variables_no_model - 1) + i] for i in range(self.variables_no_model - 1)
        }

        prepared["var13"] = differences[13:]
        prepared["interval"] = self.clean_config.interval

        self.logger.debug("DateFixer - _prepare_timepoints_to_model - return dict:\n{}".format(prepared))
        return prepared

    def _flag_necessary_time_points(self, dates_records: dict):
        """Returns a boolean mask of necessary time points.

        Args:
            dates_records (dict):
                dictionary of variable : values pairs.
                Variables should be "var0", "var1", ... to
                "var13". Values must be list-like

        Returns:
            list:
                list of boolean values. Length of the list
                is equal to length of each of the value list
                from dates_records. 0 if not necessary time points,
                1 otherwise.

        """
        pass

    def _fill_missing_dates(self, data: pd.DataFrame):
        pass

    def _fill_missing_from_neighbours(self, data: pd.DataFrame):
        pass

    def _predict_local(self, dates_records: dict):
        pass 

    def _predict_api(self, dates_records: dict):
        pass