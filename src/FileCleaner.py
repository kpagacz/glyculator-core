import logging

import pandas as pd 
import numpy as np 

from .utils import DT, GLUCOSE, PANDAS_FILL_FREQUENCIES, PANDAS_TOLERANCES
from .configs import CleanConfig
import src.DateFixer as DateFixer

# TODO (konrad.pagacz@gmail.com) expand docs
# TODO (konrad.pagacz@gmail.com) write unit tests with no integration with CleanConfig


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
        if(self.untidy is None):
            raise RuntimeError("No dataframe supplied to FileCleaner")

        if(self.clean_config is None):
            raise RuntimeError("No clean_config supplied to FileCleaner")


        # First cleaning
        cleaned = self._clean_file(self.untidy)

        # Date fix
        true_measures_flags = self.fix_dates(cleaned)
        dates_fixed = cleaned.loc[true_measures_flags, :].copy()

        # Fill NaN glucose values with the nearest
        glucose_filled = self._fill_glucose_values_with_nearest(dates_fixed, cleaned)

        # Fill missing dates
        dates_filled = self._fill_missing_dates(glucose_filled)

        self.tidied = dates_filled
        return dates_filled


    def _clean_file(self, data_df: pd.DataFrame):
        """Regularizes the formatting of the data frame.

        This function accepts the dataframe output by
        read_file() function. It should contain two
        columns: DT and GLUCOSE.

        It performs following cleaning procedures:
            Replace empty strings with np.nan
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
        
        # Replacing empty strings with nans
        # Dropping row with nans as date
        cleaned = self._replace_empty_strings_with_nans(data_df) \
            .dropna(axis="index", subset=[DT], how="any") \
            .reset_index(drop=True)
        self.logger.debug("FileCleaner - clean_file - after I STAGE:{}".format(cleaned))
        self.tidy_report["Date NAs dropped"] = cleaned.shape[0] - data_df.shape[0]

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
        """Flags measurements of data_df

        Args:
            data_df:
                Dataframe of measurements.
                Two columns: DT and GLUCOSE

        Returns:
            numpy.ndarray:
                Array of 0s and 1s - boolean values
                1 represents record, which is part of the CGM
                0 represents additional record, which should be discarded


        """
        dates = data_df[DT]
        date_fixer = DateFixer.DateFixer(self.clean_config)
        flags = date_fixer(dates)

        return flags


    def _replace_empty_strings_with_nans(self, data_df: pd.DataFrame):
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
        
        self.logger.debug("FileCleaner - _replace_empty_strings_with_nans - "
            "return: {}".format(cleaned))
        return cleaned


    def _fill_glucose_values_with_nearest(self, date_fixed: pd.DataFrame, not_fixed: pd.DataFrame) -> pd.DataFrame:
        """Attempts to fill missing glucose values.

        Does not guarantee that missing values will be filled. Does not change index
        of date_fixed.

        Args:
            date_fixed:
                DataFrame of DT and GLUCOSE columns. It is a slice of not_fixed.
            not_fixed:
                DataFrame of DT and GLUCOSE columns.

        Returns:
            pandas.DataFrame:
                date_fixed dataframe with missing glucose values filled
                based on not_fixed dataframe. 

        """
        def fill_missing_value(index, row):
            filled = np.nan
            index_no = not_fixed.index.get_loc(index)
            try:
                row_before = not_fixed.iloc[index_no - 1, :]
                difference = (row[DT] - row_before[DT]) / np.timedelta64(1, "s")
                if(difference < self.clean_config.fill_glucose_tolerance * 60):
                    filled = row_before[GLUCOSE]
            except:
                pass

            try:
                row_after = not_fixed.iloc[index_no + 1, :]
                difference = (row_after[DT] - row[DT]) / np.timedelta64(1, "s")
                if(difference < self.clean_config.fill_glucose_tolerance * 60):
                    filled = row_after[GLUCOSE]
            except:
                pass
            return filled
        
        for index, row in date_fixed.iterrows():
            if(pd.isnull(row[GLUCOSE])):
                fill = fill_missing_value(index, row)
                date_fixed.loc[index, GLUCOSE] = fill

        return date_fixed


    def _fill_missing_dates(self, df : pd.DataFrame) -> pd.DataFrame:
        """Sets DT columns as index and fills missing dates.

        Some time points might be missing from the CGM measurement. This function
        tries to input those missing timepoints and assigns them a NaN glucose value.

        Args:
            df:
                pandas.DataFrame with two columns - DT and GLUCOSE

        Returns:
            pd.DataFrame:
                dataframe with two columns - DT and GLUCOSE

        """
        first_date = df[DT].iloc[0]
        last_date = df[DT].iloc[-1]
        new_range = pd.date_range(first_date, last_date, freq=PANDAS_FILL_FREQUENCIES[self.clean_config.interval])

        df = df.set_index(DT, drop=True) \
            .reindex(new_range, method="nearest", tolerance=PANDAS_TOLERANCES[self.clean_config.interval]) \
            .reset_index(drop=False) \
            .rename(columns={"index" : DT})

        self.logger.debug("FileCleaner - _fill_missing_dates - return:\n{}".format(df))
        return df