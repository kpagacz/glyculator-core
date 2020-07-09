import unittest
import lib.FileReader as fr

class TestFileReader(unittest.TestCase):
    def setUp(self):
        self.FileReader = fr.FileReader()

    def test_validate_file_type_not_accepted(self):
        self.FileReader.extension = "test"
        self.assertFalse(self.FileReader.validate_file_type(),
            "Expected extension not to be in accepted.")
        self.FileReader.extension = None

    def test_validate_file_type_accepted_csv(self):
        self.FileReader.extension = "csv"
        self.assertTrue(self.FileReader.validate_file_type())
    
    def test_validate_file_type_accepted_tsv(self):
        self.FileReader.extension = "tsv"
        self.assertTrue(self.FileReader.validate_file_type())

    def test_validate_file_type_accepted_txt(self):
        self.FileReader.extension = "txt"
        self.assertTrue(self.FileReader.validate_file_type())

    def test_validate_file_type_delimited_csv(self):
        self.FileReader.extension = "csv"
        self.FileReader.validate_file_type()
        self.assertTrue(self.FileReader.delimited)

    def test_validate_file_type_delimited_tsv(self):
        self.FileReader.extension = "tsv"
        self.FileReader.validate_file_type()
        self.assertTrue(self.FileReader.delimited)

    def test_validate_file_type_delimited_txt(self):
        self.FileReader.extension = "txt"
        self.FileReader.validate_file_type()
        self.assertTrue(self.FileReader.delimited)

    def test_set_file_name(self):
        self.FileReader.set_file_name("test_name")
        