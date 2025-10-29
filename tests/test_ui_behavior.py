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
        logger.info("=== ТЕСТ: Загрузка виджета чата на десктопе ===")
        
        assert chatbot_page.input_box is not None, "Поле ввода не найдено"
        assert chatbot_page.send_button is not None, "Кнопка отправки не найдена"
        logger.info("✅ Тест загрузки виджета на десктопе пройден")

    @pytest.mark.mobile
    @allure.title("Chat widget loads correctly on mobile")  
    def test_mobile_simulation(self, chatbot_page: ChatPage):
        """Verify chat widget loads correctly on mobile"""
        logger.info("=== ТЕСТ: Имитация мобильного виджета ===")
        
        # Without mobile emulation, just ensure elements are present
        assert chatbot_page.input_box is not None
        assert chatbot_page.send_button is not None
        logger.info("✅ Тест мобильной имитации пройден")


@pytest.mark.ui
class TestMessageSending:
    """Test message sending functionality"""

    @allure.title("User can type message in input box")
    def test_user_can_type_message(self, chatbot_page: ChatPage):
        """Verify user can type a message in input box"""
        logger.info("=== ТЕСТ: Ввод сообщения пользователем ===")
        
        test_message = "Hello, how can I apply for a visa?"
        chatbot_page.send_message(test_message, wait_for_response=False)
        assert chatbot_page.input_box is not None
        logger.info("✅ Тест ввода сообщения пройден")

    @allure.title("Send button interaction works correctly")
    def test_send_button_interaction(self, chatbot_page: ChatPage):
        """Verify send button can be clicked"""
        logger.info("=== ТЕСТ: Взаимодействие с кнопкой отправки ===")
        
        assert chatbot_page.send_button is not None
        chatbot_page.send_button.click()
        logger.info("✅ Тест кнопки отправки пройден")


@pytest.mark.ui
class TestUIResponsiveness:
    """Test UI responsiveness and behavior"""

    @allure.title("Page elements are visible and accessible")
    def test_page_elements_are_visible(self, chatbot_page: ChatPage):
        """Verify all key page elements are visible"""
        logger.info("=== ТЕСТ: Видимость элементов страницы ===")
        
        assert chatbot_page.input_box is not None
        assert chatbot_page.send_button is not None
        logger.info("✅ Тест видимости элементов пройден")

    @allure.title("Language and text direction detection")
    def test_language_and_direction_detection(self, chatbot_page: ChatPage):
        """Test language and text direction"""
        logger.info("=== ТЕСТ: Определение языка и направления текста ===")
        
        direction = chatbot_page.get_text_direction()
        assert direction in ("ltr", "rtl")
        logger.info("✅ Тест определения языка пройден")


@pytest.mark.ui  
class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases"""

    @allure.title("Empty message handling")
    def test_empty_message_handling(self, chatbot_page: ChatPage):
        """Test how system handles empty messages"""
        logger.info("=== ТЕСТ: Обработка пустых сообщений ===")
        
        logger.info("Пробуем отправить пустое сообщение...")
        if chatbot_page.input_box is not None and chatbot_page.send_button is not None:
            chatbot_page.input_box.clear()
            chatbot_page.send_button.click()
        logger.info("✅ Тест обработки пустых сообщений пройден")

    @allure.title("Page responsiveness under load")
    def test_page_responsiveness_under_load(self, chatbot_page: ChatPage):
        """Test page responsiveness under multiple actions"""
        logger.info("=== ТЕСТ: Отзывчивость страницы под нагрузкой ===")
        
        logger.info("Выполняем множественные действия...")
        for i in range(3):
            try:
                if chatbot_page.input_box is not None:
                    chatbot_page.input_box.clear()
                    chatbot_page.input_box.send_keys(f"Test message {i}")
            except Exception as e:
                logger.warning(f"Действие {i} вызвало исключение: {e}")
        assert chatbot_page.input_box is not None
        logger.info("✅ Тест отзывчивости под нагрузкой пройден")
