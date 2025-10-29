"""Pytest configuration and fixtures."""
import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from adapters.driver_factory import DriverFactory
from utils.screenshot_utils import ScreenshotHelper
from config.settings import settings


@pytest.fixture(scope="function")
def driver() -> WebDriver:
    """
    Create WebDriver instance for each test.
    
    Yields:
        WebDriver instance
    """
    driver_instance = DriverFactory.create_driver()
    yield driver_instance
    
    # Cleanup
    driver_instance.quit()


@pytest.fixture(scope="function")
def driver_session(driver: WebDriver) -> WebDriver:
    """
    Provide driver with session handling.
    
    Args:
        driver: WebDriver fixture
        
    Yields:
        WebDriver instance
    """
    yield driver


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture test outcome for screenshots on failure."""
    outcome = yield
    rep = outcome.get_result()
    
    # Attach screenshot on failure
    if rep.when == "call" and rep.failed and settings.SCREENSHOT_ON_FAILURE:
        if "driver" in item.funcargs:
            driver = item.funcargs["driver"]
            test_name = item.nodeid.replace("::", "_")
            screenshot_path = ScreenshotHelper.take_screenshot_on_failure(driver, test_name)
            rep.screenshot_path = str(screenshot_path)


@pytest.fixture(autouse=True)
def configure_test_environment():
    """Auto-use fixture for test environment configuration."""
    # Setup
    yield
    # Teardown (if needed)

