import csv
import os
import xlrd
import pandas as pd 

from .configs import ReadConfig
from .utils import ACCEPTED_EXTENSIONS, TEXT_EXTENSIONS, DT, GLUCOSE, DATE, TIME


class FileReader:
    """Reads a CGM file.

    Responsible for reading a raw CGM files. Uses csv.Sniffer
    for auto-detection of delimiter. Can read excel files.

    Attributes:
        file_name: name of the file to read
        read_config: configuration for reading 
        delimited: flag for delimited text files
        extension (str): contains file extension
        string_io:
        bytes_io:
        read_report (dict):
    
    """
    file_name = None
    read_config = None
    extension = None
    delimited = None
    string_io = None
    bytes_io = None
    read_report = {} #TODO (konrad.pagacz@gmail.com) specify the read report

    def __init__(self, file_name: str = None, string_io = None, bytes_io = None, read_config: ReadConfig = None):
        self.file_name = file_name
        self.read_config = read_config

        if(file_name != None):
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
        the delimited attribute and check for the type validity. Uses the configuration
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
        print("Read file")
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

        # Initialize the dict as a pandas.DataFrame()
        data = pd.DataFrame(data_dict)
        
        return data
        
    def read_delimited(self):
        file = None

        return file


    def read_excel(self):
        """Reads an excel file

        Reads an excel file using xlrd package.

        Returns:
            list: list of lists (rows)

        Raises:
            RuntimeError: When file is empty or could not read its contents.

        """
        file_ = []

        sheet = xlrd.open_workbook(self.file_name).sheet_by_index(0)

        self.read_report["Raw Excel Shape"] = (sheet.nrows, sheet.ncols)
        for row_number in range(sheet.nrows):
            row = []
            for col_number in range(sheet.ncols):
                row.append(sheet.cell(row_number, col_number).value)
            file_.append(row)
        
        if(len(file_) == 0):
            raise RuntimeError("File {} empty or could not read its content.\n".\
                format(self.file_name))

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
        try:
            self.substring_extension()
        except IndexError:
            raise ValueError("Expected the file to have an extension.\n")


    def set_config(self, read_config: ReadConfig):
        self.read_config = read_config


    def substring_extension(self):
        if(self.file_name != None):
            self.extension = self.file_name.split(".")[1]
        else:
            self.extension = None
    






