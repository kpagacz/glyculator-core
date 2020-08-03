import pandas as pd 
import numpy as np
import json 
import requests

import logging

from .configs import CleanConfig

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

    def __call__(self, data: pd.DataFrame, **kwargs):
        alternative_flagger = kwargs.pop("flag_fn", default=None)
        if(alternative_flagger is None):
            prepared_timepoints = \
                self._prepare_timepoints_to_model(dates=pd.Series(data.index))
            necessary_timepoints_mask = \
                self._flag_necessary_time_points(prepared_timepoints)
        else:
            necessary_timepoints_mask = \
                alternative_flagger(pd.Series(data.index))
        

        pass

    def _prepare_timepoints_to_model(self, dates: pd.Series):
        """Transforms a series of dates to dictionary of
        variable name - list of values pairs.

        This form of the input is accepted by a Cleaner class
        and my glyculator-cleaner API.

        Arguments:
            dates (pandas.Series):
                series of dates

        Returns:
            dict:
                dictionary of variable - list of values pairs

        """
        pass

    def _flag_necessary_time_points(self, dates_records: dict):
        """Returns a boolean mask of necessary time points.

        Arguments:
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