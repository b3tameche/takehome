import unittest
import os
import json
import requests

from unittest.mock import patch, Mock, mock_open

from api_scoring_app.infra.utils import SpecLoaderFactory, LocalSpecLoader, URLSpecLoader
from api_scoring_app.core.spec_loader import SpecLoaderException



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



class TestURLSpecLoader(unittest.TestCase):
    """Test suite for URLSpecLoader."""

    @patch('api_scoring_app.infra.utils.request_builder.requests.get')
    def test_load_json_url(self, mock_get: Mock):
        # setup
        example_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "test API"
            }
        }

        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = example_spec
        mock_get.return_value = mock_response

        # test
        loader = URLSpecLoader("https://a.che/openapi.json")
        result = loader.load()

        # assert
        mock_get.assert_called_once()
        self.assertEqual(result, example_spec)

    @patch('api_scoring_app.infra.utils.request_builder.requests.get')
    def test_load_yaml_url(self, mock_get: Mock):
        # setup
        example_spec = """
        openapi: 3.0.0
        info:
            title: test API
        """
        expected_result = {
            "openapi": "3.0.0",
            "info": {
                "title": "test API"
            }
        }

        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/yaml"}
        mock_response.text = example_spec
        mock_get.return_value = mock_response

        # test
        loader = URLSpecLoader("https://a.che.com/openapi.yaml")
        result = loader.load()

        # assert
        mock_get.assert_called_once()
        self.assertEqual(result, expected_result)

    @patch('api_scoring_app.infra.utils.request_builder.requests.get')
    def test_load_guess_type_json(self, mock_get: Mock):
        # setup
        return_value = {
            "openapi": "3.0.0",
            "info": {
                "title": "test API"
            }
        }

        mock_response = Mock()
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.json.return_value = return_value
        mock_get.return_value = mock_response

        # test
        loader = URLSpecLoader("https://a.che/openapi")
        result = loader.load()

        # assert
        mock_get.assert_called_once()
        self.assertEqual(result, return_value)

    @patch('api_scoring_app.infra.utils.request_builder.requests.get')
    def test_http_error(self, mock_get: Mock):
        # setup
        mock_get.side_effect = requests.HTTPError("404 Not Found")

        # test
        loader = URLSpecLoader("https://a.che/nonexistent.json")
        with self.assertRaises(SpecLoaderException) as context:
            loader.load()

        # assert
        mock_get.assert_called_once()
        self.assertIn("Error loading spec from URL", str(context.exception))

    @patch('api_scoring_app.infra.utils.request_builder.requests.get')
    def test_connection_error(self, mock_get: Mock):
        # setup
        mock_get.side_effect = requests.ConnectionError("Connection refused")

        # test
        loader = URLSpecLoader("https://a.che/nonexistent.json")
        with self.assertRaises(SpecLoaderException) as context:
            loader.load()

        # assert
        mock_get.assert_called_once()
        self.assertIn("Error loading spec from URL", str(context.exception))

    @patch('api_scoring_app.infra.utils.request_builder.requests.get')
    def test_invalid_json(self, mock_get: Mock):
        # setup
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.side_effect = json.JSONDecodeError("Invalid json", "", 0)
        mock_response.text = "not json, not yaml"
        mock_get.return_value = mock_response

        # test
        loader = URLSpecLoader("https://a.che/invalid.json")
        with self.assertRaises(SpecLoaderException) as context:
            loader.load()

        # assert
        mock_get.assert_called_once()
        self.assertIn("Error parsing spec from URL", str(context.exception))

