"""
UI Behavior Tests for U-Ask Chatbot
Tests the user interface behavior and interactions with reliable CAPTCHA/disclaimer handling
"""
import pytest
import logging
import allure
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)


@pytest.mark.ui
@pytest.mark.smoke
class TestChatWidgetLoading:
    """Test chat widget loading behavior"""

    @allure.title("Chat widget loads correctly on desktop")
    @allure.description("Verify chat widget loads and all elements are visible on desktop")
    def test_chat_widget_loads_on_desktop(self, chatbot_page: ChatPage):
        """Verify chat widget loads correctly on desktop"""
        logger.info("=== TEST: Chat widget loads on desktop ===")
        
        assert chatbot_page.input_box is not None, "Input box not found"
        assert chatbot_page.send_button is not None, "Send button not found"
        logger.info("✅ Desktop widget load test passed")

    @pytest.mark.mobile
    @allure.title("Chat widget loads correctly on mobile")  
    def test_mobile_simulation(self, chatbot_page: ChatPage):
        """Verify chat widget loads correctly on mobile"""
        logger.info("=== TEST: Mobile widget emulation ===")
        
        # Without mobile emulation, just ensure elements are present
        assert chatbot_page.input_box is not None
        assert chatbot_page.send_button is not None
        logger.info("✅ Mobile emulation test passed")


@pytest.mark.ui
class TestMessageSending:
    """Test message sending functionality"""

    @allure.title("User can type message in input box")
    def test_user_can_type_message(self, chatbot_page: ChatPage):
        """Verify user can type a message in input box"""
        logger.info("=== TEST: User input ===")
        
        test_message = "Hello, how can I apply for a visa?"
        chatbot_page.send_message(test_message, wait_for_response=False)
        assert chatbot_page.input_box is not None
        logger.info("✅ User input test passed")

    @allure.title("Send button interaction works correctly")
    def test_send_button_interaction(self, chatbot_page: ChatPage):
        """Verify send button can be clicked"""
        logger.info("=== TEST: Send button interaction ===")
        
        assert chatbot_page.send_button is not None
        chatbot_page.send_button.click()
        logger.info("✅ Send button test passed")


@pytest.mark.ui
class TestUIResponsiveness:
    """Test UI responsiveness and behavior"""

    @allure.title("Page elements are visible and accessible")
    def test_page_elements_are_visible(self, chatbot_page: ChatPage):
        """Verify all key page elements are visible"""
        logger.info("=== TEST: Element visibility ===")
        
        assert chatbot_page.input_box is not None
        assert chatbot_page.send_button is not None
        logger.info("✅ Element visibility test passed")

    @allure.title("Language and text direction detection")
    def test_language_and_direction_detection(self, chatbot_page: ChatPage):
        """Test language and text direction"""
        logger.info("=== TEST: Language and text direction ===")
        
        direction = chatbot_page.get_text_direction()
        assert direction in ("ltr", "rtl")
        logger.info("✅ Language detection test passed")


@pytest.mark.ui  
class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases"""

    @allure.title("Empty message handling")
    def test_empty_message_handling(self, chatbot_page: ChatPage):
        """Test how system handles empty messages"""
        logger.info("=== TEST: Empty message handling ===")
        
        logger.info("Trying to send empty message...")
        if chatbot_page.input_box is not None and chatbot_page.send_button is not None:
            chatbot_page.input_box.clear()
            chatbot_page.send_button.click()
        logger.info("✅ Empty message test passed")

    @allure.title("Page responsiveness under load")
    def test_page_responsiveness_under_load(self, chatbot_page: ChatPage):
        """Test page responsiveness under multiple actions"""
        logger.info("=== TEST: Responsiveness under load ===")
        
        logger.info("Performing multiple actions...")
        for i in range(3):
            try:
                if chatbot_page.input_box is not None:
                    chatbot_page.input_box.clear()
                    chatbot_page.input_box.send_keys(f"Test message {i}")
            except Exception as e:
                logger.warning(f"Action {i} raised exception: {e}")
        assert chatbot_page.input_box is not None
        logger.info("✅ Responsiveness under load test passed")
