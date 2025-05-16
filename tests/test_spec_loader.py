import unittest
import os

from unittest.mock import patch, Mock, mock_open

from api_scoring_app.infra.utils import SpecLoaderFactory, LocalSpecLoader, URLSpecLoader
from api_scoring_app.core import SpecLoaderException

class TestSpecLoaderFactory(unittest.TestCase):
    """Test suite for SpecLoaderFactory."""

    def test_returns_url_loader(self):
        # startswith http
        http_loader = SpecLoaderFactory.create_loader("http://a.che/openapi.json")
        self.assertIsInstance(http_loader, URLSpecLoader)

        # startswith https
        https_loader = SpecLoaderFactory.create_loader("https://a.che/openapi.json")
        self.assertIsInstance(https_loader, URLSpecLoader)

        # startswith https but needs stripper
        https_needs_stripper = SpecLoaderFactory.create_loader("  https://a.che/openapi.json")
        self.assertIsInstance(https_needs_stripper, URLSpecLoader)

    def test_returns_local_loader(self):
        # relative file path
        relative_loader = SpecLoaderFactory.create_loader("./spec.yaml")
        self.assertIsInstance(relative_loader, LocalSpecLoader)

        # absolute file path
        absolute_loader = SpecLoaderFactory.create_loader("/home/b3tameche/spec.yaml")
        self.assertIsInstance(absolute_loader, LocalSpecLoader)

        # pwd file path
        pwd_loader = SpecLoaderFactory.create_loader("specs/spec.yaml")
        self.assertIsInstance(pwd_loader, LocalSpecLoader)

class TestLocalSpecLoader(unittest.TestCase):
    """Test suite for LocalSpecLoader."""

    def test_load_non_existing_file(self):
        loader = LocalSpecLoader("non_existing_file.yaml")
        with self.assertRaises(SpecLoaderException) as context:
            loader.load()

        self.assertIn("File not found", str(context.exception))

    def test_load_local_json_file(self):
        test_spec_path = os.path.join(os.path.dirname(__file__), "test_spec.json")
        loader = LocalSpecLoader(test_spec_path)
        result = loader.load()

        self.assertEqual(result["openapi"], "3.0.0")
        self.assertEqual(result["info"]["title"], "test")
        self.assertEqual(result["info"]["version"], "1.0.0")
        self.assertEqual(result["info"]["description"], "test description")
        self.assertTrue("paths" in result)

    def test_load_local_yaml_file(self):
        test_spec_path = os.path.join(os.path.dirname(__file__), "test_spec.yaml")
        loader = LocalSpecLoader(test_spec_path)
        result = loader.load()

        self.assertEqual(result["openapi"], "3.0.0")
        self.assertEqual(result["info"]["title"], "test")
        self.assertEqual(result["info"]["version"], "1.0.0")
        self.assertEqual(result["info"]["description"], "test description")
        self.assertTrue("paths" in result)

    @patch('api_scoring_app.infra.utils.spec_loader.os.path.exists')
    @patch('api_scoring_app.infra.utils.spec_loader.os.path.splitext')
    @patch('api_scoring_app.infra.utils.spec_loader.open', new_callable=mock_open, read_data='invalid yaml content')
    @patch('api_scoring_app.infra.utils.spec_loader.yaml.safe_load')
    def test_load_invalid_yaml_file(self, mock_safe_load: Mock, _: Mock, mock_splitext: Mock, mock_os_path_exists: Mock):
        # setup
        mock_safe_load.side_effect = Exception("Syntax error")
        mock_os_path_exists.return_value = True
        mock_splitext.return_value = ("invalid", ".yaml")
        loader = LocalSpecLoader("invalid.yaml")

        # test
        with self.assertRaises(SpecLoaderException) as context:
            loader.load()

        # assert
        self.assertIn("Error loading spec from local file", str(context.exception))
        mock_safe_load.assert_called_once()

    @patch('api_scoring_app.infra.utils.spec_loader.os.path.exists')
    @patch('api_scoring_app.infra.utils.spec_loader.os.path.splitext')
    @patch('api_scoring_app.infra.utils.spec_loader.open', new_callable=mock_open, read_data='{"invalid": json')
    @patch('api_scoring_app.infra.utils.spec_loader.json.load')
    def test_load_invalid_json_file(self, mock_json_load: Mock, _: Mock, mock_splitext: Mock, mock_os_path_exists: Mock):
        # setup
        mock_json_load.side_effect = Exception("Syntax error")
        mock_os_path_exists.return_value = True
        mock_splitext.return_value = ("invalid", ".json")
        loader = LocalSpecLoader("invalid.json")

        # test
        with self.assertRaises(SpecLoaderException) as context:
            loader.load()

        # assert
        self.assertIn("Error loading spec from local file", str(context.exception))
        mock_json_load.assert_called_once()

    @patch('api_scoring_app.infra.utils.spec_loader.os.path.exists')
    @patch('api_scoring_app.infra.utils.spec_loader.os.path.splitext')
    def test_load_invalid_file_extension(self, mock_splitext: Mock, mock_os_path_exists: Mock):
        mock_os_path_exists.return_value = True
        mock_splitext.return_value = ("invalid", ".txt")
        
        loader = LocalSpecLoader("invalid.txt")
        with self.assertRaises(SpecLoaderException) as context:
            loader.load()

        self.assertIn("Unsupported file extension, should be .yaml or .json", str(context.exception))


if __name__ == "__main__":
    unittest.main()
