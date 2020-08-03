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

    def __call__(self):
        pass

    def _prepare_timepoints_to_model(self, dates: pd.Series):
        pass

    def _flag_necessary_time_points(self, dates_records: dict):
        pass

    def _fill_missing_dates(self, data: pd.DataFrame):
        pass

    def _fill_missing_from_neighbours(self, data: pd.DataFrame):
        pass

    def _predict_local(self, dates_records: dict):
        pass 

    def _predict_api(self, dates_records: dict):
        pass