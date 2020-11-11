# logging NullHandler
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

# Silence the tensorflow messages
import os 
import logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL
logging.getLogger('tensorflow').setLevel(logging.FATAL)