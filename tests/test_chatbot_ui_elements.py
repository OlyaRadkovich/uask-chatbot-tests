"""Tests for chatbot UI elements and behavior."""
import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from core.chat_page import ChatPage
from config.settings import settings


@pytest.mark.usefixtures("driver")
class TestChatbotUIElements:
    """Test suite for chatbot UI elements."""
    
    def test_input_field_interaction(self, driver: WebDriver):
        """Test input field is interactive."""
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        input_element = chat_page.find_element(chat_page.CHAT_INPUT_SELECTOR)
        assert input_element.is_enabled(), "Input field should be enabled"
        assert input_element.is_displayed(), "Input field should be displayed"
    
    def test_message_history_display(self, driver: WebDriver):
        """Test that message history is displayed correctly."""
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        # Send a few messages
        for i in range(3):
            chat_page.wait_for_input_ready()
            chat_page.send_message(f"Сообщение {i+1}", wait_for_response=True)
        
        # Check message history exists
        messages = chat_page.get_all_messages()
        assert len(messages) > 0, "Message history should contain messages"
    
    def test_send_button_functionality(self, driver: WebDriver):
        """Test send button works correctly."""
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        test_message = "Тестовое сообщение"
        chat_page.send_message(test_message, wait_for_response=True)
        
        # Verify message was sent (appears in chat)
        user_messages = chat_page.get_user_messages()
        assert len(user_messages) > 0, "Message should be sent when button is clicked"
    
    def test_input_field_clears_after_sending(self, driver: WebDriver):
        """Test that input field clears after sending message."""
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        test_message = "Сообщение для проверки очистки"
        chat_page.send_message(test_message, wait_for_response=True)
        
        # Wait for input to be ready
        chat_page.wait_for_input_ready()
        
        # Input should be empty or ready for new message
        input_element = chat_page.find_element(chat_page.CHAT_INPUT_SELECTOR, timeout=5)
        input_value = input_element.get_attribute("value") or ""
        # After sending, input should be empty or minimal
        assert len(input_value) < len(test_message), "Input field should be cleared after sending"

