"""Base page object class with common functionality."""
import time
from abc import ABC
from typing import Tuple, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from config.settings import settings


class BasePage(ABC):
    """Base class for all page objects."""
    
    def __init__(self, driver: WebDriver):
        """Initialize base page."""
        self.driver = driver
        self.wait = WebDriverWait(
            driver, 
            settings.DEFAULT_TIMEOUT, 
            poll_frequency=settings.POLLING_INTERVAL
        )
    
    def navigate(self, url: str) -> None:
        """Navigate to a URL."""
        if not url or not url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL: {url}")
        
        if self.driver.current_url.startswith("data:"):
            self.driver.execute_script("window.location.href = arguments[0];", url)
        else:
            self.driver.get(url)
        
        # Wait for page load
        wait = WebDriverWait(self.driver, settings.PAGE_LOAD_TIMEOUT, poll_frequency=settings.POLLING_INTERVAL)
        wait.until(
            lambda d: d.current_url != "about:blank" 
                     and not d.current_url.startswith("data:")
                     and d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(settings.SMALL_DELAY)
    
    def find_element(self, locator: Tuple[By, str], timeout: int = None):
        """Find element by locator."""
        wait_timeout = timeout or settings.DEFAULT_TIMEOUT
        wait = WebDriverWait(self.driver, wait_timeout, poll_frequency=settings.POLLING_INTERVAL)
        return wait.until(EC.presence_of_element_located(locator))
    
    def find_elements(self, locator: Tuple[By, str], timeout: int = None):
        """Find multiple elements by locator."""
        wait_timeout = timeout or settings.DEFAULT_TIMEOUT
        wait = WebDriverWait(self.driver, wait_timeout, poll_frequency=settings.POLLING_INTERVAL)
        return wait.until(EC.presence_of_all_elements_located(locator))
    
    def is_element_present(self, locator: Tuple[By, str], timeout: int = None) -> bool:
        """Check if element is present on page."""
        try:
            wait_timeout = timeout or settings.ELEMENT_PRESENT_TIMEOUT
            wait = WebDriverWait(self.driver, wait_timeout, poll_frequency=settings.POLLING_INTERVAL)
            wait.until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False
    
    def is_element_visible(self, locator: Tuple[By, str], timeout: int = None) -> bool:
        """Check if element is visible on page."""
        try:
            wait_timeout = timeout or settings.ELEMENT_VISIBLE_TIMEOUT
            wait = WebDriverWait(self.driver, wait_timeout, poll_frequency=settings.POLLING_INTERVAL)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False
    
    def click_element(self, locator: Tuple[By, str], timeout: int = None) -> None:
        """Click element by locator."""
        wait_timeout = timeout or settings.CLICK_TIMEOUT
        wait = WebDriverWait(self.driver, wait_timeout, poll_frequency=settings.POLLING_INTERVAL)
        element = wait.until(EC.element_to_be_clickable(locator))
        element.click()
    
    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript."""
        return self.driver.execute_script(script, *args)
