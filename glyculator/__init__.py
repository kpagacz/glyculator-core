from .__version__ import __title__, __description__, __url__, __version__
from .__version__ import __author__, __author_email__, __license__
from .__version__ import __snake__

from .FileReader import FileReader

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
