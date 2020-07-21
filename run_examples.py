from src.FileReader import FileReader
from src.configs import ReadConfig
import logging
import logging.config
import yaml

# Logging setup
with open("logging_config.yaml", 'rt') as config:
    cfg = yaml.safe_load(config.read())
    logging.config.dictConfig(cfg)

logger = logging.getLogger(__name__)
print(__name__)
logger.info("LOG!!!")

rc = ReadConfig(header_skip=2, date_time_column=0, glucose_values_column=1)
fr = FileReader(file_name="examples/excel-example1.xlsx", read_config=rc)

data = fr.read_file()

print(data)