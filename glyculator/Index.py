import logging
import typing

import numpy as np
import pandas as pd
import scipy
from scipy import signal

from .utils import DT, GLUCOSE
from .configs import CalcConfig

class GVIndex():
    """Abstraction of a glycemic variability index.

    Attributes:
        calc_config: configuration for calculations
        df: dataframe with a datetime column and a glucose values column
    """
    __attrs__ = [
        "calc_config", "df"
    ]

    def __init__(self, calc_config: CalcConfig, df: pd.DataFrame = None) -> None:
        self.set_df(df)
        self.set_calc_config(calc_config)
        self.logger = logging.getLogger(__name__)

    def calculate(self, **kwargs) -> float:
        raise NotImplementedError

    def set_df(self, df: pd.DataFrame) -> None:
        if(type(df) != pd.DataFrame and df is not None):
            raise ValueError("df needs to be a pandas DataFrame. Received type:{}".format(type(df)))
        self.df = df

    def set_calc_config(self, calc_config: CalcConfig) -> None:
        if(not isinstance(calc_config, CalcConfig)):
            raise ValueError("calc_config needs to be a CalcConfig")
        self.calc_config = calc_config

    def __call__(self, df: pd.DataFrame, **kwargs) -> float:
        if(type(df) != pd.DataFrame):
            raise ValueError("Cannot call GVIndex on other than pandas.DataFrame")
        self.set_df(df)
        return self.calculate(**kwargs)


class GVMean(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVMean, self).__init__(**kwargs)

    def calculate(self) -> float:
        return np.nanmean(self.df[GLUCOSE])
    

class GVMedian(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVMedian, self).__init__(**kwargs)

    def calculate(self) -> float:
        return np.nanmedian(self.df[GLUCOSE])


class GVVariance(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVVariance, self).__init__(**kwargs)

    def calculate(self) -> float:
        return np.nanvar(self.df[GLUCOSE])


class GVNanFraction(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVNanFraction, self).__init__(**kwargs)

    def calculate(self) -> float:
        return np.nansum(np.isnan(self.df[GLUCOSE])) / len(self.df)


class GVRecordsNo(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVRecordsNo, self).__init__(**kwargs)

    def calculate(self) -> float:
        return len(self.df)


class GVCV(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVCV, self).__init__(**kwargs)

    def calculate(self) -> float:
        return np.nanstd(self.df[GLUCOSE]) / np.nanmean(self.df[GLUCOSE])


class GVstd(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVstd, self).__init__(**kwargs)

    def calculate(self) -> float:
        return np.nanstd(self.df[GLUCOSE])


class GVm100(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVm100, self).__init__(**kwargs)

    def calculate(self) -> float:
        if(self.calc_config.unit == "mg"):
            # np.ma.array is numpy built-in mask function
            # numpy functions will mask elements that are inf in
            # calculations with masked array
            return np.nanmean(1000 * np.abs(np.log10(np.ma.array(self.df[GLUCOSE]) / 100)))
        if(self.calc_config.unit == "mmol"):
            # glucose: mmol/l * 18 = mg/dl
            return np.nanmean(1000 * np.abs(np.log10(np.ma.array(self.df[GLUCOSE]) / (100 / 18))))


class GVj(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVj, self).__init__(**kwargs)

    def calculate(self) -> float:
        return 0.001 * np.power(np.nanmean(self.df[GLUCOSE]) + np.nanstd(self.df[GLUCOSE]), 2)


class GVmage(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVmage, self).__init__(**kwargs)

    def calculate(self) -> float:
        """Calculates MAGE (mean average of glucose excursions)

        Steps undertaken:
        1. Replace nans with mean
        2. Moving average with window size equal to 9
        3. Search excursions and calculate the average

        Returns:
            float:
                value of MAGE

        """
        # Mean substitution of nans
        nans_replaced = self.df[GLUCOSE].replace(to_replace=np.nan, value=np.nanmean(self.df[GLUCOSE]))
        self.logger.debug("GVmage - calculate - nans_replaced: {}".format(nans_replaced))

        # Smoothing
        smoothed = self._moving_average(nans_replaced,
            window=self.calc_config.mage_moving_average_window_size)
        self.logger.debug("GVmage - calculate - smoothed: {}".format(smoothed))

        # Finding local maximas and minimas
        maximas = signal.find_peaks(smoothed, distance=self.calc_config.mage_peak_distance)[0]
        minimas = signal.find_peaks(-1 * smoothed, distance=self.calc_config.mage_peak_distance)[0]
        self.logger.debug("GVmage - calculate - minimas: {}".format(minimas))
        self.logger.debug("GVmage - calculate - maximas: {}".format(maximas))

        # minimas and maximas are joined in an alternating manner
        # example: minimas[0] maximas[0] minimas[1] maximas[1]
        joined = self._join_extremas(minimas, maximas)

        if (joined == []):
            raise RuntimeError("No maximas or minimas found in the measurement")

        joined_values = smoothed[joined]
        value_differences = np.abs(np.diff(a=joined_values))

        self.logger.debug("GVmage - calculate - joined values: \n{} \nvalue_differences: \n{}".format(joined_values, value_differences))

        if(self.calc_config.mage_excursion_threshold == "sd"):
            threshold = np.nanstd(self.df[GLUCOSE])
        if(self.calc_config.mage_excursion_threshold == "half_sd"):
            threshold = np.nanstd(self.df[GLUCOSE]) * 0.5

        self.logger.debug("GVmage - calculate - threshold: {}".format(threshold))
        value_differences = value_differences[value_differences > threshold]

        if (value_differences.size == 0):
            return 0
        else:
            return np.nanmean(value_differences)

    def _moving_average(self, arr: pd.Series, window: int) -> pd.Series:
        """Calculates moving average smoothing.

        Arguments:
            arr (pandas.Series):
                pandas.Series of glucose values
            window (int):
                size of the moving average window

        Returns:
            pandas.Series
                Series with smoothed glucose values.

        Raises:
            ValueError:
                if arr is not a pandas.Series
            ValueError:
                if window is not int
        
        """
        if(not isinstance(arr, pd.core.series.Series)):
            raise ValueError("arr must be a pandas.Series")

        if(type(window) != int):
            raise ValueError("window must be an int")

        return np.convolve(a=arr, v=np.ones((window,)) / window, mode="valid")

    def _join_extremas(self, minimas, maximas) -> list:
        """Joins indices of minimas and maximas in an alternating manner.


        Note:
            `minimas` and `maximas` are local minimas and maximas in the original 
            measurement. This function works on indices of those minimas and maximas.

            If there are two consecutive values of either type between two consecutive
            values of the other type, than all the indices except the first index in the
            consecutive series are ignored. Eg. [1,3,5] and [2, 6] will return [1,2,3,6].

        Args:
            minimas:
                list-like of indices of glucose minimas in the original measurement
            maximas:
                list-like of indices of glucose maximas in the original measurement

        Returns:
            :obj:`list` of :obj:`int`:
                joined indices of minimas and maximas

        """
        # Can't join if there are no minimas or maximas
        if(len(minimas) == 0 or len(maximas) == 0):
            return []

        joined = []
        if(minimas[0] < maximas[0]):
            minimas_turn = False
            joined.append(minimas[0])
        else:
            minimas_turn = True
            joined.append(maximas[0])

        self._join_extremas_util(joined, minimas, maximas, int(not minimas_turn), int(minimas_turn), minimas_turn)
        return joined

    def _join_extremas_util(self, joined, minimas, maximas, minimas_ind, maximas_ind, minimas_turn) -> list:
        self.logger.debug("GVmage - _join_extremas_util - called with: \njoined {} \nminimas {} \nmaximas {} \nminimas_ind {} \nmaximas_ind {} \nminimas_turn {}"    \
            .format(joined, minimas, maximas, minimas_ind, maximas_ind, minimas_turn))

        if(minimas_turn):
            if(minimas_ind >= len(minimas)):
                self.logger.debug("GVmage - _join_extremas_util - return: {}".format(joined))
                return joined

            if(minimas[minimas_ind] > joined[-1]):
                joined.append(minimas[minimas_ind])
                minimas_turn = False
            self._join_extremas_util(joined, minimas, maximas, minimas_ind + 1, maximas_ind, minimas_turn)
        else:
            if(maximas_ind >= len(maximas)):
                self.logger.debug("GVmage - _join_extremas_util - return: {}".format(joined))
                return joined
            
            if(maximas[maximas_ind] > joined[-1]):
                joined.append(maximas[maximas_ind])
                minimas_turn = True
            self._join_extremas_util(joined, minimas, maximas, minimas_ind, maximas_ind + 1, minimas_turn)

        
class GVmodd(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVmodd, self).__init__(**kwargs)

    def calculate(self) -> float:
        daily_differences = np.diff(self.df[GLUCOSE], n=int(24 * 60 / self.calc_config.interval))
        return np.nanmean(daily_differences)


class GVcongaX(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVcongaX, self).__init__(**kwargs)

    def calculate(self, hours: int) -> float:
        if(type(hours) != int or hours <= 0):
            raise ValueError("hours must be a positive int")
        differences = np.diff(self.df[GLUCOSE], n=int(hours * 60 / self.calc_config.interval))
        return np.nanvar(differences)

    def __call__(self, df: pd.DataFrame, hours: int) -> float:
        if(type(df) != pd.DataFrame):
            raise ValueError("df must be a pandas.DataFrame")
        self.df = df
        return self.calculate(hours)  


class GVhypoglycemia(GVIndex):
    def __init__(self, **kwargs) ->None:
        super(GVhypoglycemia, self).__init__(**kwargs)

    def calculate(self, threshold: int) -> float:
        if(type(threshold) != int):
            raise ValueError("threshold must be int")
        
        return np.nansum(self.df[GLUCOSE] < threshold) / np.sum(np.invert(np.isnan(self.df[GLUCOSE])))

    def __call__(self, df: pd.DataFrame, threshold: int) -> float:
        if(type(df) != pd.DataFrame):
            raise ValueError("df must be a pandas.DataFrame")
        self.df = df
        return self.calculate(threshold)


class GVhyperglycemia(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVhyperglycemia, self).__init__(**kwargs)

    def calculate(self, threshold: int) -> float:
        if(type(threshold) != int):
            raise ValueError("threshold must be int")

        return np.nansum(self.df[GLUCOSE] > threshold) / np.sum(np.invert(np.isnan(self.df[GLUCOSE])))

    def __call__(self, df: pd.DataFrame, threshold: int) -> float:
        if(type(df) != pd.DataFrame):
            raise ValueError("df must be a pandas.DataFrame")
        self.df = df
        return self.calculate(threshold)


class GVgrade(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVgrade, self).__init__(**kwargs)

    def calculate(self) -> float:
        if(self.calc_config.unit == "mg"):
            self.df[GLUCOSE] = self.df[GLUCOSE] / 18
        if(self.calc_config.unit == "mmol"):
            self.df[GLUCOSE] = self.df[GLUCOSE]
        
        GRADEs = self.GRADE(self.df[GLUCOSE])
        return np.nanmean(GRADEs)

    def GRADE(self, array: pd.Series) -> pd.Series:
        return 425 * np.power(np.log10(np.log10(np.ma.array(array)) + 0.16), 2)


class GVgrade_hypo(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVgrade_hypo, self).__init__(**kwargs)

    def calculate(self) -> float:
        if(self.calc_config.unit == "mg"):
            threshold = 90 / 18
            glucose_values = self.df[GLUCOSE] / 18

        if(self.calc_config.unit == "mmol"):
            threshold = 90 / 18
            glucose_values = self.df[GLUCOSE]


        GRADEs = self.GRADE(glucose_values)
        hypoglycemias = glucose_values < threshold

        return np.nansum(GRADEs[hypoglycemias]) / np.nansum(GRADEs)

    def GRADE(self, array: pd.Series) -> pd.Series:
        return 425 * np.power(np.log10(np.log10(np.ma.array(array)) + 0.16), 2)


class GVgrade_hyper(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVgrade_hyper, self).__init__(**kwargs)

    def calculate(self) -> float:
        if(self.calc_config.unit == "mg"):
            threshold = 140 / 18
            glucose_values = self.df[GLUCOSE] / 18

        if(self.calc_config.unit == "mmol"):
            threshold = 140 / 18
            glucose_values = self.df[GLUCOSE]

        GRADEs = self.GRADE(glucose_values)
        hyperglycemias = glucose_values > threshold

        return np.nansum(GRADEs[hyperglycemias]) / np.nansum(GRADEs)

    def GRADE(self, array: pd.Series) -> pd.Series:
        return 425 * np.power(np.log10(np.log10(np.ma.array(array)) + 0.16), 2)
            

class GVlbgi(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVlbgi, self).__init__(**kwargs)

    def calculate(self) -> float:
        f_glucose = 1.509 * (np.power(np.log10(np.ma.array(self.df[GLUCOSE])), 1.084) - 5.381)
        r_glucose = 10 * np.power(f_glucose, 2)

        rl = np.array(r_glucose)
        rl[f_glucose > 0] = 0

        return np.nanmean(rl)


class GVhbgi(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVhbgi, self).__init__(**kwargs)

    def calculate(self) -> float:
        f_glucose = 1.509 * (np.power(np.log10(np.ma.array(self.df[GLUCOSE])), 1.084) - 5.381)
        r_glucose = 10 * np.power(f_glucose, 2)

        rh = np.array(r_glucose)
        rh[f_glucose < 0] = 0

        return np.nanmean(rh)


class GVeA1c(GVIndex):
    """Calculates estimated haemoglobin A1c

    """
    def __init__(self, **kwargs) -> None:
        super(GVeA1c, self).__init__(**kwargs)

    def calculate(self) -> float:
        if(self.calc_config.unit == "mg"):
            glucose_values = self.df[GLUCOSE] / 18.02
        
        if(self.calc_config.unit == "mmol"):
            glucose_values = self.df[GLUCOSE]

        return (np.nanmean(glucose_values) + 2.52) / 1.583


class GVauc(GVIndex):
    """Calculates AUC under the glucose curve.

    It uses the trapezoid rule via numpy.trapz
    Before the actual calculation, nan values are replaced
    with 0s. The final result is normalized to the 
    length of the measurement (supplied via calc_config)

    """
    def __init__(self, **kwargs) -> None:
        super(GVauc, self).__init__(**kwargs)

    def calculate(self, standardize: bool = True) -> float:
        # nan replacement is required for the auc functions
        glucose_values = np.where(self.df[GLUCOSE] == np.nan, 0, self.df[GLUCOSE])

        if(standardize):
            auc = np.trapz(glucose_values, dx=self.calc_config.interval)   \
                / (len(glucose_values) - 1)
        else:
            auc = np.trapz(glucose_values, dx=self.calc_config.interval) 

        return auc


class GVhypo_events_count(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVhypo_events_count, self).__init__(**kwargs)

    def calculate(self, threshold: int, threshold_duration: int = 15) -> float:
        """Calculates number of hypoglycemic events.

        Arguments:
            threshold (int):
                Values of glycemia below this are treated as hypoglycemias
            hypo_event_records_threshold_duration (int, optional, default=15):
                Sequence of hypoglycemic glucose values must have duration
                greater than this to be counted as a hypoglycemic event.
                Value is expressed in minutes. Default = 15

        Returns:
            int:
                number of hypoglycemic events
        
        Raises:
            ValueError:
                if threshold or hypo_event_records_threshold_duration
                are not int

        """
        if(type(threshold) != int):
            raise ValueError("threshold must be int")

        if(type(threshold_duration) != int):
            raise ValueError("hypo_event_records_threshold_duration must be int")

        hypoglycemias = self.df[GLUCOSE] < threshold

        hypo_event_records_threshold = threshold_duration / self.calc_config.interval

        current_hypo_records = 0
        total_hypo_event_count = 0
        for record in hypoglycemias:
            if(record):
                current_hypo_records = current_hypo_records + 1
            else:
                if(current_hypo_records >= hypo_event_records_threshold):
                    total_hypo_event_count = total_hypo_event_count + 1
                current_hypo_records = 0

        if(current_hypo_records >= hypo_event_records_threshold):
            total_hypo_event_count = total_hypo_event_count + 1
            
        return total_hypo_event_count


class GVtime_in_hypo(GVIndex):
    """Calculates total time spent in hypoglycemia (in minutes)

    """
    def __init__(self, **kwargs) -> None:
        super(GVtime_in_hypo, self).__init__(**kwargs)

    def calculate(self, threshold: typing.Union[int, float]) -> float:
        if(type(threshold) not in [int, float]):
            raise ValueError("threshold must be int")

        hypoglycemias = self.df[GLUCOSE] < threshold

        return np.nansum(hypoglycemias) * self.calc_config.interval


class GVmean_hypo_event_duration(GVIndex):
    """Calculates mean duration of hypoglycemic events.

    Hypoglycemic event is defined as a sequence of hypoglycemic
    glucose values.

    """
    def __init__(self, **kwargs) -> None:
        super(GVmean_hypo_event_duration, self).__init__(**kwargs)

    def calculate(self, threshold: int, records_duration: int = 15) -> float:
        """Calculates mean duration of hypoglycemic events.

        Arguments:
            threshold (int):
                Values of glycemia below this are treated as hypoglycemias
            records_duration (int):
                Sequence of hypoglycemic glucose values must have duration
                greater than this to be counted as a hypoglycemic event.
                Value is expressed in minutes. Default = 15

        Returns:
            float:
                mean duration of hypoglycemic events
        
        Raises:
            ValueError:
                if threshold or hypo_event_records_threshold_duration
                are not int

        """
        if(type(threshold) != int):
            raise ValueError("threshold must be int")

        if(type(records_duration) != int):
            raise ValueError("records_duration")

        hypoglycemias = self.df[GLUCOSE] < threshold

        hypo_event_records_threshold = records_duration / self.calc_config.interval

        current_hypo_records = 0
        total_hypo_event_count = 0
        hypo_events_duration = []
        for record in hypoglycemias:
            if(record):
                current_hypo_records = current_hypo_records + 1
            else:
                if(current_hypo_records >= hypo_event_records_threshold):
                    total_hypo_event_count = total_hypo_event_count + 1
                    hypo_events_duration.append(current_hypo_records)
                current_hypo_records = 0

        if (len(hypo_events_duration)):
            return np.nanmean(hypo_events_duration) * self.calc_config.interval
        else:
            return 0


class GVtime_in_range(GVIndex):
    def __init__(self, **kwargs) -> None:
        super(GVtime_in_range, self).__init__(**kwargs)

    def calculate(self, lower_bound: int = None, upper_bound: int = None) -> float:
        lower_bound = lower_bound if lower_bound is not None else self.calc_config.tir_range[0]
        upper_bound = upper_bound if upper_bound is not None else self.calc_config.tir_range[1]

        if(type(lower_bound) not in [float, int] or type(upper_bound) not in [int, float]):
            raise ValueError("lower_bound and upper_bound must be int")

        return np.nansum(
            (self.df[GLUCOSE] > lower_bound) & (self.df[GLUCOSE] < upper_bound)
            ) / np.nansum(np.invert(np.isnan(self.df[GLUCOSE])))


INDICES_TO_CALC = {
    "Mean" : GVMean,
    "Median" : GVMedian,
    "Variance" : GVVariance,
    "CV" : GVCV,
    "Missing values" : GVNanFraction,
    "Total time points No" : GVRecordsNo,
    "Standard deviation" : GVstd,
    "M100" : GVm100,
    "J-index" : GVj,
    "MAGE" : GVmage,
    "MODD" : GVmodd,
    "CONGA" : GVcongaX,
    "Hypoglycemia fraction" : GVhypoglycemia,
    "Hyperglycemia fraction" : GVhyperglycemia,
    "GRADE" : GVgrade,
    "GRADE hypoglycemia" : GVgrade_hypo,
    "GRADE hyperglycemia" : GVgrade_hyper,
    "Low Blood Glucose Index" : GVlbgi,
    "High Blood Glucose Index" : GVhbgi,
    "eA1c" : GVeA1c,
    "AUC" : GVauc,
    "Hypoglycemic events No" : GVhypo_events_count,
    "Time in hypoglycemia" : GVtime_in_hypo,
    "Mean duration of hypoglycemic event" : GVmean_hypo_event_duration,
    "Time in range": GVtime_in_range,
}