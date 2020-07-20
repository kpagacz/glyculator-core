import unittest
from unittest.mock import patch, Mock
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

    @patch("os.path")
    def test_read_file_not_found_exception(self, mock_path):
        mock_path.isfile.return_value = False
        self.FileReader.read_config = "mock"
        self.FileReader.file_name = "Mock"
        self.FileReader.extension = "csv"
        with self.assertRaises(FileNotFoundError):
            self.FileReader.read_file()

    @patch("os.path")
    def test_read_file_config_validation_false(self, mock_path):
        mock_path.isfile.return_value = True
        mock_read_config = Mock()
        mock_read_config.validate.return_value = False
        self.FileReader.read_config = mock_read_config
        self.FileReader.file_name = "Mock"
        self.FileReader.extension = "csv"
        with self.assertRaises(ValueError):
            self.FileReader.read_file()


    @patch("os.path")
    def test_read_file_delimited_call(self, mock_path):
        # os.path mock config
        mock_path.isfile.return_value = True

        # self.read_config mock config
        mock_read_config = Mock()
        mock_read_config.validate.return_value = True
        self.FileReader.read_config = mock_read_config
        
        # self.read_delimited() mock config
        mock_read_delimited = Mock()
        self.FileReader.read_delimited = mock_read_delimited

        self.FileReader.file_name = "Mock"
        self.FileReader.extension = "csv"
        self.FileReader.read_file()
        self.FileReader.read_delimited.assert_called()


    def test_read_file_delimited_set_to_true(self):
        self.FileReader.read_config = "Mock"
        self.FileReader.file_name = "test"
        self.FileReader.extension = "csv"
        try:
            self.FileReader.read_file()
        except:
            pass
        self.assertTrue(expr=self.FileReader.delimited, msg="Failed to set \
            delimited to True in read_file() via validate_file_type()")

    def test_read_file_delimited_stays_false(self):
        self.FileReader.read_config = "Mock"
        self.FileReader.file_name = "test"
        self.FileReader.extension = "xlsx"
        try:
            self.FileReader.read_file()
        except:
            pass
        self.assertFalse(expr=self.FileReader.delimited,
         msg="delimited set to true in read_file() when extenstion is xlsx")       
        