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
            Remove rows with empty DT cells.
            Set DT as index

        Arguments:
            data_df (pandas.DataFrame): 

        Returns:
            pandas.DataFrame:
                cleaned dataframe with one column GLUCOSE
                and DT as index

        """
        self.logger.debug("FileCleaner - clean_file - input file: {}".format(data_df))
        
        # I STAGE
        # Replacing empty strings with nans
        # Dropping row with nans as date
        cleaned = self.replace_empty_strings_with_nans(data_df) \
            .dropna(axis="index", subset=[DT, how="any")
        self.logger.debug("FileCleaner - clean_file - after I STAGE:{}".format(cleaned))
        self.tidy_report["Date NAs dropped"] = cleaned.shape[0] - data_df.shape[0]

        
        cleaned = cleaned.reset_index(drop=True)

        # Set DT as index
        try:
            cleaned.set_index(DT, inplace=True, drop=True)
        except:
            raise RuntimeError("Error setting DT as index")


        self.logger.debug("FileCleaner - clean_file - return: {}".format(cleaned))
        return cleaned


    def set_untidy(self, data_df: pd.DataFrame):
        if(data_df is not None):
            if(type(data_df) != pd.core.frame.DataFrame):
                raise ValueError("data_df must be a pd.DataFrame")
            self.untidy = data_df


    def set_clean_config(self, clean_config: CleanConfig):
        if(clean_config is not None):
            if(type(clean_config) != CleanConfig):
                raise ValueError("clean_config must be a CleanConfig instance")
            self.clean_config = clean_config


    def fix_dates(self, data_df: pd.DataFrame):
        print(data_df[DT].date)


    def replace_empty_strings_with_nans(self, data_df: pd.DataFrame):
        """Replaces values in cells containing empty strings with NaN

        Arguments:
            data_df (pd.DataFrame):
                DataFrame
        
        Returns:
            pd.DataFrame:
                DataFrame, where empty strings were replaced with NaNs
        
        Raises:
            RuntimeError: when replacement returns an error
        """
        try:
            cleaned = data_df   \
                .replace(to_replace="", value=np.nan)
        except:
            raise RuntimeError("Error removing NAN values from the dataset.")

        return cleaned


