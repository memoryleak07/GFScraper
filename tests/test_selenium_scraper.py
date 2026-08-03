import logging
import unittest
from unittest.mock import patch

from selenium_scraper import SeleniumScraper


class SeleniumScraperTests(unittest.TestCase):
    def test_create_chromedriver_manager_uses_supported_signature(self):
        scraper = SeleniumScraper(logger=logging.getLogger("test"))
        fake_manager = object()

        with patch("selenium_scraper.ChromeDriverManager", return_value=fake_manager) as mock_ctor:
            created_manager = scraper._create_chromedriver_manager(logging.WARNING)

        self.assertIs(created_manager, fake_manager)
        mock_ctor.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
