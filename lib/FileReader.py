import csv
import os

from lib.configs import ReadConfig
from lib.utils import ACCEPTED_EXTENSIONS


class FileReader:
    """Reads a CGM file.

    Responsible for reading the raw CGM files. Uses csv.Sniffer
    for auto-detection of delimiter. Can read excel files.

    Attributes:
        file_name: name of the file to read
        read_config: configuration for reading 
        delimited: flag for delimited text files
        extension (str): contains file extension
    """
    file_name = None
    read_config = None
    extension = None
    delimited = None
    string_io = None
    bytes_io = None

    def __init__(self, file_name: str = None, string_io = None, bytes_io = None, read_config: ReadConfig = None):
        self.file_name = file_name
        self.read_config = read_config

        if(file_name != None):
            self.substring_extension()


    def validate_file_type(self):
        if(self.extension not in ACCEPTED_EXTENSIONS):
            return False
        else:
            if(self.extension in "csv tsv txt".split()):
                self.delimited = True
            return True


    def read_file(self):
        """Reads a file.

        Performs pre-read checks and reads a file supplied by a file_name with
        configuration stored in read_config.

        """
        # Pre-read checks
        print("Read file")
        if(self.read_config == None):
            raise TypeError("Tried reading the file with no supplied ReadConfig. Try supplying a ReadConfig with set_config().\n")
        if(self.file_name == None and self.string_io == None and self.bytes_io == None):
            raise TypeError("Tried reading the file with no supplied source. Try supplying a file name with set_file_name() or a source.\n")
        if(self.validate_file_type == False):
            raise ValueError("File type {} not supported.\n".format(self.extension))
        if(os.path.isfile(self.file_name) == False):
                raise FileNotFoundError("{} not found.\n".format(self.file_name))
        
        
    def read_delimited(self):
        file = None

        return file


    def read_excel(self):
        file = None

        return file


    def set_file_name(self, file_name: str):
        self.file_name = file_name
        self.substring_extension()


    def set_config(self, read_config: ReadConfig):
        self.read_config = read_config


    def substring_extension(self):
        if(self.file_name != None):
            self.extension = self.file_name.split(".")[1]
        else:
            self.extension = None
    






