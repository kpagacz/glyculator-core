# logging NullHandler
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())