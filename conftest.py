"""
Pytest configuration and fixtures
"""
import pytest
import logging
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from pathlib import Path
from typing import Generator

from config import (
    BrowserConfig,
    TestConfig,
    ENGLISH_URL,
    ARABIC_URL,
    SCREENSHOTS_DIR
)
from utils.logger import setup_logger
from utils.test_helpers import ScreenshotHelper
from pages.chat_page import ChatPage

# Setup logging
logger = setup_logger(__name__)


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--browser",
        action="store",
        default=BrowserConfig.BROWSER_TYPE,
        help="Browser to use: chrome or firefox"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=BrowserConfig.HEADLESS,
        help="Run browser in headless mode"
    )
    parser.addoption(
        "--language",
        action="store",
        default=TestConfig.DEFAULT_LANGUAGE,
        help="Test language: en or ar"
    )


@pytest.fixture(scope="session")
def browser_type(request) -> str:
    """Get browser type from command line"""
    return request.config.getoption("--browser").lower()


@pytest.fixture(scope="session")
def is_headless(request) -> bool:
    """Get headless mode from command line"""
    return request.config.getoption("--headless")


@pytest.fixture(scope="function")
def language(request) -> str:
    """Get language from command line"""
    return request.config.getoption("--language").lower()


@pytest.fixture(scope="function")
def driver(browser_type: str, is_headless: bool) -> Generator[webdriver.Remote, None, None]:
    """
    Main WebDriver fixture.
    Initializes driver, sets window size, and handles teardown.
    """
    driver_instance = None
    logger.info(f"Launching {browser_type} browser (headless={is_headless})")
    try:
        if browser_type == "chrome":
            options = ChromeOptions()
            if is_headless:
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"--window-size={BrowserConfig.WINDOW_WIDTH},{BrowserConfig.WINDOW_HEIGHT}")
            options.add_argument("--disable-gpu")
            driver_instance = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=options
            )
        elif browser_type == "firefox":
            options = FirefoxOptions()
            if is_headless:
                options.add_argument("--headless")
            options.add_argument(f"--width={BrowserConfig.WINDOW_WIDTH}")
            options.add_argument(f"--height={BrowserConfig.WINDOW_HEIGHT}")
            driver_instance = webdriver.Firefox(
                service=webdriver.firefox.service.Service(GeckoDriverManager().install()),
                options=options
            )
        else:
            raise ValueError(f"Unsupported browser: {browser_type}")

        driver_instance.implicitly_wait(BrowserConfig.IMPLICIT_WAIT)
        yield driver_instance

    finally:
        if driver_instance:
            logger.info("Closing browser")
            driver_instance.quit()


@pytest.fixture(scope="function")
def chatbot_page(driver: webdriver.Remote, language: str) -> Generator[ChatPage, None, None]:
    """
    MODIFIED FIXTURE:
    Initializes ChatPage, navigates, and handles disclaimers/CAPTCHA
    to provide a test-ready page.
    """
    url = ENGLISH_URL if language == "en" else ARABIC_URL
    logger.info(f"Initializing ChatPage for language: {language}")

    chatbot = ChatPage(driver, language=language)
    chatbot.navigate(url)

    try:
        logger.info("Attempting to close disclaimer...")
        chatbot.close_disclaimer_reliably() #
        logger.info("Disclaimer handled.")

        logger.info("Attempting to close potential CAPTCHA...")
        chatbot.close_captcha_modals() #
        logger.info("CAPTCHA modals handled.")

    except Exception as e:
        logger.error(f"Error during page preparation: {e}")

    try:
        chatbot.wait_for_widget()
        chatbot.switch_to_chat_iframe()
        logger.info("Switched to chat iframe. Page is ready.")
        yield chatbot

    except Exception as e:
        logger.error(f"Failed to initialize chatbot: {e}")
        ScreenshotHelper.take_screenshot(driver, f"chatbot_init_failed_{language}")
        pytest.fail(f"Chatbot widget failed to load: {e}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test results and take screenshots on failure.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        logger.info(f"Test '{item.name}' FAILED")
        if TestConfig.SCREENSHOT_ON_FAILURE:
            # Try to get the fixture instance
            driver_instance = None
            if "chatbot_page" in item.funcargs:
                driver_instance = item.funcargs["chatbot_page"].driver
            elif "driver" in item.funcargs:
                driver_instance = item.funcargs["driver"]

            if driver_instance:
                try:
                    screenshot_name = ScreenshotHelper.generate_screenshot_name(item.name, "failed")
                    screenshot_path = str(SCREENSHOTS_DIR / screenshot_name)
                    driver_instance.save_screenshot(screenshot_path)
                    logger.info(f"Screenshot saved: {screenshot_path}")
                except Exception as e:
                    logger.error(f"Failed to capture screenshot: {e}")
            else:
                logger.warning("Could not find 'driver' or 'chatbot_page' fixture for screenshot.")


@pytest.fixture(scope="session", autouse=True)
def test_session_setup():
    """Session-level setup and teardown"""
    logger.info("=" * 80)
    logger.info("Starting Test Session")
    logger.info("=" * 80)

    yield

    logger.info("=" * 80)
    logger.info("Test Session Complete")
    logger.info("=" * 80)


@pytest.fixture(scope="function", autouse=True)
def test_case_logger(request):
    """Log test case start and end"""
    logger.info(f"Starting test: {request.node.name}")
    yield
    logger.info(f"Finished test: {request.node.name}")