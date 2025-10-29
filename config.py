"""
Configuration file for U-Ask QA Automation Framework
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
LOGS_DIR = REPORTS_DIR / "logs"
SESSION_FILE = BASE_DIR / "session.json"  # File to save browser session (cookies)

# Create directories if they don't exist
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Application Under Test
BASE_URL = os.getenv("BASE_URL", "https://ask.u.ae")
ENGLISH_URL = f"{BASE_URL}/en/"
ARABIC_URL = f"{BASE_URL}/ar/"

# Browser configuration
class BrowserConfig:
    BROWSER_TYPE = os.getenv("BROWSER", "chromium")  # chromium, firefox, webkit
    HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
    VIEWPORT_WIDTH = int(os.getenv("VIEWPORT_WIDTH", "1920"))
    VIEWPORT_HEIGHT = int(os.getenv("VIEWPORT_HEIGHT", "1080"))
    SLOW_MO = int(os.getenv("SLOW_MO", "0"))  # Slow down operations by ms
    TIMEOUT = int(os.getenv("TIMEOUT", "30000"))  # Default timeout in ms

    # Mobile emulation
    MOBILE_DEVICE = os.getenv("MOBILE_DEVICE", "iPhone 12")  # For mobile testing

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
    # Simple similarity threshold for comparing responses (using built-in difflib)
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))  # For semantic similarity

# Logging configuration
class LogConfig:
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = LOGS_DIR / "test_execution.log"

# Test data
TEST_DATA_FILE = DATA_DIR / "test-data.json"

# Selectors (can be overridden if needed)
class Selectors:
    # These will be updated after inspecting the actual U-Ask website
    CHAT_WIDGET = "#chat-widget"
    INPUT_BOX = "textarea[placeholder*='Ask'], input[type='text']"
    SEND_BUTTON = "button[type='submit'], button[aria-label*='Send']"
    MESSAGE_CONTAINER = ".message-container, .chat-messages"
    USER_MESSAGE = ".user-message, .message.user"
    AI_RESPONSE = ".ai-message, .bot-message, .message.bot"
    LOADING_INDICATOR = ".loading, .typing-indicator"
    ERROR_MESSAGE = ".error-message, .alert-error"
    LANGUAGE_SELECTOR = "[lang], .language-selector"
