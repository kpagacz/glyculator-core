import logging

import pandas as pd 
import numpy as np 

from .utils import DT, GLUCOSE
from .configs import CleanConfig


class FileCleaner():
    """Cleans the raw datafile

    Attributes:
        untidy (pandas.DataFrame):
        tidy (pandas.DataFrame):
        tidy_report (dict):
            contains information about performed tidying

    """
    untidy = None
    tidied = None
    clean_config = None
    tidy_report = {}

    def __init__(self, data_df: pd.DataFrame = None, clean_config: CleanConfig = None):
        self.logger = logging.getLogger(__name__)
        self.set_untidy(data_df)
        self.set_clean_config(clean_config)


    def tidy(self):
        """Fires up cleaning routines

        Raises:
            RuntimeError: 
                if untidy attribute is None
                if clean_config attribute is None

        """
        if(self.untidy == None):
            raise RuntimeError("No dataframe supplied to FileCleaner")

        if(self.clean_config == None):
            raise RuntimeError("No clean_config supplied to FileCleaner")


        # First cleaning
        cleaned = self.clean_file(self.untidy)


        # DT manipulations
        self.tidied = cleaned


    def clean_file(self, data_df: pd.DataFrame):
        """Regularizes the formatting of the data frame.

        This function accepts the dataframe output by
        read_file() function. It should contain two
        columns: DT and GLUCOSE.

        It performs following cleaning procedures:
        1. Removing rows with empty DT cells.

        Arguments:
            data_df (pandas.DataFrame): 

        Returns:
            pandas.DataFrame:
                cleaned dataframe with two columns:
                DT and GLUCOSE

        """
        self.logger.debug("FileCleaner - clean_file - input file: {}".format(data_df))
        
        # I STAGE
        # Replacing empty strings with nans
        # Dropping row with nans as date
        cleaned = data_df   \
            .replace(to_replace="", value=np.nan)   \
            .dropna(axis="index", subset=[DT])
        self.logger.debug("FileCleaner - clean_file - after I STAGE:{}".format(cleaned))

        # Adding to report
        self.tidy_report["Date NAs dropped"] = cleaned.shape[0] - data_df.shape[0]


        # Resetting index  
        cleaned = cleaned.reset_index(drop=True)


        self.logger.debug("FileCleaner - clean_file - return: {}".format(cleaned))
        return cleaned


    def set_untidy(self, data_df: pd.DataFrame):
        if(data_df != None):
            if(type(data_df) != pd.core.frame.DataFrame):
                raise ValueError("data_df must be a pd.DataFrame")
            self.untidy = data_df


    def set_clean_config(self, clean_config: CleanConfig):
        if(clean_config != None):
            if(type(clean_config) != CleanConfig):
                raise ValueError("clean_config must be a CleanConfig instance")
            self.clean_config = clean_config


    def fix_dates(self, data_df: pd.DataFrame):
        print(data_df[DT].date)
