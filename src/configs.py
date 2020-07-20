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

        # Validation
        self.validateNonnegative(header_skip)
        self.validateNonnegative(date_time_column)
        self.validateNonnegative(date_column)
        self.validateNonnegative(time_column)
        self.validateNonnegative(glucose_values_column)

        # Assignment
        self.header_skip = header_skip
        self.date_column = date_column
        self.date_time_column = date_time_column
        self.time_column = time_column
        self.glucose_values_column = glucose_values_column

    def validate(self):
        if(self.glucose_values_column == None):
            return False
        
        if(self.header_skip == None):
            return False

        if(self.date_time_column == None and 
            (self.date_column == None or self.time_column == None)):
            return False

        return True
    
    def validateNonnegative(self, value: int):
        if(value != None):
            if(value < 0):
                raise ValueError("Header skip, column number must be nonnegative\n")

    
    def set_header_skip(self, value: int):
        self.validateNonnegative(value)
        self.header_skip = value

    def set_date_column(self, value: int):
        self.validateNonnegative(value)
        self.date_column = value

    def set_date_time_column(self, value: int):
        self.validateNonnegative(value)
        self.date_time_column = value

    def set_time_column(self, value: int):
        self.validateNonnegative(value)
        self.time_column = value

    def set_glucose_values_column(self, value: int):
        self.validateNonnegative(value)
        self.glucose_values_column = value