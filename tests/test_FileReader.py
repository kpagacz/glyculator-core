import unittest
from unittest.mock import patch
import src.FileReader as fr


class TestFileReader(unittest.TestCase):
    def setUp(self):
        self.FileReader = fr.FileReader()

    def test_validate_file_type_not_accepted(self):
        self.FileReader.extension = "test"
        self.assertFalse(self.FileReader.validate_file_type(),
            "Expected extension not to be in accepted.")

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

    def test_set_file_name_error(self):
        with self.assertRaises(ValueError):
            self.FileReader.set_file_name("test_no_extension")

    def test_substring_extension(self):
        self.FileReader.set_file_name("test_name.test")
        self.FileReader.substring_extension()
        self.assertEqual(self.FileReader.extension, "test")

    def test_substring_extension_none(self):
        self.FileReader.set_file_name(None)
        self.FileReader.substring_extension()
        self.assertEqual(self.FileReader.extension, None)

    def test_read_file_no_config_exception(self):
        self.FileReader.read_config = None
        with self.assertRaises(TypeError):
            self.FileReader.read_file()

    def test_read_file_no_file_name_exception(self):
        self.FileReader.read_config = "mock"
        self.FileReader.file_name = None
        with self.assertRaises(TypeError):
            self.FileReader.read_file()

    def test_read_file_bad_extension_exception(self):
        self.FileReader.read_config = "mock"
        self.FileReader.file_name = "Mock"
        self.FileReader.extension = "test"
        with self.assertRaises(ValueError):
            self.FileReader.read_file()

    @patch("os.path.isfile()", False, create=True)
    def test_read_file_not_found_exception(self):
        self.FileReader.read_config = "mock"
        self.FileReader.file_name = "Mock"
        self.FileReader.extension = "csv"
        with self.assertRaises(FileNotFoundError):
            self.FileReader.read_file()

