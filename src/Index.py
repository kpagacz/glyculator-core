import numpy as np
import pandas as pd 


from .utils import DT, GLUCOSE


class GVIndex():
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def calculate(self):
        raise NotImplementedError


class GVMean(GVIndex):
    def __init__(self, df: pd.DataFrame):
        super.__init__(df)

    def calculate(self):
        return np.nanmean(self.df[GLUCOSE])
    

class GVMedian(GVIndex):
    def __init__(self, df: pd.DataFrame):
        super.__init__(df)

    def calculate(self):
        return np.nanmedian(self.df[GLUCOSE])


class GVVariance(GVIndex):
    def __init__(self, df: pd.DataFrame):
        super.__init__(df)

    def calculate(self):
        return np.nanvar(self.df[GLUCOSE])


class GVNanCount(GVIndex):
    def __init__(self, df:pd.DataFrame):
        super.__init__(df)

    def calculate(self):
        return np.isnan(self.df[GLUCOSE]) / len(self.df)


class GVRecordsNo(GVIndex):
    def __init__(self, df:pd.DataFrame):
        super.__init__(df)

    def calculate(self):
        return len(self.df)


class GVCV(GVIndex):
    def __init__(self, df:pd.DataFrame):
        super.__init__(df)

    def calculate(self):
        return np.nanvar(self.df[GLUCOSE]) / np.nanmean(self.df[GLUCOSE])