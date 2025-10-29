"""
Stealth Browser Configuration
Legal approaches to minimize reCAPTCHA triggers for automated testing
"""
import json
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

logger = logging.getLogger(__name__)


class StealthBrowserConfig:
    """
    Creates a browser configuration that mimics real user behavior
    to reduce reCAPTCHA triggers legally
    """

    @staticmethod
    def get_realistic_user_agent() -> str:
        """Return realistic user agent string"""
        return (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    @staticmethod
    def get_realistic_viewport() -> Dict[str, int]:
        """Return realistic viewport size"""
        return {"width": 1920, "height": 1080}

    @staticmethod
    def get_chrome_options() -> Options:
        """
        Return Chrome options that make automation look more human

        Legal approach: Configure browser to behave like a real user
        """
        options = Options()

        # Set user agent
        options.add_argument(f'user-agent={StealthBrowserConfig.get_realistic_user_agent()}')

        # Set window size
        viewport = StealthBrowserConfig.get_realistic_viewport()
        options.add_argument(f'window-size={viewport["width"]},{viewport["height"]}')

        # Additional stealth settings
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Set geolocation (New York)
        prefs = {
            'profile.default_content_setting_values.geolocation': 1,
            'profile.default_content_settings.geolocation': 1,
            'profile.content_settings.exceptions.geolocation[*]': {
                'setting': 1
            }
        }
        options.add_experimental_option('prefs', prefs)

        return options

    @staticmethod
    def create_stealth_driver() -> WebDriver:
        """
        Create a WebDriver instance with stealth configuration

        Returns:
            Configured WebDriver instance
        """
        logger.info("Creating stealth browser configuration...")

        options = StealthBrowserConfig.get_chrome_options()
        driver = webdriver.Chrome(options=options)

        # Execute stealth scripts
        StealthBrowserConfig.inject_stealth_scripts(driver)

        logger.info("✓ Stealth browser created")
        return driver

    @staticmethod
    def inject_stealth_scripts(driver: WebDriver) -> None:
        """
        Inject JavaScript to make automation less detectable

        Args:
            driver: WebDriver instance
        """
        scripts = [
            # Override navigator.webdriver
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """,

            # Add plugins
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/pdf"},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    }
                ]
            });
            """,

            # Add chrome object
            """
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            """
        ]

        for script in scripts:
            driver.execute_script(script)


class HumanBehaviorSimulator:
    """
    Simulate human-like interactions to reduce bot detection
    """

    @staticmethod
    def human_type(driver: WebDriver, selector: str, text: str, delay_ms: int = 100):
        """
        Type text with human-like delays between characters
        """
        logger.info(f"Typing with human-like delays: {text[:50]}...")
        element = driver.find_element(By.CSS_SELECTOR, selector)

        # Click with slight delay
        element.click()
        time.sleep(0.3)

        # Type character by character
        for i, char in enumerate(text):
            element.send_keys(char)
            time.sleep((delay_ms + (i % 30)) / 1000)

        logger.info("✓ Human-like typing completed")

    @staticmethod
    def human_mouse_move(driver: WebDriver, element) -> None:
        """
        Move mouse to element in a human-like way
        """
        actions = ActionChains(driver)
        actions.move_to_element(element)
        actions.perform()
        time.sleep(0.2)

    @staticmethod
    def random_scroll(driver: WebDriver):
        """
        Scroll page randomly to simulate reading behavior
        """
        logger.info("Simulating human scroll behavior...")

        driver.execute_script("window.scrollBy(0, 300)")
        time.sleep(0.5)

        driver.execute_script("window.scrollBy(0, -100)")
        time.sleep(0.3)

        driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(0.2)

        logger.info("✓ Scroll simulation completed")


class RecaptchaHelper:
    """
    Helper methods for dealing with reCAPTCHA legally
    """

    @staticmethod
    def wait_for_human_solve(driver: WebDriver, timeout_ms: int = 120000) -> bool:
        """
        Legal approach: Pause automation and let human solve reCAPTCHA
        """
        logger.warning("⏸️  reCAPTCHA DETECTED - Please solve manually")
        logger.warning("⏸️  Waiting up to 120 seconds for human intervention...")

        try:
            wait = WebDriverWait(driver, timeout_ms/1000)
            wait.until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='recaptcha']"))
            )
            logger.info("✓ reCAPTCHA solved! Continuing automation...")
            return True
        except Exception as e:
            logger.error(f"✗ Timeout waiting for reCAPTCHA solve: {e}")
            return False

    @staticmethod
    def is_recaptcha_present(driver: WebDriver) -> bool:
        """Check if reCAPTCHA is currently visible"""
        try:
            return len(driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha']")) > 0
        except:
            return False

    @staticmethod
    def load_cookies(driver: WebDriver, session_file: str) -> bool:
        """Load saved cookies from file"""
        logger.info(f"Loading cookies from {session_file}...")

        try:
            with open(session_file, 'r') as f:
                cookies = json.load(f)

            for cookie in cookies:
                driver.add_cookie(cookie)

            logger.info(f"✓ Loaded {len(cookies)} cookies")
            return True
        except Exception as e:
            logger.error(f"✗ Could not load cookies: {e}")
            return False

    @staticmethod
    def save_cookies(driver: WebDriver, session_file: str):
        """Save current cookies to file"""
        logger.info(f"Saving cookies to {session_file}...")

        cookies = driver.get_cookies()
        with open(session_file, 'w') as f:
            json.dump(cookies, f, indent=2)

        logger.info(f"✓ Saved {len(cookies)} cookies")


def create_optimal_test_browser(session_file: Optional[str] = None) -> WebDriver:
    """
    Create optimally configured browser for testing
    """
    logger.info("🔧 Creating optimal test browser...")

    driver = StealthBrowserConfig.create_stealth_driver()

    if session_file:
        RecaptchaHelper.load_cookies(driver, session_file)

    logger.info("✅ Optimal test browser ready!")
    logger.info("📌 Tips:")
    logger.info("   - Use HumanBehaviorSimulator for interactions")
    logger.info("   - Add pauses between actions")
    logger.info("   - Scroll and move mouse naturally")
    logger.info("   - Save cookies after first successful run")

    return driver