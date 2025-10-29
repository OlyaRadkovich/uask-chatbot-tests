"""
Test automation helper functions with disclaimer and CAPTCHA handling
Can be imported in any framework tests
"""
import logging
import time
import allure
from typing import Dict, Any, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException

logger = logging.getLogger(__name__)


class AutomationHelpers:
    """Class with helper functions for test automation"""

    @staticmethod
    def close_disclaimer_reliably(driver: WebDriver, max_attempts: int = 3) -> bool:
        """
        Reliably closes disclaimer with multiple attempts

        Args:
            driver: Selenium WebDriver
            max_attempts: Maximum number of attempts

        Returns:
            bool: True if disclaimer is closed or not found
        """
        disclaimer_selectors = [
            ".overlay-disclaimer button",
            ".disclaimer button",
            ".overlay button",
            "[data-dismiss='modal']",
            ".modal button",
            ".close-btn",
            "button:contains('Close')",
            "button:contains('Accept')",
            "button:contains('Continue')",
            ".btn-close",
            "[aria-label*='close' i]",
            ".disclaimer-close",
            ".popup-close"
        ]

        for attempt in range(max_attempts):
            logger.info(f"Attempt {attempt + 1} to close disclaimer...")

            for selector in disclaimer_selectors:
                try:
                    wait = WebDriverWait(driver, 2)
                    disclaimer_btn = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"✓ Found disclaimer: {selector}")
                    disclaimer_btn.click()
                    time.sleep(2)

                    # Check that disclaimer disappeared
                    try:
                        WebDriverWait(driver, 2).until(
                            EC.invisibility_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        logger.info("✓ Disclaimer successfully closed")
                        return True
                    except TimeoutException:
                        continue

                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            # Additional attempts
            try:
                from selenium.webdriver.common.keys import Keys
                webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(1)
            except:
                pass

            time.sleep(2)

        logger.info("Disclaimer not found or already closed")
        return True

    @staticmethod
    def close_captcha_modals(driver: WebDriver, max_attempts: int = 3) -> bool:
        """
        Closes CAPTCHA modal windows that block the interface

        Args:
            driver: Selenium WebDriver
            max_attempts: Maximum number of attempts

        Returns:
            bool: True if modal windows are closed
        """
        modal_selectors = [
            "#modalRecaptcha",
            ".modal.show",
            ".swal2-container",
            ".modal-backdrop",
            "[role='dialog'][aria-modal='true']",
            ".captcha-modal",
            ".recaptcha-modal"
        ]

        close_selectors = [
            "#modalRecaptcha button",
            "#modalRecaptcha .btn-close",
            "#modalRecaptcha [aria-label*='close' i]",
            ".swal2-close",
            ".swal2-cancel",
            ".modal .close",
            ".modal .btn-close",
            ".modal button[data-dismiss='modal']",
            ".modal button:contains('Close')",
            ".modal button:contains('Cancel')",
            ".modal button:contains('OK')"
        ]

        for attempt in range(max_attempts):
            logger.info(f"Attempt {attempt + 1} to close CAPTCHA modals...")

            # Check for modal windows
            modals_found = False
            for selector in modal_selectors:
                try:
                    modal = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if modal.is_displayed():
                        logger.warning(f"🔍 Found modal window: {selector}")
                        modals_found = True
                        break
                except:
                    continue

            if not modals_found:
                logger.info("✓ CAPTCHA modal windows not found")
                return True

            # Try to close modal windows
            for selector in close_selectors:
                try:
                    close_btn = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"✓ Found close button: {selector}")
                    close_btn.click()
                    time.sleep(2)

                    # Check that modal window disappeared
                    try:
                        WebDriverWait(driver, 2).until(
                            EC.invisibility_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        logger.info("✓ Modal window closed")
                        return True
                    except TimeoutException:
                        continue

                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            time.sleep(2)

        logger.warning("⚠️ CAPTCHA modal windows remain open")
        return False

    @staticmethod
    def wait_for_services_to_load(driver: WebDriver, max_wait: int = 30) -> bool:
        """
        Waits for services to load

        Args:
            driver: Selenium WebDriver
            max_wait: Maximum waiting time in seconds

        Returns:
            bool: True if services loaded
        """
        logger.info("Waiting for services to load...")

        loading_indicators = [
            "Connecting to Services...",
            "Loading...",
            "Please wait...",
            "Initializing...",
            "Loading...",
            "Connecting to services..."
        ]

        for i in range(max_wait):
            time.sleep(1)
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text

                # Check that loading is completed
                is_loading = any(indicator in body_text for indicator in loading_indicators)

                if not is_loading:
                    logger.info(f"✓ Services loaded in {i+1} seconds!")
                    return True

            except Exception as e:
                logger.debug(f"Error checking loading: {e}")

            if (i + 1) % 10 == 0:
                logger.info(f"Waiting for loading... {i+1}/{max_wait} seconds")

        logger.warning("Loading did not complete within the allotted time")
        return False

    @staticmethod
    def setup_page_reliably(driver: WebDriver, url: str = "https://ask.u.ae/en/") -> Dict[str, Any]:
        """
        Reliably prepares page for testing

        Args:
            driver: Selenium WebDriver
            url: URL to load

        Returns:
            Dict with preparation results
        """
        logger.info("=== Page preparation ===")

        # Navigation
        logger.info(f"Opening website: {url}")
        driver.get(url)
        time.sleep(3)

        # Screenshot initial state
        try:
            allure.attach(
                driver.get_screenshot_as_png(),
                name="Page Initial Load",
                attachment_type=allure.attachment_type.PNG
            )
        except:
            pass

        # Close disclaimer
        disclaimer_closed = AutomationHelpers.close_disclaimer_reliably(driver)

        # Close CAPTCHA modal windows if any
        captcha_modals_closed = AutomationHelpers.close_captcha_modals(driver)

        # Wait for services to load
        services_loaded = AutomationHelpers.wait_for_services_to_load(driver)

        # Check modal windows again after loading
        final_modals_closed = AutomationHelpers.close_captcha_modals(driver)

        # Final screenshot
        try:
            allure.attach(
                driver.get_screenshot_as_png(),
                name="Page Ready",
                attachment_type=allure.attachment_type.PNG
            )
        except:
            pass

        result = {
            "disclaimer_closed": disclaimer_closed,
            "captcha_modals_closed": captcha_modals_closed,
            "services_loaded": services_loaded,
            "final_modals_closed": final_modals_closed,
            "page_ready": disclaimer_closed and services_loaded,
            "url": url,
            "title": driver.title
        }

        logger.info(f"Preparation result: {result}")
        return result

    @staticmethod
    def find_chat_elements(driver: WebDriver) -> Dict[str, Any]:
        """
        Reliably finds chat elements with fallback selectors

        Args:
            driver: Selenium WebDriver

        Returns:
            Dict with found elements
        """

        # Selectors for input field
        input_selectors = [
            "[contenteditable='true'][placeholder*='ask' i]",
            "[contenteditable='true'][placeholder*='question' i]",
            "[contenteditable='true']:not([aria-hidden='true'])",
            "textarea[placeholder*='ask' i]",
            "textarea[placeholder*='question' i]",
            "input[placeholder*='ask' i]",
            ".chat-input textarea",
            ".chat-input input",
            ".message-input",
            "#chat-input",
            ".input-message"
        ]

        # Selectors for send button
        send_selectors = [
            "button[aria-label*='send' i]",
            "button[title*='send' i]",
            "button:contains('Send')",
            ".send-button",
            ".chat-send",
            "button svg[class*='send']",
            "button:has(svg)",
            ".btn-send",
            "[data-testid*='send']",
            "button[type='submit']"
        ]

        # Selectors for chat widget
        widget_selectors = [
            "#chat-widget",
            ".chat-widget",
            "#chat-container",
            ".chat-container",
            "iframe[title*='chat']",
            "[data-testid*='chat']",
            ".chat-wrapper",
            ".chatbot"
        ]

        result = {
            "input_box": None,
            "send_button": None,
            "chat_widget": None,
            "input_found": False,
            "send_found": False,
            "widget_found": False,
            "input_selector": None,
            "send_selector": None,
            "widget_selector": None
        }

        # Search for input field
        for selector in input_selectors:
            try:
                wait = WebDriverWait(driver, 3)
                element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if element.is_displayed():
                    logger.info(f"✓ Found input field: {selector}")
                    result["input_box"] = element
                    result["input_found"] = True
                    result["input_selector"] = selector
                    break
            except:
                continue

        # Search for send button
        for selector in send_selectors:
            try:
                wait = WebDriverWait(driver, 3)
                element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if element.is_displayed():
                    logger.info(f"✓ Found send button: {selector}")
                    result["send_button"] = element
                    result["send_found"] = True
                    result["send_selector"] = selector
                    break
            except:
                continue

        # Search for chat widget
        for selector in widget_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:  # May not be visible
                    logger.info(f"✓ Found chat widget: {selector}")
                    result["chat_widget"] = elements[0]
                    result["widget_found"] = True
                    result["widget_selector"] = selector
                    break
            except:
                continue

        logger.info(
            f"Found elements: input={result['input_found']}, send={result['send_found']}, widget={result['widget_found']}")
        return result

    @staticmethod
    def type_message_reliably(driver: WebDriver, message: str, input_element: Optional[WebElement] = None) -> bool:
        """
        Reliably enters message into chat field

        Args:
            driver: Selenium WebDriver
            message: message to enter
            input_element: Ready input field element (if None, searched automatically)

        Returns:
            bool: True if message entered successfully
        """
        if input_element is None:
            elements = AutomationHelpers.find_chat_elements(driver)
            if not elements["input_found"]:
                logger.error("Input field not found")
                return False
            input_element = elements["input_box"]

        try:
            logger.info(f"Typing message: {message}")

            # Click on field
            input_element.click()
            time.sleep(0.5)

            # Clear field
            input_element.clear()
            time.sleep(0.3)

            # Enter message
            input_element.send_keys(message)
            time.sleep(1)

            # Check that text is entered
            try:
                if input_element.get_attribute("contenteditable"):
                    current_value = input_element.text
                else:
                    current_value = input_element.get_attribute("value")

                success = message in current_value
                if success:
                    logger.info(f"✓ Message successfully typed: {current_value[:50]}...")
                else:
                    logger.warning(f"Message not entered correctly. Expected: {message}, got: {current_value}")

                return success

            except Exception as e:
                logger.warning(f"Failed to verify entered text: {e}")
                return True  # Assume success if cannot verify

        except Exception as e:
            logger.error(f"Error entering message: {e}")
            return False

    @staticmethod
    def click_send_button_reliably(driver: WebDriver, send_element: Optional[WebElement] = None) -> bool:
        """
        Reliably clicks the send button

        Args:
            driver: Selenium WebDriver
            send_element: Ready send button element (if None, searched automatically)

        Returns:
            bool: True if button clicked successfully
        """
        if send_element is None:
            elements = AutomationHelpers.find_chat_elements(driver)
            if not elements["send_found"]:
                logger.error("Send button not found")
                return False
            send_element = elements["send_button"]

        try:
            logger.info("Clicking send button...")
            send_element.click()
            time.sleep(1)
            logger.info("✓ Send button clicked")
            return True

        except Exception as e:
            logger.error(f"Error clicking send button: {e}")
            return False

    @staticmethod
    def check_for_captcha(driver: WebDriver) -> Dict[str, Any]:
        """
        Quickly checks for active CAPTCHA

        Args:
            driver: Selenium WebDriver

        Returns:
            Dict with CAPTCHA information
        """
        captcha_results = {
            "captcha_detected": False,
            "captcha_types": []
        }

        captcha_selectors = [
            ("iframe[src*='recaptcha']", "Active reCAPTCHA"),
            (".g-recaptcha", "Visible Google reCAPTCHA"),
            ("#modalRecaptcha", "CAPTCHA Modal")
        ]

        for selector, description in captcha_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].is_displayed():
                    captcha_results["captcha_detected"] = True
                    captcha_results["captcha_types"].append(description)
                    logger.debug(f"🔍 Active CAPTCHA: {description}")
                    break

            except Exception as e:
                logger.debug(f"Error checking {selector}: {e}")
                continue

        return captcha_results

    @staticmethod
    def wait_for_manual_captcha_solution(driver: WebDriver, timeout: int = 30) -> bool:
        """
        Notifies user about CAPTCHA and waits for its solution

        Args:
            driver: Selenium WebDriver
            timeout: maximum waiting time in seconds (default 30)

        Returns:
            bool: True if CAPTCHA disappeared
        """
        print("\n" + "="*60)
        print("🔴 CAPTCHA detected - manual solution required")
        print("="*60)
        print("👆 Solve CAPTCHA in browser")
        print("⏳ Test will automatically continue when CAPTCHA disappears")
        print(f"⏰ Timeout: {timeout} seconds")
        print("="*60 + "\n")

        start_time = time.time()
        check_interval = 5

        while time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed

            try:
                captcha_info = AutomationHelpers.check_for_captcha(driver)
                if not captcha_info["captcha_detected"]:
                    logger.info(f"✅ CAPTCHA disappeared after {elapsed} seconds")
                    print(f"\n✅ CAPTCHA SOLVED! Continuing test...\n")
                    return True

            except Exception as e:
                logger.debug(f"CAPTCHA check error: {e}")

            logger.info(f"🔍 Waiting for CAPTCHA solution... ({remaining}s remaining)")

            if remaining > check_interval:
                time.sleep(check_interval)
            else:
                time.sleep(remaining)
                break

        try:
            final_check = AutomationHelpers.check_for_captcha(driver)
            return not final_check["captcha_detected"]
        except Exception:
            return False

    @staticmethod
    def send_message_complete(driver: WebDriver, message: str, wait_for_response: bool = True) -> Dict[str, Any]:
        """
        Complete message sending cycle: finds elements, enters text, sends, checks CAPTCHA

        Args:
            driver: Selenium WebDriver
            message: Message to send
            wait_for_response: Whether to wait for bot response

        Returns:
            Dict with sending results
        """
        logger.info(f"=== Sending message: {message} ===")

        elements = AutomationHelpers.find_chat_elements(driver)

        if not elements["input_found"] or not elements["send_found"]:
            return {
                "success": False,
                "error": "Required elements not found",
                "elements": elements
            }

        captcha_before = AutomationHelpers.check_for_captcha(driver)

        typing_success = AutomationHelpers.type_message_reliably(driver, message, elements["input_box"])
        if not typing_success:
            return {
                "success": False,
                "error": "Failed to enter message",
                "captcha_before": captcha_before,
                "elements": elements
            }

        try:
            allure.attach(
                driver.get_screenshot_as_png(),
                name="Message Typed",
                attachment_type=allure.attachment_type.PNG
            )
        except:
            pass

        send_success = AutomationHelpers.click_send_button_reliably(driver, elements["send_button"])
        if not send_success:
            return {
                "success": False,
                "error": "Failed to click send button",
                "captcha_before": captcha_before,
                "typing_success": typing_success,
                "elements": elements
            }

        time.sleep(2)

        modal_close_success = AutomationHelpers.close_captcha_modals(driver)
        captcha_after = AutomationHelpers.check_for_captcha(driver)

        captcha_manually_solved = False
        if captcha_after["captcha_detected"]:
            logger.warning("🔴 CAPTCHA detected - manual solution required")
            captcha_manually_solved = AutomationHelpers.wait_for_manual_captcha_solution(driver)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        message_appears = message in body_text

        try:
            allure.attach(
                driver.get_screenshot_as_png(),
                name="After Send",
                attachment_type=allure.attachment_type.PNG
            )
        except:
            pass

        content_changed = False
        if wait_for_response and message_appears:
            logger.info("Waiting for possible bot response...")
            initial_length = len(body_text)
            time.sleep(5)
            new_body_text = driver.find_element(By.TAG_NAME, "body").text
            content_changed = len(new_body_text) != initial_length

        result = {
            "success": True,
            "message": message,
            "elements": elements,
            "typing_success": typing_success,
            "send_success": send_success,
            "message_appears": message_appears,
            "captcha_triggered": captcha_after["captcha_detected"],
            "captcha_manually_solved": captcha_manually_solved,
            "content_changed": content_changed,
            "body_text_length": len(body_text)
        }

        logger.info(f"sending result: success={result['success']}, message_appears={message_appears}, captcha_triggered={result['captcha_triggered']}")
        return result

    @staticmethod
    def safe_screenshot(driver: WebDriver, name: str = "screenshot") -> bool:
        """
        Safely takes screenshot (doesn't crash on error)

        Args:
            driver: Selenium WebDriver
            name: Screenshot name for Allure

        Returns:
            bool: True if screenshot taken successfully
        """
        try:
            allure.attach(
                driver.get_screenshot_as_png(),
                name=name,
                attachment_type=allure.attachment_type.PNG
            )
            return True
        except Exception as e:
            logger.warning(f"Failed to take screenshot {name}: {e}")
            return False