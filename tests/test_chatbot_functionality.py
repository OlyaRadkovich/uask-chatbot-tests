"""Tests for chatbot core functionality."""
import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from core.chat_page import ChatPage
from config.settings import settings


@pytest.mark.usefixtures("driver")
class TestChatbotFunctionality:
    """Test suite for chatbot functionality."""
    
    def test_chat_page_loads(self, driver: WebDriver):
        """Test that chat page loads correctly."""
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        assert chat_page.is_page_loaded(), "Chat page should be loaded"
        assert chat_page.is_element_visible(chat_page.CHAT_INPUT_SELECTOR), "Input field should be visible"
    
    def test_send_simple_message(self, driver: WebDriver):
        """Test sending a simple message to chatbot."""
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        test_message = "Привет, как дела?"
        chat_page.send_message(test_message, wait_for_response=True)
        
        user_messages = chat_page.get_user_messages()
        assert any(test_message in msg for msg in user_messages), "User message should appear in chat"
    
    def test_receive_bot_response(self, driver: WebDriver):
        """Test that bot responds to messages."""
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        chat_page.send_message("Что ты умеешь?", wait_for_response=True)
        
        assert chat_page.is_response_received(), "Bot should send a response"
        bot_message = chat_page.get_last_bot_message()
        assert bot_message is not None, "Bot message should not be empty"
        assert len(bot_message.strip()) > 0, "Bot message should contain text"
    
    def test_multiple_messages_exchange(self, driver: WebDriver):
        """Test multiple message exchange with bot."""
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        messages = [
            "Расскажи о себе",
            "Какие функции доступны?",
            "Спасибо за помощь"
        ]
        
        for message in messages:
            chat_page.wait_for_input_ready()
            chat_page.send_message(message, wait_for_response=True)
            assert chat_page.is_response_received(), f"Bot should respond to: {message}"
        
        # Verify all messages are in chat
        all_messages = chat_page.get_all_messages()
        assert len(all_messages) >= len(messages) * 2, "Chat should contain all messages and responses"

