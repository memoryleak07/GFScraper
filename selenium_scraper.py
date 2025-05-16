import os
import time
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)
from webdriver_manager.chrome import ChromeDriverManager

import config
from logging_config import setup_logger


class SeleniumScraper:
    """
    A generic class for web scraping using Selenium.
    Can be used as a base class for more specific scrapers.
    """

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 5,
        browser_path: Optional[str] = None,
        user_agent: Optional[str] = None,
        proxy: Optional[str] = None,
        download_path: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the scraper with given parameters.

        Args:
            headless: Whether to run the browser in headless mode
            timeout: Default timeout for Selenium waits in seconds
            browser_path: Optional path to browser binary (Chrome/Chromium)
            user_agent: Optional custom user agent string
            proxy: Optional proxy server address (format: "host:port")
            download_path: Optional path to download directory
        """
        self.timeout = timeout
        self.driver = None
        self.headless = headless
        self.browser_path = browser_path
        self.user_agent = user_agent
        self.proxy = proxy
        self.download_path = download_path
        # self.screenshots_dir = "screenshots"
        self.logger = logger or setup_logger("Scraper")

    def initialize_driver(self):
        """
        Initialize and configure the Chrome WebDriver.

        Returns:
            The configured WebDriver instance
        """
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless")

        # Common options for stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")

        # Set language to English
        chrome_options.add_argument("--lang=en-US")
        chrome_options.add_experimental_option('prefs', {
            'intl.accept_languages': 'en,en_US',
        })
        # Set user agent if provided
        if self.user_agent:
            chrome_options.add_argument(f"--user-agent={self.user_agent}")

        # Set proxy if provided
        if self.proxy:
            chrome_options.add_argument(f"--proxy-server={self.proxy}")

        # Set download directory if provided
        if self.download_path:
            os.makedirs(self.download_path, exist_ok=True)
            prefs = {
                "download.default_directory": self.download_path,
                "download.prompt_for_download": False,
                }
            chrome_options.add_experimental_option("prefs", prefs)

        # Use custom binary location if provided
        if self.browser_path:
            chrome_options.binary_location = self.browser_path

        self.logger.info("Initializing Chrome WebDriver...")

        try:
            # service = Service(ChromeDriverManager().install())
            service = Service(executable_path="chromedriver-win64\\chromedriver.exe")

            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(self.timeout)
            self.driver = driver
            self.logger.info("WebDriver initialized successfully")
            return driver
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise

    def close_driver(self):
        """Close the WebDriver instance."""
        if self.driver:
            self.logger.info("Closing WebDriver...")
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.warning(f"Error while closing WebDriver: {str(e)}")
            finally:
                self.driver = None

    def __enter__(self):
        """Context manager entry point."""
        if not self.driver:
            self.initialize_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.close_driver()

    def wait_for_element(
        self, by: By, selector: str, timeout: Optional[int] = None
    ) -> Optional[webdriver.remote.webelement.WebElement]:
        """
        Wait for an element to be present and visible.

        Args:
            by: The method to locate elements (e.g., By.ID, By.CSS_SELECTOR)
            selector: The selector string
            timeout: Timeout in seconds (uses default if None)

        Returns:
            The WebElement if found, None otherwise
        """
        if timeout is None:
            timeout = self.timeout

        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            self.logger.warning(f"Timeout waiting for element: {selector}")
            return None

    def wait_for_elements(
        self, by: By, selector: str, timeout: Optional[int] = None
    ) -> List[webdriver.remote.webelement.WebElement]:
        """
        Wait for elements to be present.

        Args:
            by: The method to locate elements
            selector: The selector string
            timeout: Timeout in seconds (uses default if None)

        Returns:
            List of WebElements if found, empty list otherwise
        """
        if timeout is None:
            timeout = self.timeout

        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, selector))
            )
            return elements
        except TimeoutException:
            self.logger.warning(f"Timeout waiting for elements: {selector}")
            return []

    def wait_for_clickable(
        self, by: By, selector: str, timeout: Optional[int] = None
    ) -> Optional[webdriver.remote.webelement.WebElement]:
        """
        Wait for an element to be clickable.

        Args:
            by: The method to locate the element
            selector: The selector string
            timeout: Timeout in seconds (uses default if None)

        Returns:
            The WebElement if found and clickable, None otherwise
        """
        if timeout is None:
            timeout = self.timeout

        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            return element
        except TimeoutException:
            self.logger.warning(f"Timeout waiting for clickable element: {selector}")
            return None

    def navigate_to_url(self, url: str) -> bool:
        """
        Navigate to the specified URL and wait for page to load.

        Args:
            url: The URL to navigate to

        Returns:
            bool: Whether navigation was successful
        """
        self.logger.info(f"Navigating to URL: {url}")

        if not self.driver:
            self.logger.warning("Driver not initialized. Initializing now...")
            self.initialize_driver()

        try:
            self.driver.get(url)

            # Wait for document ready state
            WebDriverWait(self.driver, self.timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            self.logger.info("Navigation successful")
            return True
        except Exception as e:
            self.logger.error(f"Navigation failed: {str(e)}")
            return False

    def get_element_text(self, by: By, selector: str) -> Optional[str]:
        """
        Get text from an element.

        Args:
            by: The method to locate the element
            selector: The selector string

        Returns:
            The element's text if found, None otherwise
        """
        element = self.wait_for_element(by, selector)
        if element:
            try:
                return element.text.strip()
            except Exception as e:
                self.logger.warning(
                    f"Error getting text from element {selector}: {str(e)}"
                )
        return None

    def get_element_attribute(
        self, by: By, selector: str, attribute: str
    ) -> Optional[str]:
        """
        Get an attribute value from an element.

        Args:
            by: The method to locate the element
            selector: The selector string
            attribute: The attribute name

        Returns:
            The attribute value if found, None otherwise
        """
        element = self.wait_for_element(by, selector)
        if element:
            try:
                return element.get_attribute(attribute)
            except Exception as e:
                self.logger.warning(
                    f"Error getting attribute {attribute} from element {selector}: {str(e)}"
                )
        return None

    def click_element(
        self, by: By, selector: str, timeout: Optional[int] = None
    ) -> bool:
        """
        Click on an element.

        Args:
            by: The method to locate the element
            selector: The selector string
            timeout: Timeout in seconds (uses default if None)

        Returns:
            bool: Whether the click was successful
        """
        element = self.wait_for_clickable(by, selector, timeout)
        if element:
            try:
                element.click()
                return True
            except Exception as e:
                self.logger.warning(f"Error clicking element {selector}: {str(e)}")
                try:
                    # Try JavaScript click as fallback
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                except Exception as js_e:
                    self.logger.warning(f"JavaScript click also failed: {str(js_e)}")
        return False

    def input_text(self, by: By, selector: str, text: str) -> bool:
        """
        Input text into an element.

        Args:
            by: The method to locate the element
            selector: The selector string
            text: The text to input

        Returns:
            bool: Whether the text input was successful
        """
        element = self.wait_for_element(by, selector)
        if element:
            try:
                element.clear()
                element.send_keys(text)
                return True
            except Exception as e:
                self.logger.warning(
                    f"Error inputting text to element {selector}: {str(e)}"
                )
        return False

    def execute_script(self, script: str, *args) -> Any:
        """
        Execute JavaScript in the browser.

        Args:
            script: The JavaScript code to execute
            *args: Arguments to pass to the script

        Returns:
            The return value of the script
        """
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self.logger.warning(f"Error executing script: {str(e)}")
            return None

    def get_page_source(self) -> str:
        """
        Get the current page's HTML source.

        Returns:
            The page source as a string
        """
        return self.driver.page_source

    def take_screenshot(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Take a screenshot of the current page.

        Args:
            filename: Optional filename for the screenshot

        Returns:
            The path to the saved screenshot file, or None if failed
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"

        try:
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved to {filename}")
            return filename
        except Exception as e:
            self.logger.warning(f"Error taking screenshot: {str(e)}")
            return None

    def scroll_to_element(self, element) -> bool:
        """
        Scroll to make an element visible.

        Args:
            element: The WebElement to scroll to

        Returns:
            bool: Whether the scroll was successful
        """
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            return True
        except Exception as e:
            self.logger.warning(f"Error scrolling to element: {str(e)}")
            return False

    def scroll_down(self, amount: int = 500) -> None:
        """
        Scroll down the page by a specific amount of pixels.

        Args:
            amount: Number of pixels to scroll down
        """
        self.driver.execute_script(f"window.scrollBy(0, {amount});")

    def scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the page."""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scroll_to_top(self) -> None:
        """Scroll to the top of the page."""
        self.driver.execute_script("window.scrollTo(0, 0);")

    def wait_and_refresh(self, seconds: int = 5) -> None:
        """
        Wait for a specified number of seconds and then refresh the page.

        Args:
            seconds: Number of seconds to wait before refreshing
        """
        time.sleep(seconds)
        self.driver.refresh()
        WebDriverWait(self.driver, self.timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def switch_to_frame(self, frame_reference) -> bool:
        """
        Switch to an iframe.

        Args:
            frame_reference: Either an index, name/id, or WebElement

        Returns:
            bool: Whether the switch was successful
        """
        try:
            self.driver.switch_to.frame(frame_reference)
            return True
        except Exception as e:
            self.logger.warning(f"Error switching to frame: {str(e)}")
            return False

    def switch_to_default_content(self) -> None:
        """Switch back to the main document from an iframe."""
        self.driver.switch_to.default_content()

    def switch_to_window(self, window_handle) -> bool:
        """
        Switch to a different window or tab.

        Args:
            window_handle: The handle of the window to switch to

        Returns:
            bool: Whether the switch was successful
        """
        try:
            self.driver.switch_to.window(window_handle)
            return True
        except Exception as e:
            self.logger.warning(f"Error switching to window: {str(e)}")
            return False

    def get_window_handles(self) -> List[str]:
        """
        Get handles of all open windows/tabs.

        Returns:
            List of window handles
        """
        return self.driver.window_handles

    def close_current_window(self) -> None:
        """Close the current window/tab."""
        self.driver.close()

    def accept_alert(self) -> bool:
        """
        Accept an alert popup.

        Returns:
            bool: Whether the alert was successfully accepted
        """
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            return True
        except Exception as e:
            self.logger.warning(f"Error accepting alert: {str(e)}")
            return False

    def dismiss_alert(self) -> bool:
        """
        Dismiss an alert popup.

        Returns:
            bool: Whether the alert was successfully dismissed
        """
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
            return True
        except Exception as e:
            self.logger.warning(f"Error dismissing alert: {str(e)}")
            return False

    def get_cookies(self) -> List[Dict]:
        """
        Get all cookies from the browser.

        Returns:
            List of cookie dictionaries
        """
        return self.driver.get_cookies()

    def add_cookie(self, cookie: Dict) -> None:
        """
        Add a cookie to the browser.

        Args:
            cookie: Cookie dictionary with required fields
        """
        self.driver.add_cookie(cookie)

    def delete_all_cookies(self) -> None:
        """Delete all cookies from the browser."""
        self.driver.delete_all_cookies()

    def wait_for_page_load(self) -> None:
        """Wait for the page to load completely."""
        WebDriverWait(self.driver, self.timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def wait_for_ajax(self) -> None:
        """Wait for all AJAX requests to complete."""
        WebDriverWait(self.driver, self.timeout).until(
            lambda d: d.execute_script("return jQuery.active == 0")
        )

    def wait_for_condition(
        self, condition_function: Callable, timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for a custom condition to be true.

        Args:
            condition_function: A function that returns True when the condition is met
            timeout: Timeout in seconds (uses default if None)

        Returns:
            bool: Whether the condition was met within the timeout
        """
        if timeout is None:
            timeout = self.timeout

        try:
            WebDriverWait(self.driver, timeout).until(condition_function)
            return True
        except TimeoutException:
            return False

    def save_page_source(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Save the current page source to a file.

        Args:
            filename: Optional filename for the source file

        Returns:
            The path to the saved file, or None if failed
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"page_source_{timestamp}.html"

        try:
            filepath = os.path.abspath(filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            self.logger.info(f"Page source saved to {filepath}")
            return filepath
        except Exception as e:
            self.logger.warning(f"Error saving page source: {str(e)}")
            return None

    def extract_data(self, selectors: Dict[str, tuple]) -> Dict[str, Any]:
        """
        Extract data from the page using a dictionary of selectors.

        Args:
            selectors: Dictionary mapping field names to tuples of (By, selector_string)

        Returns:
            Dictionary with the extracted data
        """
        results = {}
        for field_name, (by, selector) in selectors.items():
            results[field_name] = self.get_element_text(by, selector)
        return results

    def run_scraping_task(
        self, url: str, extraction_function: Callable
    ) -> Dict[str, Any]:
        """
        Run a complete scraping task for a URL.

        Args:
            url: The URL to scrape
            extraction_function: Function that takes the scraper as an argument and returns data

        Returns:
            Dictionary with the scraped data and metadata
        """
        start_time = time.time()
        result = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "data": None,
            "error": None,
        }

        try:
            if not self.driver:
                self.initialize_driver()

            success = self.navigate_to_url(url)
            if not success:
                result["error"] = "Failed to navigate to URL"
                return result

            data = extraction_function(self)
            result["data"] = data
            result["success"] = True

        except Exception as e:
            self.logger.error(f"Error during scraping task: {str(e)}")
            result["error"] = str(e)

        finally:
            result["duration_seconds"] = time.time() - start_time
            return result

    def accept_google_cookies(self) -> bool:
        """
        Accept cookies on Google's initial page.

        This function finds and clicks the 'Accept all' or equivalent button
        on Google's cookie consent dialog.

        Returns:
            bool: Whether the cookies were successfully accepted
        """
        self.logger.info("Attempting to accept Google cookies...")

        try:
            if not self.driver:
                self.initialize_driver()

            # Try different selectors that Google might use for the cookie consent button
            # First method: Look for the "Accept all" button by its text
            accept_buttons = self.driver.find_elements(
                By.XPATH, "//button[contains(., 'Accept all')]"
            )
            if accept_buttons:
                self.logger.info("Found 'Accept all' button by text")
                return self.click_element(
                    By.XPATH, "//button[contains(., 'Accept all')]"
                )

            # Second method: Try common Google cookie button ID
            if self.driver.find_elements(By.ID, "L2AGLb"):
                self.logger.info("Found Google cookie button by ID 'L2AGLb'")
                return self.click_element(By.ID, "L2AGLb")

            # Third method: Look for buttons in the cookie dialog
            cookie_dialog = self.driver.find_elements(By.XPATH, "//div[@role='dialog']")
            if cookie_dialog:
                self.logger.info("Found cookie dialog, looking for buttons within it")
                buttons = cookie_dialog[0].find_elements(By.TAG_NAME, "button")
                # Usually the "Accept all" button is the second button
                if len(buttons) >= 2:
                    try:
                        buttons[1].click()
                        self.logger.info(
                            "Clicked on the second button in cookie dialog"
                        )
                        return True
                    except Exception as e:
                        self.logger.warning(f"Failed to click second button: {str(e)}")

            # Fourth method: Try another common selector
            if self.driver.find_elements(
                By.CSS_SELECTOR, ".cookie-dialog button.accept-button"
            ):
                self.logger.info("Found cookie accept button by CSS selector")
                return self.click_element(
                    By.CSS_SELECTOR, ".cookie-dialog button.accept-button"
                )

            self.logger.warning("Could not find Google cookie consent button")
            return False
        except Exception as e:
            self.logger.error(f"Error accepting Google cookies: {str(e)}")
            return False
