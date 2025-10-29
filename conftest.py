"""
Pytest configuration and Selenium fixtures
"""
import pytest
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from typing import Generator

from config import (
    TestConfig,
    ENGLISH_URL,
    ARABIC_URL,
    SCREENSHOTS_DIR,
    SESSION_FILE
)
from utils.session_manager import SessionManager
from utils.logger import setup_logger
from utils.test_helpers import ScreenshotHelper
from pages.chat_page import ChatPage

logger = setup_logger(__name__)


def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true", default=False, help="Run browser in headless mode")
    parser.addoption("--language", action="store", default=TestConfig.DEFAULT_LANGUAGE, help="Test language: en or ar")


@pytest.fixture(scope="session")
def headless(request) -> bool:
    return request.config.getoption("--headless")


@pytest.fixture(scope="session")
def test_language(request) -> str:
    return request.config.getoption("--language")


@pytest.fixture(scope="function")
def driver(headless: bool) -> Generator[webdriver.Chrome, None, None]:
    logger.info(f"Launching Chrome (headless={headless})")
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Use Selenium Manager to resolve the correct chromedriver for the platform
    drv = webdriver.Chrome(options=options)
    
    # Note: Session will be loaded per-test in chatbot_page fixture
    # This allows cookies to be fresh for each test
    if SESSION_FILE.exists():
        logger.info(f"Saved session file found: {SESSION_FILE}")
    else:
        logger.info("No saved session found, starting fresh")
    
    yield drv
    logger.info("Closing Chrome")
    drv.quit()


@pytest.fixture(scope="function")
def chatbot_page(driver, test_language: str) -> ChatPage:
    """Function-scoped ChatPage; new browser per test as requested."""
    logger.info(f"Initializing ChatPage for language: {test_language}")
    chatbot = ChatPage(driver)
    url = ENGLISH_URL if test_language == "en" else ARABIC_URL

    # Load saved session for this fresh browser if available
    if SESSION_FILE.exists():
        logger.debug("Loading saved session for new browser")
        SessionManager.load_session(driver, SESSION_FILE, target_url=url)

    chatbot.navigate(url)

    # Close disclaimers
    try:
        chatbot.close_disclaimer_reliably()
    except Exception as e:
        logger.info(f"Disclaimer close attempt skipped: {e}")

    # Handle CAPTCHA if shown
    captcha_info = chatbot.check_for_captcha()
    if captcha_info["captcha_detected"]:
        logger.warning("🔴 CAPTCHA detected on test start - waiting for manual solution")
        if chatbot.wait_for_manual_captcha_solution(timeout=60):
            if chatbot.save_session_after_captcha(SESSION_FILE):
                logger.info("✓ Session saved after CAPTCHA solution")
            # Give the page a moment to fully recover from CAPTCHA modal
            import time
            time.sleep(2)

    try:
        chatbot.wait_for_chat_widget(timeout=20000)
    except Exception as e:
        logger.error(f"Failed to load chat widget: {e}")
        if TestConfig.SCREENSHOT_ON_FAILURE:
            chatbot.take_screenshot("chat_widget_load_failure")
        raise

    # Cleanup input for a clean start
    try:
        if chatbot.input_box:
            chatbot.driver.execute_script(
                "arguments[0].textContent=''; arguments[0].innerText='';",
                chatbot.input_box,
            )
    except Exception:
        pass

    return chatbot


 


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        if "chatbot_page" in item.funcargs and report.failed and TestConfig.SCREENSHOT_ON_FAILURE:
            chatbot = item.funcargs.get("chatbot_page")
            screenshot_name = ScreenshotHelper.generate_screenshot_name(item.name, "failed")
            try:
                screenshot_path = chatbot.take_screenshot(screenshot_name)
                logger.info(f"Screenshot saved: {screenshot_path}")
                ScreenshotHelper.save_screenshot_metadata(
                    screenshot_path,
                    item.name,
                    {"error": str(report.longrepr), "test_phase": report.when}
                )
            except Exception as e:
                logger.error(f"Failed to capture screenshot: {e}")


@pytest.fixture(scope="session", autouse=True)
def test_session_setup():
    """
    Session-level setup and teardown
    Runs once before all tests and once after
    """
    logger.info("=" * 80)
    logger.info("Starting Test Session")
    logger.info("=" * 80)

    yield

    logger.info("=" * 80)
    logger.info("Test Session Complete")
    logger.info("=" * 80)


@pytest.fixture(scope="function", autouse=True)
def test_case_logger(request):
    """
    Log test case start and end
    """
    logger.info(f"Starting test: {request.node.name}")

    yield

    logger.info(f"Finished test: {request.node.name}")
