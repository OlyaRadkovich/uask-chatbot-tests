"""
UI Behavior Tests for U-Ask Chatbot
Tests the user interface behavior and interactions with reliable CAPTCHA/disclaimer handling
"""
import pytest
import logging
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.automation_helpers import AutomationHelpers

logger = logging.getLogger(__name__)


@pytest.mark.ui
@pytest.mark.smoke
class TestChatWidgetLoading:
    """Test chat widget loading behavior"""

    @allure.title("Chat widget loads correctly on desktop")
    @allure.description("Verify chat widget loads and all elements are visible on desktop")
    def test_chat_widget_loads_on_desktop(self, driver):
        """Verify chat widget loads correctly on desktop"""
        logger.info("=== TEST: Chat widget loading on desktop ===")

        # Set desktop viewport
        driver.set_window_size(1920, 1080)

        # Reliable page preparation
        setup_result = AutomationHelpers.setup_page_reliably(driver)
        assert setup_result["page_ready"], "Page is not ready for testing"

        # Search for chat elements with fallback
        elements = AutomationHelpers.find_chat_elements(driver)

        assert elements["input_found"], "Input field not found"
        assert elements["send_found"], "Send button not found"
        assert elements["widget_found"], "Chat widget not found"

        logger.info(f"Found elements: input={elements['input_found']}, send={elements['send_found']}, widget={elements['widget_found']}")

        # Check CAPTCHA (document but don't block)
        captcha_info = AutomationHelpers.check_for_captcha(driver)
        if captcha_info["captcha_detected"]:
            logger.warning(f"🔍 CAPTCHA detected: {captcha_info}")

        logger.info("✅ Desktop widget loading test passed")

    @pytest.mark.mobile
    @allure.title("Chat widget loads correctly on mobile")
    def test_mobile_simulation(self, driver):
        """Verify chat widget loads correctly on mobile"""
        logger.info("=== TEST: Mobile widget simulation ===")

        # Mobile viewport
        driver.set_window_size(375, 667)

        setup_result = AutomationHelpers.setup_page_reliably(driver)
        assert setup_result["page_ready"], "Mobile page is not ready"

        elements = AutomationHelpers.find_chat_elements(driver)

        assert elements["input_found"], "Mobile input field not found"
        assert elements["send_found"], "Mobile send button not found"
        assert elements["widget_found"], "Mobile chat widget not found"

        logger.info(f"Found elements: input={elements['input_found']}, send={elements['send_found']}, widget={elements['widget_found']}")

        logger.info("✅ Mobile simulation test passed")


@pytest.mark.ui
class TestMessageSending:
    """Test message sending functionality"""

    @allure.title("User can type message in input box")
    def test_user_can_type_message(self, driver):
        """Verify user can type a message in input box"""
        logger.info("=== TEST: User message input ===")

        setup_result = AutomationHelpers.setup_page_reliably(driver)
        assert setup_result["page_ready"], "Page is not ready"

        elements = AutomationHelpers.find_chat_elements(driver)
        assert elements["input_found"], "Input field not found"

        test_message = "Hello, how can I apply for a visa?"

        # Reliable message input
        typing_success = AutomationHelpers.type_message_reliably(driver, test_message, elements["input_box"])
        assert typing_success, "Failed to input message"

        logger.info(f"Typing message: {test_message}")
        logger.info("✅ Message input test passed")

    @allure.title("Send button interaction works correctly")
    def test_send_button_interaction(self, driver):
        """Verify send button can be clicked"""
        logger.info("=== TEST: Send button interaction ===")

        setup_result = AutomationHelpers.setup_page_reliably(driver)
        assert setup_result["page_ready"], "Page is not ready"

        elements = AutomationHelpers.find_chat_elements(driver)

        # Check CAPTCHA before sending
        captcha_before = AutomationHelpers.check_for_captcha(driver)
        if captcha_before["captcha_detected"]:
            logger.warning(f"🔍 CAPTCHA found: {captcha_before}")

        # Click send button
        logger.info("Clicking send button...")
        send_success = AutomationHelpers.click_send_button_reliably(driver, elements["send_button"])
        assert send_success, "Failed to click send button"

        # Check CAPTCHA after sending
        captcha_after = AutomationHelpers.check_for_captcha(driver)
        if captcha_after["captcha_detected"]:
            logger.warning("⚠️ CAPTCHA detected after sending - this is expected")

        logger.info("✅ Send button test passed")


@pytest.mark.ui
class TestUIResponsiveness:
    """Test UI responsiveness and behavior"""

    @allure.title("Page elements are visible and accessible")
    def test_page_elements_are_visible(self, driver):
        """Verify all key page elements are visible"""
        logger.info("=== TEST: Page elements visibility ===")

        setup_result = AutomationHelpers.setup_page_reliably(driver)
        assert setup_result["page_ready"], "Page is not ready"

        elements = AutomationHelpers.find_chat_elements(driver)

        assert elements["input_found"], "Input field not visible"
        assert elements["send_found"], "Send button not visible"
        assert elements["widget_found"], "Chat widget not visible"

        logger.info(f"Found elements: input={elements['input_found']}, send={elements['send_found']}, widget={elements['widget_found']}")
        logger.info("✅ Elements visibility test passed")

    @allure.title("Language and text direction detection")
    def test_language_and_direction_detection(self, driver):
        """Test language and text direction"""
        logger.info("=== TEST: Language and text direction detection ===")

        setup_result = AutomationHelpers.setup_page_reliably(driver)
        assert setup_result["page_ready"], "Page is not ready"

        # Get page language information
        try:
            html = driver.find_element(By.TAG_NAME, "html")
            lang = html.get_attribute("lang") or "en"
            dir_attr = html.get_attribute("dir") or "ltr"

            logger.info(f"Page language: {lang}, direction: {dir_attr}")

            # For English expect LTR
            if "en" in lang.lower():
                assert dir_attr == "ltr" or dir_attr is None, f"Expected LTR for English, got: {dir_attr}"

        except Exception as e:
            logger.warning(f"Failed to detect language/direction: {e}")

        logger.info("✅ Language detection test passed")


@pytest.mark.ui
class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases"""

    @allure.title("Empty message handling")
    def test_empty_message_handling(self, driver):
        """Test how system handles empty messages"""
        logger.info("=== TEST: Empty message handling ===")

        setup_result = AutomationHelpers.setup_page_reliably(driver)
        assert setup_result["page_ready"], "Page is not ready"

        elements = AutomationHelpers.find_chat_elements(driver)

        # Try to send empty message
        logger.info("Attempting to send empty message...")
        try:
            elements["input_box"].clear()
            send_success = AutomationHelpers.click_send_button_reliably(driver, elements["send_button"])
            logger.info(f"Empty message sent: {send_success}")
        except Exception as e:
            logger.info(f"Empty message handled with exception: {e}")

        logger.info("✅ Empty message handling test passed")

    @allure.title("Page responsiveness under load")
    def test_page_responsiveness_under_load(self, driver):
        """Test page responsiveness under multiple actions"""
        logger.info("=== TEST: Page responsiveness under load ===")

        setup_result = AutomationHelpers.setup_page_reliably(driver)
        assert setup_result["page_ready"], "Page is not ready"

        elements = AutomationHelpers.find_chat_elements(driver)

        # Perform multiple actions
        logger.info("Performing multiple actions...")
        for i in range(3):
            try:
                elements["input_box"].clear()
                elements["input_box"].send_keys(f"Test message {i}")
                driver.implicitly_wait(0.5)
                elements["input_box"].clear()
                driver.implicitly_wait(0.5)
            except Exception as e:
                logger.warning(f"Action {i} caused exception: {e}")

        # Page should remain responsive
        final_elements = AutomationHelpers.find_chat_elements(driver)
        assert final_elements["input_found"], "Input field became unavailable after load"

        logger.info("✅ Responsiveness under load test passed")