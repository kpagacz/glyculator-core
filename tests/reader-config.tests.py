import sys
sys.path.append(".")

from src.FileReader import FileReader
from src.configs import ReadConfig
import logging
import logging.config
import yaml
import traceback


# Logging setup
with open("logging_config.yaml", 'rt') as config:
    cfg = yaml.safe_load(config.read())
    logging.config.dictConfig(cfg)

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

# excel-example1.xlsx
# DT supplied
rc = ReadConfig(header_skip=2, date_time_column=0, glucose_values_column=1)
fr = FileReader(file_name="examples/excel-example1.xlsx", read_config=rc)
try:
    example1 = fr.read_file()
    # logger.debug("Read excel-example1.xlsx:\n{}".format(data))
except Exception as e:
    logger.debug("Erorr reading in excel-example1.xlsx: {}".format(e.with_traceback()))
logger.debug("=============================")

# excel-example2.xlsx
# DT not supplied
rc = ReadConfig(header_skip=2, date_column=2, time_column=3, glucose_values_column=1)
fr = FileReader(file_name="examples/excel-example2.xlsx", read_config=rc)
try:
    example2 = fr.read_file()
except Exception as error:
    logger.debug(traceback.format_exc())
logger.debug("=============================")


# csv-example1.csv
rc = ReadConfig(header_skip=2, date_time_column=0, glucose_values_column=1)
fr = FileReader(file_name="examples/csv-example1.csv", read_config=rc)
try:
    example3 = fr.read_file()
except Exception as error:
    logger.debug(traceback.format_exc())
logger.debug("=============================")

# csv-example2.csv
# DT not supplied
rc = ReadConfig(header_skip=2, date_column=2, time_column=3, glucose_values_column=1)
fr = FileReader(file_name="examples/csv-example2.csv", read_config=rc)
try:
    example4 = fr.read_file()
except Exception as error:
    logger.debug(traceback.format_exc())
logger.debug("=============================")
