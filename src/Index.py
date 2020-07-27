import numpy as np
import pandas as pd 

from .utils import DT, GLUCOSE
from .configs import CalcConfig



__all__ = [GVIndex, GVMean, GVMedian, GVVariance, GVNanCount]


class GVIndex():
    def __init__(self, df: pd.DataFrame, calc_config: CalcConfig):
        self.df = self.set_df(df)
        self.calc_config = self.set_calc_config(calc_config)

    def calculate(self):
        raise NotImplementedError

    def set_df(self, df: pd.DataFrame):
        if(type(df) != pd.core.frame.DataFrame):
            raise ValueError("df needs to be a pandas DataFrame")

        return df

    def set_calc_config(self, calc_config: CalcConfig):
        if(type(calc_config) != CalcConfig):
            raise ValueError("calc_config needs to be a CalcConfig")

        return calc_config


class GVMean(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self):
        return np.nanmean(self.df[GLUCOSE])
    

class GVMedian(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self):
        return np.nanmedian(self.df[GLUCOSE])


class GVVariance(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self):
        return np.nanvar(self.df[GLUCOSE])


class GVNanCount(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self):
        return np.isnan(self.df[GLUCOSE]) / len(self.df)


class GVRecordsNo(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self):
        return len(self.df)


class GVCV(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self):
        return np.nanvar(self.df[GLUCOSE]) / np.nanmean(self.df[GLUCOSE])


class GVstd(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self):
        return np.nanstd(self.df[GLUCOSE])


class GVm100(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self):
        if(self.calc_config == "mg"):
            # np.ma.array is numpy built-in mask function
            # numpy functions will mask elements that are inf in
            # calculations with masked array
            return np.nanmean(1000 * np.log10(np.ma.array(self.df[GLUCOSE]) / 100))
        if(self.calc_config == "mmol"):
            # glucose: mmol/l * 18 = mg/dl
            return np.nanmean(1000 * np.log10(np.ma.array(self.df[GLUCOSE]) / (100 / 18)))


class GVj(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self):
        return 0.001 * np.power(np.nanmean(self.df[GLUCOSE]) + np.nanstd(self.df[GLUCOSE]), 2)


class GVmage(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self):
        return "mage-placeholder" # TODO (konrad.pagacz@gmail.com) implement mage


class GVmodd(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self):
        daily_differences = np.diff(self.df[GLUCOSE], n=24 * 60 / self.calc_config.interval)
        return np.nanmean(daily_differences)


class GVcongaX(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self, hours: int):
        if(type(hours) != int):
            raise ValueError("hours must be int")
        differences = np.diff(self.df[GLUCOSE], n=hours * 60 / self.calc_config.interval)
        return np.nanvar(differences)

    def __call__(self, hours: int, **kwargs):
        if(type(hours) != int):
            raise ValueError("hours must be int")
        df = kwargs.pop("df")
        calc_config = kwargs.pop("calc_config")
        differences = np.diff(df[GLUCOSE], n=hours * 60 / calc_config.interval)
        return np.nanvar(differences)   


class GVhypoglycemia(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self, threshold: int):
        if(type(threshold) != int):
            raise ValueError("threshold must be int")
        
        return np.nansum(self.df[GLUCOSE] < threshold)


class GVhyperglycemia(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self, threshold: int):
        if(type(threshold) != int):
            raise ValueError("threshold must be int")

        return np.nansum(self.df[GLUCOSE] > threshold)


class GVgrade(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self):
        if(self.calc_config.unit == "mg"):
            GRADEs = 425 * np.power(np.log10(np.log10(self.df[GLUCOSE] / 18) + 0.16), 2)

        if(self.calc_config.unit == "mmol"):
            GRADEs = 425 * np.power(np.log10(np.log10(self.df[GLUCOSE]) + 0.16), 2)

        return np.nanmean(GRADEs)


class GVgrade_hypo(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self):
        if(self.calc_config.unit == "mg"):
            GRADEs = 425 * np.power(np.log10(np.log10(self.df[GLUCOSE] / 18) + 0.16), 2)
            hypoglycemias = self.df[GLUCOSE][self.df[GLUCOSE] < 90]

        if(self.calc_config.unit == "mmol"):
            GRADEs = 425 * np.power(np.log10(np.log10(self.df[GLUCOSE]) + 0.16), 2)
            hypoglycemias = self.df[GLUCOSE][self.df[GLUCOSE] < 90 / 18]

        return np.nansum(hypoglycemias / GRADEs)


class GVgrade_hyper(GVIndex):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)

    def calculate(self):
        if(self.calc_config.unit == "mg"):
            GRADEs = 425 * np.power(np.log10(np.log10(self.df[GLUCOSE] / 18) + 0.16), 2)
            hyperglycemias = self.df[GLUCOSE][self.df[GLUCOSE] < 140]

        if(self.calc_config.unit == "mmol"):
            GRADEs = 425 * np.power(np.log10(np.log10(self.df[GLUCOSE]) + 0.16), 2)
            hyperglycemias = self.df[GLUCOSE][self.df[GLUCOSE] < 140 / 18]

        return np.nansum(hyperglycemias / GRADEs)
            


