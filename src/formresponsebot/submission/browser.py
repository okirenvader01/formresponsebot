"""Browser management for formresponsebot."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class BrowserManager:
    """Create and manage fresh Chrome browser instances."""

    def __init__(self, page_load_timeout=30):
        self.page_load_timeout = page_load_timeout

    def create(self):
        """Create and return a fresh Chrome browser."""
        chrome_options = Options()

        chrome_options.add_argument(
            "--start-maximized"
        )

        new_driver = webdriver.Chrome(
            options=chrome_options
        )

        new_driver.set_page_load_timeout(
            self.page_load_timeout
        )

        return new_driver

    def close(self, browser):
        """Safely close a browser instance."""
        if browser is not None:
            try:
                browser.quit()
            except Exception:
                pass