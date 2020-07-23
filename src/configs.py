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

    """
    interval = None

    def __init__(self, interval: int = None):
        self.set_interval(interval)

    def set_interval(self, interval: int):
        """Interval setter.

        Arguments:
            interval (int): interval of a CGM measurement

        Raises:
            ValueError: if the interval is not 5 and not 15
        """
        if(interval not in [5, 15]):
            raise ValueError("Interval needs to be 5 or 15")