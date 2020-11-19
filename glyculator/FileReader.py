import os
import xlrd
import csv
import logging
import datetime

import numpy as np
import pandas as pd
from pandas.core.tools.datetimes import _guess_datetime_format

from .configs import ReadConfig
from .utils import ACCEPTED_EXTENSIONS, TEXT_EXTENSIONS, DT, GLUCOSE, DATE, TIME

# TODO (konrad.pagacz@gmail.com) expand docs

class FileReader:
    """Responsible for reading files and parsing them.

    Attributes:
        file_name (str): name of the file to read
        read_config (ReadConfig): configuration for reading 
        delimited (bool): flag for delimited text files
        extension (str): contains file extension
        string_io:
        bytes_io:
        read_report (dict): contains diagnostic information about the reading process
    
    """
    __attrs__ = [
        "file_name", "read_config", "extension", "delimited", "string_io", "bytes_io", "read_report",
        "delimited"
    ]

    def __init__(self, file_name: str = None, string_io = None, bytes_io = None, read_config: ReadConfig = None):

        # File name, which contains the data to be read
        self.file_name = file_name

        # Currently not supported
        self.string_io = string_io
        self.bytes_io = bytes_io

        # Object of class ReadConfig, which contains the configuration for this FileReader
        self.read_config = read_config

        # Flag for the file being delimited
        self.delimited = False

        self.read_report = dict()
        self.logger = logging.getLogger(__name__)


        if(file_name is not None):
            self.substring_extension()
        

    def validate_file_type(self):
        """Validates the file type.

        It validates the file type is one of the accepted file types based
        on its extension.
        Side effects: sets the delimited attribute to True if the file
        is expected to be a comma-seperated values file.

        Returns:
            bool: True if the file is one of the accepted types, false otherwise

        """
        if(self.extension not in ACCEPTED_EXTENSIONS):
            return False
        else:
            if(self.extension in TEXT_EXTENSIONS):
                self.delimited = True
            return True


    def read_file(self):
        """Reads a file.

        Performs pre-read checks and reads a file supplied by a file_name with
        configuration stored in read_config. Also calls validate_file_type to set
        the delimited attribute determining whether to treat the file as delimited
        or excel; and check for the type validity. Uses the configuration
        stored in the read_config attribute.

        Returns:
            pandas.DataFrame: Read file

        Raises:
            TypeError: if no ReadConfig is supplied
            TypeError: if no file name, stringIO or bytesIO is supplided
            ValueError: if the file type of a file is not supported
            FileNotFoundError: if the file specified by `file_name` is not found
            ValueError: if the supplied ReadConfig fails to validate

        """
        # Pre-read checks
        self.logger.debug("FileReader - started reading file")
        if(self.read_config == None):
            raise TypeError("Tried reading the file with no supplied ReadConfig. Try supplying a ReadConfig with set_config().\n")
        if(self.file_name == None and self.string_io == None and self.bytes_io == None):
            raise TypeError("Tried reading the file with no supplied source. Try supplying a file name with set_file_name() or a source.\n")
        if(self.string_io == None and self.bytes_io == None):
            if(self.validate_file_type() == False):
                raise ValueError("File type {} not supported.\n".format(self.extension))
            if(os.path.isfile(self.file_name) == False):
                raise FileNotFoundError("{} not found\n".format(self.file_name))
            if(self.read_config.validate() == False):
                raise ValueError("The supplied ReadConfig fails to validate.\n")

        
        # Reading to a list of lists
        if(self.file_name != None):
            if(self.delimited):
                data = self.read_delimited()
            else:
                data = self.read_excel()
        else:
            if(self.bytes_io != None): #TODO (konrad.pagacz@gmail.com) Make the IO reading
                data = self.read_bytes_io()
            else:
                data = self.read_string_io()

        # Creating a dict from a list of lists
        # using the read_config
        data_dict = self.lists_to_dict(data)

        # Merge Date and Time column as needed
        # if not needed remove them
        if(self.read_config.date_time_column == None):
            data_dict = self.merge_date_and_time(data_dict)
        
        # Date and Time are no longer needed
        # all the information is stored in a DT column
        del data_dict[DATE]
        del data_dict[TIME]

        # Initialize the dict as a pandas.DataFrame()
        data = pd.DataFrame(data_dict)
        self.logger.debug("FileReader - read_file - return:\n{}".format(data))

        return data
        

    def read_delimited(self):
        """Reads a csv file

        Tries to sniff the format of the csv and then attempts to read it.

        Returns:
            list: list of lists (rows)

        Raises:
            RuntimeError: When file is empty or could not read its contents.

        """
        file_ = []

        # Open and sniff the formatting of the file
        # Read the file row by row appending to file_
        with open(self.file_name, newline='') as csv_file:
            dialect = csv.Sniffer().sniff(csv_file.read(1024))
            csv_file.seek(0)
            csv_reader = csv.reader(csv_file, dialect=dialect)

            for row in csv_reader:
                file_.append(row)

        self.logger.debug("FileReader - read_delimited - read file:\n{}".format(file_))


        # This transposition makes it a little bit more efficient to subset the
        # columns DT DATE and TIME
        transposed_file_ = list(zip(*file_))
        # Detect datetime format using _guess_datetime_format from Pandas library
        # This is needed, because the date time format might vary
        for col_name, index in zip([DT, DATE], [self.read_config.date_time_column,
                                                        self.read_config.date_column]):
            if(index != None):
                # Detect format of the datetime 
                dt_array = list(transposed_file_[index])    \
                    [self.read_config.header_skip:]
                first_nonzero = pd.notnull(dt_array).nonzero()[0][0]
                dt_format = _guess_datetime_format(dt_array[first_nonzero], dayfirst=True)
                self.logger.debug("FileReader - read_delimited - detected {} format: {}"    \
                    .format(col_name, dt_format))
            
                for row in file_[self.read_config.header_skip: ]:
                    col = index
                    try:
                        row[col] = datetime.datetime.strptime(row[col], dt_format)
                    except:
                        row[col] = ""

        for col_name, index in zip([TIME], [self.read_config.time_column]):
            if(index != None):
                # Detect format of the datetime 
                dt_array = list(transposed_file_[index])    \
                    [self.read_config.header_skip:]
                first_nonzero = pd.notnull(dt_array).nonzero()[0][0]
                if(len(dt_array[first_nonzero].split(":")) == 2):
                    dt_format = "%H:%M"
                else:
                    dt_format = "%H:%M:%S"
                self.logger.debug("FileReader - read_delimited - detected {} format: {}"    \
                    .format(col_name, dt_format))

                for row in file_[self.read_config.header_skip: ]:
                    col = index
                    try:
                        row[col] = datetime.datetime.strptime(row[col], dt_format)
                    except:
                        row[col] = ""

        # Glucose values are read as strings, so there is a need to convert them to numeric
        for row in file_[self.read_config.header_skip: ]:
            row[self.read_config.glucose_values_column] = float(row[self.read_config.glucose_values_column])

        self.logger.debug("FileReader - read_delimited - return: {}".format(file_))
        return file_


    def read_excel(self):
        """Reads an excel file

        Reads an excel file using xlrd package. Also attempts to translate
        the Excel date formatting to datetime ISO format.

        Returns:
            list: list of lists (rows)

        Raises:
            RuntimeError: When file is empty or could not read its contents.

        """
        file_ = []

        # Open the excel sheet and report its shape
        wb = xlrd.open_workbook(self.file_name)
        sheet = wb.sheet_by_index(0)
        self.read_report["Raw Excel Shape"] = (sheet.nrows, sheet.ncols)

        # Read in the whole file
        # Could read only the relevant columns, but it gets messy,
        # because the order of appending cells to row[]
        # would dictate the order of DATE TIME DT GLUCOSE columns
        # which would later disrupt joining thr rows together using the 
        # read_config configuration. The positions would have to be set permanently
        # in the file_, which I am not a big fan of. This doesn't make it that much slower
        # because the whole file needs to be parsed anyway.
        for row_number in range(sheet.nrows):
            row = []
            for col_number in range(sheet.ncols):
                row.append(sheet.cell(row_number, col_number).value)
            file_.append(row)
        
        if(len(file_) == 0):
            raise RuntimeError("File {} empty or could not read its content.\n".\
                format(self.file_name))
        
        self.logger.debug("FileReader - read_excel - read the whole file:\n{}".format(file_))

        # Translate the Excel date time format
        for row in file_[self.read_config.header_skip: ]:
            # DT
            if(self.read_config.date_time_column != None):
                col = self.read_config.date_time_column
                try:
                    row[col] = xlrd.xldate.xldate_as_datetime(row[col],
                        datemode=wb.datemode)
                except:
                    row[col] = ""

            # DATE
            if(self.read_config.date_column != None):
                col = self.read_config.date_column
                try:
                    row[col] = xlrd.xldate.xldate_as_datetime(row[col],
                        datemode=wb.datemode)
                except:
                    row[col] = ""

            # TIME
            if(self.read_config.time_column != None):
                col = self.read_config.time_column
                try:
                    row[col] = xlrd.xldate.xldate_as_datetime(row[col],
                        datemode=wb.datemode)
                except:
                    row[col] = ""

        self.logger.debug("FileReader - read_excel - return:\n{}".format(file_))
        return file_


    def read_string_io(self):
        print("String io")
        file = None
        return file


    def read_bytes_io(self):
        print("Bytes IO")
        file = None
        return file


    def set_file_name(self, file_name: str):
        self.file_name = file_name
 

    def set_config(self, read_config: ReadConfig):
        if(not isinstance(read_config, ReadConfig)):
            raise ValueError("read_config must be a ReadConfig object")
        self.read_config = read_config


    def substring_extension(self):
        if(self.file_name is not None and len(self.file_name.split(".")) >= 2):
            self.extension = self.file_name.split(".")[-1]
        else:
            self.extension = None


    def lists_to_dict(self, data: list):
        """Converts rows read by this class to a dictionary.
        
        Args:
            data: list of lists, which represents a list of rows of the read file

        Returns:
            dict: dictionary with keys DT and GLUCOSE or DATE, TIME and GLUCOSE depending
                on the read_config

        """
        data_dict = {
            DT : [],
            GLUCOSE : [],
            DATE : [],
            TIME : [],
        }

        data = data[self.read_config.header_skip:]
        dt_column_number = self.read_config.date_time_column
        date_column_number = self.read_config.date_column
        time_column_number = self.read_config.time_column
        glucose_column_number = self.read_config.glucose_values_column

        if (dt_column_number != None):
            for row in data:
                data_dict[GLUCOSE].append(row[glucose_column_number])
                data_dict[DT].append(row[dt_column_number])
        else:
            for row in data:
                data_dict[GLUCOSE].append(row[glucose_column_number]) 
                data_dict[DATE].append(row[date_column_number])
                data_dict[TIME].append(row[time_column_number])

        self.logger.debug("FileReader - lists_to_dict - return {}".format(data_dict))
        return data_dict


    def merge_date_and_time(self, data_dict: dict):
        """Merges date and time columns.

        Performs an element-wise paste operation on DATE and TIME lists of data_dict
        and assigns the result to DT key in data_dict. Assumes dates are
        datetime.datetime objects.

        Arguments:
            data_dict (dict): should contain date and time keys

        Returns:
            dict: Dictionary with additional DT key, which contains
                the results of pasting

        """
        data_dict_date_type = type(data_dict[DATE])
        data_dict_time_type = type(data_dict[TIME])

        if (data_dict_date_type is not list or data_dict_time_type is not list):
            raise ValueError("data_dict[{}] and data_dict[{}] should be of the type list".format(DATE, TIME))

        dt_list = [datetime.datetime.combine(date.date(), time.time()) for  \
            (date, time) in zip(data_dict[DATE], data_dict[TIME])]
        data_dict[DT] = dt_list
        return data_dict


    def __call__(self, file_name) -> pd.DataFrame:
        self.file_name = file_name
        read_file = self.read_file()
        return read_file
    


