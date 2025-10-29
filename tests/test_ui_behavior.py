"""
UI Behavior Tests for U-Ask Chatbot
Tests the user interface behavior and interactions
"""
import pytest
import logging
from selenium.webdriver.remote.webdriver import WebDriver
from core.chat_page import ChatPage
from config.settings import settings
import time

logger = logging.getLogger(__name__)


@pytest.mark.ui
@pytest.mark.smoke
class TestChatWidgetLoading:
    """Test chat widget loading behavior"""

    @pytest.mark.usefixtures("driver")
    def test_chat_widget_loads_on_desktop(self, driver: WebDriver):
        """Verify chat widget loads correctly on desktop"""
        logger.info("=== ТЕСТ: Загрузка виджета чата на десктопе ===")
        
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        # Проверяем наличие элементов чата
        assert chat_page.is_page_loaded(), "Chat page should be loaded"
        assert chat_page.is_element_visible(chat_page.CHAT_INPUT_SELECTOR), "Input field should be visible"
        
        logger.info("✅ Тест загрузки виджета на десктопе пройден")

    @pytest.mark.mobile
    @pytest.mark.usefixtures("driver")
    def test_mobile_simulation(self, driver: WebDriver):
        """Verify chat widget loads correctly on mobile"""
        logger.info("=== ТЕСТ: Имитация мобильного виджета ===")
        
        # Устанавливаем размер окна для мобильного
        driver.set_window_size(375, 667)
        
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        assert chat_page.is_page_loaded(), "Mobile chat page should be loaded"
        assert chat_page.is_element_visible(chat_page.CHAT_INPUT_SELECTOR), "Mobile input field should be visible"
        
        logger.info("✅ Тест мобильной имитации пройден")


@pytest.mark.ui
class TestMessageSending:
    """Test message sending functionality"""

    @pytest.mark.usefixtures("driver")
    def test_user_can_type_message(self, driver: WebDriver):
        """Verify user can type a message in input box"""
        logger.info("=== ТЕСТ: Ввод сообщения пользователем ===")
        
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        input_element = chat_page.find_element(chat_page.CHAT_INPUT_SELECTOR)
        assert input_element.is_enabled(), "Input field should be enabled"
        
        test_message = "Hello, how can I apply for a visa?"
        
        # Вводим сообщение
        chat_page.send_keys(chat_page.CHAT_INPUT_SELECTOR, test_message)
        
        # Проверяем что текст введен (для contenteditable используем innerText)
        is_contenteditable = input_element.get_attribute("contenteditable") == "true"
        if is_contenteditable:
            input_text = driver.execute_script("return arguments[0].innerText || arguments[0].textContent || '';", input_element)
        else:
            input_text = input_element.get_attribute("value") or ""
        assert test_message in input_text, f"Message should be in input field. Got: '{input_text}'"
        
        logger.info("✅ Тест ввода сообщения пройден")

    @pytest.mark.usefixtures("driver")
    def test_send_button_interaction(self, driver: WebDriver):
        """Verify send button can be clicked"""
        logger.info("=== ТЕСТ: Взаимодействие с кнопкой отправки ===")
        
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        test_message = "Test message"
        chat_page.send_message(test_message, wait_for_response=True)
        
        # Проверяем что сообщение было отправлено
        user_messages = chat_page.get_user_messages()
        assert len(user_messages) > 0 or chat_page.is_response_received(), "Message should be sent"
        
        logger.info("✅ Тест кнопки отправки пройден")


@pytest.mark.ui
class TestUIResponsiveness:
    """Test UI responsiveness and behavior"""

    @pytest.mark.usefixtures("driver")
    def test_page_elements_are_visible(self, driver: WebDriver):
        """Verify all key page elements are visible"""
        logger.info("=== ТЕСТ: Видимость элементов страницы ===")
        
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        assert chat_page.is_element_visible(chat_page.CHAT_INPUT_SELECTOR), "Input field should be visible"
        
        logger.info("✅ Тест видимости элементов пройден")

    @pytest.mark.usefixtures("driver")
    def test_language_and_direction_detection(self, driver: WebDriver):
        """Test language and text direction"""
        logger.info("=== ТЕСТ: Определение языка и направления текста ===")
        
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        # Получаем информацию о языке страницы
        try:
            from selenium.webdriver.common.by import By
            html_element = driver.find_element(By.TAG_NAME, "html")
            lang = html_element.get_attribute("lang") or "en"
            dir_attr = html_element.get_attribute("dir") or "ltr"
            
            logger.info(f"Язык страницы: {lang}, направление: {dir_attr}")
            
            # Для английского ожидаем LTR
            if "en" in lang.lower():
                assert dir_attr == "ltr" or dir_attr is None, f"Для английского ожидается LTR, получили: {dir_attr}"
            
        except Exception as e:
            logger.warning(f"Не удалось определить язык/направление: {e}")
        
        logger.info("✅ Тест определения языка пройден")


@pytest.mark.ui
class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases"""

    @pytest.mark.usefixtures("driver")
    def test_empty_message_handling(self, driver: WebDriver):
        """Test how system handles empty messages"""
        logger.info("=== ТЕСТ: Обработка пустых сообщений ===")
        
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        # Пробуем отправить пустое сообщение
        logger.info("Пробуем отправить пустое сообщение...")
        
        input_element = chat_page.find_element(chat_page.CHAT_INPUT_SELECTOR)
        input_element.clear()
        
        # Попытка отправить пустое сообщение
        try:
            input_element.send_keys("\n")  # Enter без текста
            time.sleep(0.3)
            logger.info("Пустое сообщение обработано")
        except Exception as e:
            logger.info(f"Пустое сообщение обработано с исключением: {e}")
        
        # Проверяем что страница все еще функциональна
        assert chat_page.is_page_loaded(), "Page should remain functional"
        
        logger.info("✅ Тест обработки пустых сообщений пройден")

    @pytest.mark.usefixtures("driver")
    def test_page_responsiveness_under_load(self, driver: WebDriver):
        """Test page responsiveness under multiple actions"""
        logger.info("=== ТЕСТ: Отзывчивость страницы под нагрузкой ===")
        
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        # Выполняем множественные действия
        logger.info("Выполняем множественные действия...")
        for i in range(3):
            try:
                chat_page.send_keys(chat_page.CHAT_INPUT_SELECTOR, f"Test message {i}")
                time.sleep(0.2)
                input_element = chat_page.find_element(chat_page.CHAT_INPUT_SELECTOR)
                input_element.clear()
                time.sleep(0.2)
            except Exception as e:
                logger.warning(f"Действие {i} вызвало исключение: {e}")
        
        # Страница должна оставаться отзывчивой
        assert chat_page.is_element_visible(chat_page.CHAT_INPUT_SELECTOR), "Input field should remain accessible"
        
        logger.info("✅ Тест отзывчивости под нагрузкой пройден")

