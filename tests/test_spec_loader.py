import unittest

from api_scoring_app.infra.utils import SpecLoaderFactory, LocalSpecLoader, URLSpecLoader

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

if __name__ == "__main__":
    unittest.main()
