"""
Page Object Model for the U-Ask Chatbot Page
"""
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException
)
from config import Selectors  # <--- THIS IS THE FIX. IMPORT THE CLASS.

# Setup logger
logger = logging.getLogger(__name__)


class ChatPage:
    """Page Object for the main chat interface"""

    def __init__(self, driver: webdriver.Remote, language: str = "en"):
        """
        Initialize the ChatPage object
        :param driver: Selenium WebDriver instance
        :param language: 'en' or 'ar'
        """
        self.driver = driver
        self.language = language
        self.wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
        self.short_wait = WebDriverWait(driver, 3)
        self.default_timeout = 20  # Default wait time
        self.locators = Selectors()  # This line will now work

    def navigate(self, url: str):
        """Navigate to the chat page URL"""
        logger.info(f"Navigating to {url}")
        self.driver.get(url)

    def wait_for_widget(self, timeout: int = 15):
        """
        Wait for the chat widget's iframe to be present
        (This assumes the chat widget is inside an iframe)
        """
        try:
            logger.info("Waiting for chat widget to load")
            # This selector is a guess. Update it with the real iframe selector.
            # If there is no iframe, wait for self.locators.INPUT_BOX instead.
            iframe_selector = (By.CSS_SELECTOR, "iframe[title='Chatbot']")
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(iframe_selector)
            )
            logger.info("Chat widget found in iframe")
        except TimeoutException:
            logger.error("Chat widget iframe did not load in time")
            raise

    def switch_to_chat_iframe(self):
        """Switch WebDriver context into the chat widget's iframe"""
        try:
            # Update this selector
            iframe_element = self.driver.find_element(By.CSS_SELECTOR, "iframe[title='Chatbot']")
            self.driver.switch_to.frame(iframe_element)
            logger.info("Switched to chat iframe context")
        except NoSuchElementException:
            logger.warning("Chat iframe not found. Assuming no iframe.")
            # If the chat is not in an iframe, this function can be skipped
            pass
        except Exception as e:
            logger.error(f"Error switching to iframe: {e}")
            raise

    def switch_to_default_content(self):
        """Switch back to the main page content"""
        self.driver.switch_to.default_content()

    def get_input_box(self):
        """Find and return the chat input box"""
        try:
            return self.wait.until(
                EC.element_to_be_clickable(self.locators.INPUT_BOX)
            )
        except TimeoutException:
            logger.error("Chat input box not found or not clickable")
            raise

    def get_send_button(self):
        """Find and return the send button"""
        try:
            return self.wait.until(
                EC.element_to_be_clickable(self.locators.SEND_BUTTON)
            )
        except TimeoutException:
            logger.error("Send button not found or not clickable")
            raise

    def send_message(self, message: str, wait_for_response: bool = True):
        """
        Type a message and click send
        :param message: The text to send
        :param wait_for_response: Whether to wait for the AI response
        """
        try:
            logger.info(f"Sending message: {message[:50]}...")
            input_box = self.get_input_box()
            input_box.clear()
            input_box.send_keys(message)

            send_button = self.get_send_button()
            send_button.click()

            if wait_for_response:
                self.wait_for_response()

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise

    def is_loading(self) -> bool:
        """Check if the AI loading indicator is visible"""
        try:
            # This is a guess. Update with the real loading selector
            loading_indicator = self.driver.find_element(*self.locators.AI_TYPING_INDICATOR)
            return loading_indicator.is_displayed()
        except NoSuchElementException:
            return False

    def wait_for_response(self, timeout: int = 30):
        """
        Wait for the AI loading indicator to appear and then disappear.
        This signals a response has started and finished.
        """
        try:
            logger.info("Waiting for AI response to start...")
            # 1. Wait for the loading indicator to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.locators.AI_TYPING_INDICATOR)
            )
            logger.info("AI response started (loading indicator found).")

            # 2. Wait for the loading indicator to disappear
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(self.locators.AI_TYPING_INDICATOR)
            )
            logger.info("AI response finished (loading indicator disappeared).")
        except TimeoutException:
            logger.warning("AI response timeout. Indicator did not appear or disappear.")
            # This might not be a failure, just a very fast response
        except Exception as e:
            logger.error(f"Error while waiting for response: {e}")

    def wait_for_stable_response(self, initial_wait: int = 1, check_interval: float = 0.5, stable_time: int = 2):
        """
        Waits for an AI response to finish "typing" by checking for text stability.
        This is more reliable than a simple loading indicator.
        """
        try:
            # Wait for the first sign of a response
            self.wait_for_response(timeout=self.default_timeout)
        except TimeoutException:
            logger.warning("Initial response indicator not found, proceeding anyway.")

        logger.info("Waiting for AI response text to stabilize...")
        last_text = ""
        stable_counter = 0
        max_checks = int(self.default_timeout / check_interval)

        for _ in range(max_checks):
            current_text = self.get_last_ai_response()
            if current_text == last_text and current_text != "":
                stable_counter += 1
            else:
                stable_counter = 0  # Reset counter if text changes

            last_text = current_text

            # If text hasn't changed for 'stable_time' seconds
            if stable_counter * check_interval >= stable_time:
                logger.info("Response text is stable.")
                return True

            time.sleep(check_interval)

        logger.warning("Response text did not stabilize in time.")
        return False


    def get_last_ai_response(self) -> str:
        """Get the text from the last AI response block"""
        try:
            messages = self.driver.find_elements(*self.locators.AI_MESSAGE)
            if messages:
                return messages[-1].text.strip()
            return ""
        except NoSuchElementException:
            logger.warning("Could not find any AI messages.")
            return ""

    def get_last_user_message(self) -> str:
        """Get the text from the last user message block"""
        try:
            messages = self.driver.find_elements(*self.locators.USER_MESSAGE)
            if messages:
                return messages[-1].text.strip()
            return ""
        except NoSuchElementException:
            logger.warning("Could not find any user messages.")
            return ""

    def close_disclaimer_reliably(self, attempts: int = 3):
        """
        Reliably find and close the disclaimer overlay.
        Handles race conditions where the overlay might not be present.
        """
        for i in range(attempts):
            try:
                self.switch_to_default_content() # Look on the main page
                disclaimer_btn = self.short_wait.until(
                    EC.element_to_be_clickable(self.locators.DISCLAIMER_BUTTON)
                )
                logger.info(f"Disclaimer found (attempt {i+1}), closing...")
                disclaimer_btn.click()
                logger.info("Disclaimer closed.")
                return
            except TimeoutException:
                logger.info("Disclaimer not found, assuming it's closed.")
                return # Not an error, it might already be gone
            except ElementClickInterceptedException:
                logger.warning("Disclaimer click intercepted, retrying...")
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error closing disclaimer: {e}")
                time.sleep(1)

    def close_captcha_modals(self, attempts: int = 2):
        """
        Reliably find and close any CAPTCHA modals that might appear.
        This simply closes the modal, it doesn't solve it.
        """
        for i in range(attempts):
            try:
                self.switch_to_default_content() # Look on the main page
                close_btn = self.short_wait.until(
                    EC.element_to_be_clickable(self.locators.CAPTCHA_CLOSE_BUTTON)
                )
                logger.info(f"CAPTCHA modal found (attempt {i+1}), closing...")
                close_btn.click()
                logger.info("CAPTCHA modal closed.")
                return
            except TimeoutException:
                logger.info("CAPTCHA modal not found.")
                return # Not an error
            except Exception as e:
                logger.error(f"Error closing CAPTCHA: {e}")
                time.sleep(1)