from .Index import *

ACCEPTED_EXTENSIONS = [
    "xlsx",
    "xls",
    "csv",
    "txt",
    "tsv"
]

TEXT_EXTENSIONS = [
    "csv",
    "txt",
    "tsv",
]

DT = "date-time"
GLUCOSE = "glucose"
DATE = "date"
TIME = "time"


INDICES_TO_CALC = {
    "Mean" : GVMean,
    "Median" : GVMedian,
    "Variance" : GVVariance,
    "CV" : GVCV,
    "Missing values" : GVNanCount,
    "Total time points no" : GVRecordsNo
}

MAGE_EXCURSION_THRESHOLDS = [
    "sd",
    "half-sd"
]
