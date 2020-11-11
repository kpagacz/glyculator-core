RECORDS_TRAIN = 50000
RECORDS_TEST = 5000
INTERVAL = 300
MAX_ADDITIONAL_RECORDS = 10

WINDOW_SIZE = 15
RECORD_LENGTH = 15
"""
Record length is the same as WINDOW_SIZE,
but due to its misleading name I prefer to use WINDOW_SIZE.
I was too lazy to refactor the whole code to use WINDOW_SIZ

Konrad

"""

NUMERIC_FEATURES = ["var" + str(i) for i in range(WINDOW_SIZE - 1)]
BATCH_SIZE = 32
PREDICTIONS_THRESHOLD = 0.5
MODEL_PATH = "src/cleaner/model/DenseComplicatedv2"