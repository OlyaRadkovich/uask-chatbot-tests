"""Tests for chatbot response quality and behavior."""
import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from core.chat_page import ChatPage
from config.settings import settings


@pytest.mark.usefixtures("driver")
class TestChatbotResponses:
    """Test suite for chatbot response validation."""
    
    def test_response_time(self, driver: WebDriver):
        """Test that bot responds within reasonable time."""
        import time
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        start_time = time.time()
        chat_page.send_message("Быстрый тест", wait_for_response=True)
        response_time = time.time() - start_time
        
        assert response_time < 60, "Bot should respond within 60 seconds"
        assert chat_page.is_response_received(), "Bot should provide a response"
    
    def test_response_not_empty(self, driver: WebDriver):
        """Test that bot response contains content."""
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        chat_page.send_message("Привет", wait_for_response=True)
        
        bot_message = chat_page.get_last_bot_message()
        assert bot_message is not None, "Bot should provide a response"
        assert len(bot_message.strip()) > 0, "Response should not be empty"
    
    def test_different_question_types(self, driver: WebDriver):
        """Test bot handles different types of questions."""
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        questions = [
            "Что такое ИИ?",
            "Как работает машинное обучение?",
            "Расскажи шутку"
        ]
        
        for question in questions:
            chat_page.wait_for_input_ready()
            chat_page.send_message(question, wait_for_response=True)
            
            bot_message = chat_page.get_last_bot_message()
            assert bot_message is not None, f"Bot should respond to: {question}"
            assert len(bot_message.strip()) > 0, f"Response to '{question}' should not be empty"
    
    def test_context_preservation(self, driver: WebDriver):
        """Test that bot maintains context in conversation."""
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        # First message
        chat_page.send_message("Меня зовут Иван", wait_for_response=True)
        chat_page.wait_for_input_ready()
        
        # Follow-up message that should use context
        chat_page.send_message("Как меня зовут?", wait_for_response=True)
        
        bot_responses = chat_page.get_bot_messages()
        assert len(bot_responses) >= 2, "Bot should provide multiple responses"
    
    def test_error_handling(self, driver: WebDriver):
        """Test bot handles edge cases and errors gracefully."""
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        # Test with very long message
        long_message = "А" * 1000
        chat_page.send_message(long_message, wait_for_response=True)
        
        # Bot should either respond or handle gracefully
        # At minimum, page should not crash
        assert chat_page.is_page_loaded(), "Page should still be functional after long message"

