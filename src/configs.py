from typing import Union
from .utils import MAGE_EXCURSION_THRESHOLDS, METRONOME_ADDRESS, METRONOME_ENDPOINT, METRONOME_PORT


# TODO (konrad.pagacz@gmail.com) expand docs

class ReadConfig:
    """Configuration for reading a CGM file.

    """
    file_length = None
    header_skip = None
    date_time_column = None
    date_column = None
    time_column = None
    glucose_values_column = None

    def __init__(self, header_skip: int = 0, 
        date_time_column: int = None, 
        date_column: int = None, 
        time_column: int = None,
        glucose_values_column: int = None):

        # Assignment
        self.set_header_skip(header_skip)
        self.set_date_time_column(date_time_column)
        self.set_date_column(date_column)
        self.set_time_column(time_column)
        self.set_glucose_values_column(glucose_values_column)

    def validate(self):
        try:
            if(self.glucose_values_column == None):
                return False
            
            if(self.header_skip == None):
                return False

            if(self.date_time_column == None and 
                (self.date_column == None or self.time_column == None)):
                return False
        except:
            return False

        return True
    
    def validateNonnegative(self, value: int):
        if(value != None):
            if(value < 0):
                raise ValueError("Number must be non-negative\n")

    def set_header_skip(self, value: int):
        try:
            self.validateNonnegative(value)
        except ValueError:
            raise ValueError("Header skip must be non-negative\n")
        self.header_skip = value

    def set_date_column(self, value: int):
        try:
            self.validateNonnegative(value)
        except ValueError:
            raise ValueError("Date column must be non-negative\n")
        self.date_column = value

    def set_date_time_column(self, value: int):
        try:
            self.validateNonnegative(value)
        except ValueError:
            raise ValueError("Date and time column must be non-negative\n")
        self.date_time_column = value

    def set_time_column(self, value: int):
        try:
            self.validateNonnegative(value)
        except ValueError:
            raise ValueError("Time column must be non-negative\n")
        self.time_column = value

    def set_glucose_values_column(self, value: int):
        try:
            self.validateNonnegative(value)
        except ValueError:
            raise ValueError("Glucose values column must be non-negative\n")
        self.glucose_values_column = value


class CleanConfig:
    """Configuration for cleaning a CGM file.

    Attributes:
        interval
        use_api
        api_port
        api_address
        api_endpoint
        _full_api_address

    """
    def __init__(self,
    interval: int,
    use_api: Union[str, bool],
    api_port: Union[int, None] = None,
    api_address: Union[str, None] = None,
    api_endpoint: Union[str, None] = None):
        self.set_interval(interval)
        self.set_use_api(use_api)
        if(api_port is not None):
            self.set_api_port(api_port)
        if(api_address):
            self.set_api_address(api_address)
        if(api_endpoint):
            self.set_api_endpoint(api_endpoint)

    def set_interval(self, interval: int):
        """Interval setter.

        Args:
            interval (int): interval of a CGM measurement

        Raises:
            ValueError: if the interval is not 5 and not 15
        """
        if(interval not in [5, 15]):
            raise ValueError("Interval needs to be 5 or 15")
        else:
            self.interval = interval

    def set_use_api(self, use_api: Union[bool, str]):
        """use_api flag setter.

        Args:
            use_api:
                boolean designating whether to use an HTTP API
                to clean dates

        Raises:
            ValueError: if api_dates is not a boolean

        """
        if(type(use_api) != bool and type(use_api) != str):
            raise ValueError("api_dates must be boolean (True or False) or str")
        else:
            if(use_api == "metronome"):
                self.set_api_address(METRONOME_ADDRESS)
                self.set_api_port(METRONOME_PORT)
                self.set_api_endpoint(METRONOME_ENDPOINT)
            self.use_api = use_api

    def set_api_port(self, api_port: int):
        """api_port setter.

        Args:
            api_port:
                Port at which the API listens

        Raises:
            ValueError: if api_port is not int or None

        """
        if(type(api_port) != int and api_port is not None):
            raise ValueError("api_port must be an integer or None")
        else:
            self.api_port = api_port

    def set_api_address(self, api_address: str):
        """api_address setter.

        Args:
            api_address:
                Address to the API

        Raises:
            ValueError: if api_address is not int or None

        """
        if(type(api_address) != str and api_address is not None):
            raise ValueError("api_endpoint must be str or None")
        else:
            self.api_address = api_address

    def set_api_endpoint(self, api_endpoint: str):
        """endpoint setter.

        Args:
            api_endpoint:
                Endpoint of the API

        Raises:
            ValueError: if api_address is not int or None

        """
        if(type(api_endpoint) != str and api_endpoint is not None):
            raise ValueError("api_endpoint must be str or None")
        else:
            self.api_endpoint = api_endpoint

    def _construct_full_api_address(self):
        elements_to_join = []
        elements_to_join.append(self.api_address)
        if(self.api_port is not None):
            elements_to_join.append(":")
            elements_to_join.append(str(self.api_port))
            elements_to_join.append("/")
        if(self.api_endpoint is not None):
            elements_to_join.append(self.api_endpoint)

        self._full_api_address = "".join(elements_to_join)
        return self._full_api_address


class CalcConfig:
    """Configuration for calculating glycemic variability indices.

    Attributes:
        interval (int):
            time in minutes between glycemic measurements
        unit (str): 
            "mg" or "mmol" unit of glycemic measurement
        mage_excursion_threshold:
            int or "sd", "half-sd"

    """
    def __init__(self, interval: int = 5, **kwargs):
        self.interval = self.set_interval(interval)
        self.unit = self.set_unit(kwargs.pop("unit", "mg"))
        self.mage_excursion_threshold = self.set_excursion_threshold(
            kwargs.pop("mage_exc", "sd")
        )
        self.mage_moving_average_windows_size = self.set_mage_moving_average(kwargs.pop("mage_window", 9))
        self.mage_peak_distance = self.set_mage_peak_distance(kwargs.pop("mage_distance", 10))

    def set_interval(self, interval: int):
        """Interval setter.

        Arguments:
            interval (int): interval of a CGM measurement

        Raises:
            ValueError: if the interval is not 5 and not 15
        """
        if(interval not in [5, 15]):
            raise ValueError("Interval needs to be 5 or 15")
        return interval

    def set_unit(self, unit: str):
        """Unit setter.

        Arguments:
            unit (str):
                Unit used in glucose measurement.
                Must be "mg" or "mmol"

        Returns:
            str: unit

        Raises:
            ValueError: if ``unit`` is not "mg" nor "mmol"

        """
        if(unit not in ["mg", "mmol"]):
            raise ValueError("unit needs to be mg or mmol")

        return unit
        
    def set_excursion_threshold(self, exc_threshold):
        if(type(exc_threshold) not in [int, str]):
            raise ValueError("mage_excursion_threshold must be int or one of {}".format(MAGE_EXCURSION_THRESHOLDS))

        if(type(exc_threshold) == int):
            return exc_threshold

        if(type(exc_threshold) == str):
            if(exc_threshold not in MAGE_EXCURSION_THRESHOLDS):
                raise ValueError("mage_excursion_threshold must be int or one of {}".format(MAGE_EXCURSION_THRESHOLDS))
            else:
                return exc_threshold

    def set_mage_moving_average(self, window_size: int):
        if(type(window_size) != int):
            raise ValueError("window_size must be an int")
        
        return window_size

    def set_mage_peak_distance(self, mage_distance: int):
        if(type(mage_distance) != int):
            raise ValueError("mage_distance must be an int")
        return mage_distance
    
    