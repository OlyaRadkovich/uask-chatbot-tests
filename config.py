"""
Configuration file for U-Ask QA Automation Framework
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from selenium.webdriver.common.by import By

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
LOGS_DIR = REPORTS_DIR / "logs"

# Create directories if they don't exist
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Application Under Test
BASE_URL = os.getenv("BASE_URL", "https://ask.u.ae")
ENGLISH_URL = f"{BASE_URL}/en/"
ARABIC_URL = f"{BASE_URL}/ar/"

# Browser configuration
class BrowserConfig:
    BROWSER_TYPE = os.getenv("BROWSER", "chrome")  # chrome, firefox
    HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
    WINDOW_WIDTH = int(os.getenv("VIEWPORT_WIDTH", "1920"))
    WINDOW_HEIGHT = int(os.getenv("VIEWPORT_HEIGHT", "1080"))
    IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", "10"))  # seconds
    PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))  # seconds

    # Mobile emulation
    MOBILE_DEVICE = {
        "deviceName": os.getenv("MOBILE_DEVICE", "iPhone 12")
    }

# Test configuration
class TestConfig:
    DEFAULT_LANGUAGE = os.getenv("TEST_LANGUAGE", "en")  # en or ar
    MAX_RESPONSE_TIME = int(os.getenv("MAX_RESPONSE_TIME", "10000"))  # ms
    SCREENSHOT_ON_FAILURE = os.getenv("SCREENSHOT_ON_FAILURE", "True").lower() == "true"

    # AI response validation thresholds
    MIN_RESPONSE_LENGTH = 10  # Minimum characters for valid response
    MAX_RESPONSE_TIME_AI = 30000  # Maximum time to wait for AI response (ms)

    # Retry configuration
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "2"))  # seconds

# AI Response validation thresholds
class AIValidationConfig:
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))

# Logging configuration
class LogConfig:
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = LOGS_DIR / "test_execution.log"

# Test data
TEST_DATA_FILE = DATA_DIR / "test-data.json"

# Selectors with Selenium By class
class Selectors:
    # Tuple format: (By.LOCATOR_TYPE, "locator_value")
    CHAT_WIDGET = (By.CSS_SELECTOR, "#chat-widget")
    INPUT_BOX = (By.CSS_SELECTOR, "textarea[placeholder*='Ask'], input[type='text']")
    SEND_BUTTON = (By.CSS_SELECTOR, "button[type='submit'], button[aria-label*='Send']")
    MESSAGE_CONTAINER = (By.CSS_SELECTOR, ".message-container, .chat-messages")
    USER_MESSAGE = (By.CSS_SELECTOR, ".user-message, .message.user")
    AI_RESPONSE = (By.CSS_SELECTOR, ".ai-message, .bot-message, .message.bot")
    LOADING_INDICATOR = (By.CSS_SELECTOR, ".loading, .typing-indicator")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message, .alert-error")
    LANGUAGE_SELECTOR = (By.CSS_SELECTOR, "[lang], .language-selector")