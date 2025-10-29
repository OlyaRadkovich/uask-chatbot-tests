"""Screenshot utility functions."""
from pathlib import Path
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver
from config.settings import settings


class ScreenshotHelper:
    """Helper class for taking screenshots."""
    
    @staticmethod
    def take_screenshot(driver: WebDriver, filename: str = None) -> Path:
        """
        Take screenshot and save to reports directory.
        
        Args:
            driver: WebDriver instance
            filename: Optional filename (without extension)
            
        Returns:
            Path to saved screenshot
        """
        # Ensure screenshot directory exists
        settings.SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}"
        
        # Ensure .png extension
        if not filename.endswith(".png"):
            filename += ".png"
        
        # Full path
        screenshot_path = settings.SCREENSHOT_DIR / filename
        
        # Take screenshot
        driver.save_screenshot(str(screenshot_path))
        
        return screenshot_path
    
    @staticmethod
    def take_screenshot_on_failure(driver: WebDriver, test_name: str) -> Path:
        """
        Take screenshot with test name.
        
        Args:
            driver: WebDriver instance
            test_name: Name of the test that failed
            
        Returns:
            Path to saved screenshot
        """
        safe_name = test_name.replace(" ", "_").replace("::", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"failure_{safe_name}_{timestamp}.png"
        
        return ScreenshotHelper.take_screenshot(driver, filename)

