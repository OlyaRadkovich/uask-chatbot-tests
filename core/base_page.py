"""Base page object class with common functionality."""
import time
from abc import ABC
from typing import List, Optional, Tuple, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config.settings import settings


class BasePage(ABC):
    """Base class for all page objects."""
    
    def __init__(self, driver: WebDriver):
        """
        Initialize base page.
        
        Args:
            driver: WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(
            driver, 
            settings.DEFAULT_TIMEOUT,
            poll_frequency=settings.POLLING_INTERVAL
        )
    
    def navigate(self, url: str) -> None:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to (must include protocol: http:// or https://)
        """
        # Проверка формата URL
        if not url or url.strip() == "":
            raise ValueError("URL cannot be empty")
        
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"URL must start with http:// or https://, got: {url}")
        
        # Убеждаемся, что драйвер готов
        if self.driver is None:
            raise RuntimeError("WebDriver is not initialized")
        
        # Навигация с обработкой таймаутов и проверками
        try:
            # Сначала убеждаемся, что мы не на data: странице
            if self.driver.current_url.startswith("data:"):
                # Если уже на data:, попробуем обновить
                self.driver.execute_script("window.location.href = arguments[0];", url)
            else:
                self.driver.get(url)
            
            # Ждем, пока страница загрузится (проверяем, что URL изменился и корректен)
            wait = WebDriverWait(self.driver, settings.PAGE_LOAD_TIMEOUT, poll_frequency=0.5)
            wait.until(
                lambda d: d.current_url != "about:blank" 
                         and d.current_url != "data:," 
                         and not d.current_url.startswith("data:")
                         and (url in d.current_url or d.execute_script("return document.readyState") == "complete")
            )
        except TimeoutException:
            # Если таймаут, проверяем текущий URL
            current_url = self.driver.current_url
            if current_url.startswith("data:") or current_url == "data:,":
                # Повторная попытка навигации
                self.driver.get(url)
                import time
                time.sleep(2)  # Даем время на загрузку
                current_url = self.driver.current_url
                if current_url.startswith("data:"):
                    raise RuntimeError(
                        f"Navigation failed. Page opened with data: URL instead of {url}.\n"
                        f"Current URL: {current_url}.\n"
                        f"Please check:\n"
                        f"1. URL format is correct (should start with http:// or https://)\n"
                        f"2. Browser settings are correct\n"
                        f"3. Network connectivity"
                    )
            # Продолжаем, если URL корректный, но загрузка долгая
        
        # Даем время для загрузки динамических элементов (disclaimer и т.д.)
        import time
        time.sleep(1)
    
    def get_current_url(self) -> str:
        """Get current page URL."""
        return self.driver.current_url
    
    def get_title(self) -> str:
        """Get page title."""
        return self.driver.title
    
    def find_element(self, locator: Tuple[By, str], timeout: Optional[int] = None) -> WebElement:
        """
        Find element with explicit wait.
        
        Args:
            locator: Tuple of (By, selector)
            timeout: Optional timeout override
            
        Returns:
            WebElement
        """
        wait_timeout = timeout or settings.DEFAULT_TIMEOUT
        wait = WebDriverWait(self.driver, wait_timeout, poll_frequency=settings.POLLING_INTERVAL)
        return wait.until(EC.presence_of_element_located(locator))
    
    def find_elements(self, locator: Tuple[By, str], timeout: Optional[int] = None) -> List[WebElement]:
        """
        Find multiple elements with explicit wait.
        
        Args:
            locator: Tuple of (By, selector)
            timeout: Optional timeout override
            
        Returns:
            List of WebElements
        """
        wait_timeout = timeout or settings.DEFAULT_TIMEOUT
        wait = WebDriverWait(self.driver, wait_timeout, poll_frequency=settings.POLLING_INTERVAL)
        wait.until(EC.presence_of_element_located(locator))
        return self.driver.find_elements(*locator)
    
    def click_element(self, locator: Tuple[By, str], timeout: Optional[int] = None) -> None:
        """
        Click on element with wait for clickability.
        
        Args:
            locator: Tuple of (By, selector)
            timeout: Optional timeout override
        """
        wait_timeout = timeout or settings.DEFAULT_TIMEOUT
        wait = WebDriverWait(self.driver, wait_timeout, poll_frequency=settings.POLLING_INTERVAL)
        element = wait.until(EC.element_to_be_clickable(locator))
        element.click()
    
    def send_keys(self, locator: Tuple[By, str], text: str, timeout: Optional[int] = None) -> None:
        """
        Send text to input element.
        
        Args:
            locator: Tuple of (By, selector)
            text: Text to send
            timeout: Optional timeout override
        """
        element = self.find_element(locator, timeout)
        element.clear()
        element.send_keys(text)
    
    def get_text(self, locator: Tuple[By, str], timeout: Optional[int] = None) -> str:
        """
        Get text from element.
        
        Args:
            locator: Tuple of (By, selector)
            timeout: Optional timeout override
            
        Returns:
            Element text
        """
        element = self.find_element(locator, timeout)
        return element.text
    
    def is_element_present(self, locator: Tuple[By, str], timeout: Optional[int] = None) -> bool:
        """
        Check if element is present on page.
        
        Args:
            locator: Tuple of (By, selector)
            timeout: Optional timeout override
            
        Returns:
            True if element is present, False otherwise
        """
        try:
            self.find_element(locator, timeout)
            return True
        except (TimeoutException, NoSuchElementException):
            return False
    
    def is_element_visible(self, locator: Tuple[By, str], timeout: Optional[int] = None) -> bool:
        """
        Check if element is visible on page.
        
        Args:
            locator: Tuple of (By, selector)
            timeout: Optional timeout override
            
        Returns:
            True if element is visible, False otherwise
        """
        try:
            wait_timeout = timeout or settings.DEFAULT_TIMEOUT
            wait = WebDriverWait(self.driver, wait_timeout, poll_frequency=settings.POLLING_INTERVAL)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False
    
    def wait_for_element_to_disappear(self, locator: Tuple[By, str], timeout: Optional[int] = None) -> bool:
        """
        Wait for element to disappear from DOM.
        
        Args:
            locator: Tuple of (By, selector)
            timeout: Optional timeout override
            
        Returns:
            True if element disappeared, False otherwise
        """
        try:
            wait_timeout = timeout or settings.DEFAULT_TIMEOUT
            wait = WebDriverWait(self.driver, wait_timeout, poll_frequency=settings.POLLING_INTERVAL)
            wait.until(EC.invisibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False
    
    def scroll_to_element(self, locator: Tuple[By, str], timeout: Optional[int] = None) -> None:
        """
        Scroll to element.
        
        Args:
            locator: Tuple of (By, selector)
            timeout: Optional timeout override
        """
        element = self.find_element(locator, timeout)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)  # Small delay for scroll animation
    
    def execute_script(self, script: str, *args) -> Any:
        """
        Execute JavaScript.
        
        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to script
            
        Returns:
            Script execution result
        """
        return self.driver.execute_script(script, *args)

