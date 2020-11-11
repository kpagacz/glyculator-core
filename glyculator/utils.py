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


MAGE_EXCURSION_THRESHOLDS = [
    "sd",
    "half_sd"
]


ACCEPTED_API = [
    "metronome"
]

METRONOME_ADDRESS = "http://localhost"
METRONOME_PORT = 5000
METRONOME_ENDPOINT = "v1/models/metronome"

PANDAS_FILL_FREQUENCIES = {
    5 : "5min",
    15 : "15min",
}

PANDAS_TOLERANCES = {
    5 : "2.5min",
    15 : "7.5min",
}