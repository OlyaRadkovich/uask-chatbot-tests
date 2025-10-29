"""Chat page object with chatbot interaction methods."""
from typing import List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.base_page import BasePage
from config.settings import settings


class ChatPage(BasePage):
    """Page object for chatbot interface."""
    
    # Locators - используем отдельные селекторы для лучшей совместимости
    CHAT_INPUT_SELECTOR = (By.CSS_SELECTOR, "textarea, input[type='text']")
    SEND_BUTTON_CSS = (By.CSS_SELECTOR, "button[type='submit'], .send-button, button.send")
    SEND_BUTTON_XPATH = (By.XPATH, "//button[contains(text(), 'Отправить') or contains(text(), 'Send')]")
    MESSAGE_CONTAINER_SELECTOR = (By.CSS_SELECTOR, ".message, .chat-message")
    USER_MESSAGE_SELECTOR = (By.CSS_SELECTOR, ".user-message, [class*='user']")
    BOT_MESSAGE_SELECTOR = (By.CSS_SELECTOR, ".bot-message, .assistant-message, [class*='bot'], [class*='assistant']")
    LOADING_INDICATOR_SELECTOR = (By.CSS_SELECTOR, ".loading, .spinner, [class*='loading']")
    CHAT_HISTORY_SELECTOR = (By.CSS_SELECTOR, ".chat-history, .messages-container")
    
    # Disclaimer modal locators
    DISCLAIMER_MODAL_SELECTOR = (By.CSS_SELECTOR, "[class*='disclaimer'], [class*='modal'], [id*='disclaimer']")
    ACCEPT_BUTTON_XPATH = (By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Accept and continue')]")
    ACCEPT_BUTTON_CSS = (By.CSS_SELECTOR, "button:contains('Accept'), .accept-button, [aria-label*='Accept']")
    DECLINE_BUTTON_XPATH = (By.XPATH, "//button[contains(text(), 'Decline')]")
    
    def __init__(self, driver):
        """Initialize chat page."""
        super().__init__(driver)
    
    def accept_disclaimer(self, timeout: Optional[int] = None) -> bool:
        """
        Accept disclaimer modal if present.
        
        Args:
            timeout: Optional timeout override
            
        Returns:
            True if disclaimer was accepted, False if not present
        """
        try:
            wait_timeout = timeout or settings.DEFAULT_TIMEOUT
            # Проверяем наличие disclaimer модального окна
            if self.is_element_present(self.DISCLAIMER_MODAL_SELECTOR, timeout=3) or \
               self.is_element_present(self.ACCEPT_BUTTON_XPATH, timeout=3):
                
                # Пробуем найти и нажать кнопку Accept
                accept_found = False
                
                # Сначала пробуем XPath (более надежный для текстового поиска)
                if self.is_element_present(self.ACCEPT_BUTTON_XPATH, timeout=2):
                    self.click_element(self.ACCEPT_BUTTON_XPATH)
                    accept_found = True
                # Если не нашли, пробуем различные варианты селекторов
                elif self.is_element_present((By.XPATH, "//a[contains(text(), 'Accept')]"), timeout=2):
                    self.click_element((By.XPATH, "//a[contains(text(), 'Accept')]"))
                    accept_found = True
                elif self.is_element_present((By.XPATH, "//button[contains(., 'Accept')]"), timeout=2):
                    self.click_element((By.XPATH, "//button[contains(., 'Accept')]"))
                    accept_found = True
                
                if accept_found:
                    # Ждем, пока модальное окно исчезнет
                    import time
                    time.sleep(1)  # Небольшая задержка для анимации закрытия
                    return True
                
            return False
        except Exception:
            # Если возникла ошибка, продолжаем (может быть, disclaimer уже был закрыт)
            return False
    
    def is_page_loaded(self) -> bool:
        """
        Check if chat page is loaded.
        Also handles disclaimer acceptance.
        """
        # Сначала пробуем принять disclaimer, если он есть
        self.accept_disclaimer()
        
        # Затем проверяем, что поле ввода видно
        return self.is_element_visible(self.CHAT_INPUT_SELECTOR)
    
    def navigate(self, url: str) -> None:
        """
        Navigate to chat page and handle disclaimer if present.
        
        Args:
            url: URL to navigate to
        """
        # Используем базовый метод навигации
        super().navigate(url)
        
        # После навигации обрабатываем disclaimer
        import time
        time.sleep(1)  # Даем время для загрузки модального окна
        self.accept_disclaimer()
    
    def send_message(self, message: str, wait_for_response: bool = True) -> None:
        """
        Send message to chatbot.
        
        Args:
            message: Message text to send
            wait_for_response: Whether to wait for bot response
        """
        # Убеждаемся, что disclaimer принят перед отправкой сообщения
        self.accept_disclaimer(timeout=2)
        
        # Find and clear input field
        input_element = self.find_element(self.CHAT_INPUT_SELECTOR)
        input_element.clear()
        input_element.send_keys(message)
        
        # Try to find and click send button (try CSS first, then XPath)
        send_button_found = False
        if self.is_element_present(self.SEND_BUTTON_CSS, timeout=2):
            self.click_element(self.SEND_BUTTON_CSS)
            send_button_found = True
        elif self.is_element_present(self.SEND_BUTTON_XPATH, timeout=2):
            self.click_element(self.SEND_BUTTON_XPATH)
            send_button_found = True
        
        if not send_button_found:
            # Fallback: submit with Enter key
            input_element.send_keys(Keys.RETURN)
        
        # Wait for response if requested
        if wait_for_response:
            self.wait_for_bot_response()
    
    def wait_for_bot_response(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for bot to respond.
        
        Args:
            timeout: Optional timeout override
            
        Returns:
            True if response received, False otherwise
        """
        try:
            wait_timeout = timeout or settings.DEFAULT_TIMEOUT * 3  # Longer timeout for responses
            wait = WebDriverWait(self.driver, wait_timeout, poll_frequency=settings.POLLING_INTERVAL)
            
            # Wait for loading to start (if present)
            if self.is_element_present(self.LOADING_INDICATOR_SELECTOR, timeout=2):
                # Wait for loading to disappear
                self.wait_for_element_to_disappear(self.LOADING_INDICATOR_SELECTOR, timeout=wait_timeout)
            
            # Wait for bot message to appear
            def bot_response_appeared(_driver):
                try:
                    messages = self.get_bot_messages()
                    if len(messages) > 0:
                        return True
                    return self.is_element_visible(self.BOT_MESSAGE_SELECTOR, timeout=2)
                except Exception:
                    return False
            
            wait.until(bot_response_appeared)
            return True
        except Exception:
            return False
    
    def get_bot_messages(self) -> List[str]:
        """
        Get all bot messages from chat.
        
        Returns:
            List of bot message texts
        """
        messages = []
        try:
            elements = self.find_elements(self.BOT_MESSAGE_SELECTOR)
            messages = [elem.text for elem in elements if elem.text.strip()]
        except Exception:
            pass
        return messages
    
    def get_last_bot_message(self) -> Optional[str]:
        """
        Get the last bot response.
        
        Returns:
            Last bot message text or None
        """
        bot_messages = self.get_bot_messages()
        return bot_messages[-1] if bot_messages else None
    
    def get_user_messages(self) -> List[str]:
        """
        Get all user messages from chat.
        
        Returns:
            List of user message texts
        """
        messages = []
        try:
            elements = self.find_elements(self.USER_MESSAGE_SELECTOR)
            messages = [elem.text for elem in elements if elem.text.strip()]
        except Exception:
            pass
        return messages
    
    def get_all_messages(self) -> List[str]:
        """
        Get all messages (user + bot) from chat.
        
        Returns:
            List of all message texts
        """
        messages = []
        try:
            elements = self.find_elements(self.MESSAGE_CONTAINER_SELECTOR)
            messages = [elem.text for elem in elements if elem.text.strip()]
        except Exception:
            pass
        return messages
    
    def clear_chat(self) -> None:
        """Clear chat history if clear button exists."""
        clear_selectors = [
            (By.CSS_SELECTOR, ".clear-chat, .reset-chat, button[aria-label*='clear']"),
            (By.XPATH, "//button[contains(text(), 'Очистить')]"),
            (By.XPATH, "//button[contains(text(), 'Clear')]")
        ]
        
        for selector in clear_selectors:
            if self.is_element_present(selector, timeout=2):
                self.click_element(selector)
                break
    
    def is_response_received(self) -> bool:
        """Check if bot response was received."""
        return len(self.get_bot_messages()) > 0
    
    def wait_for_input_ready(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for input field to be ready for new message.
        
        Args:
            timeout: Optional timeout override
            
        Returns:
            True if input is ready, False otherwise
        """
        try:
            wait_timeout = timeout or settings.DEFAULT_TIMEOUT
            wait = WebDriverWait(self.driver, wait_timeout, poll_frequency=settings.POLLING_INTERVAL)
            wait.until(EC.element_to_be_clickable(self.CHAT_INPUT_SELECTOR))
            return True
        except Exception:
            return False

