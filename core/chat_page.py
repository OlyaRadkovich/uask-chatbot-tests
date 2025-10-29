"""Chat page object with chatbot interaction methods."""
import time
import logging
from typing import List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.base_page import BasePage
from config.settings import settings
from utils.automation_helpers import AutomationHelpers

logger = logging.getLogger(__name__)


class ChatPage(BasePage):
    """Page object for chatbot interface."""
    
    # Locators
    # CSS селекторы более надежны для динамических страниц, XPath как fallback
    CHAT_INPUT = (By.CSS_SELECTOR, ".expando-textarea.chat-input-question.ask-input, .expando-textarea.chat-input-question, .chat-input-question, [contenteditable='true']")
    CHAT_INPUT_SELECTOR = (By.CSS_SELECTOR, ".expando-textarea.chat-input-question.ask-input, .expando-textarea.chat-input-question, .chat-input-question, [contenteditable='true']")  # Alias для совместимости
    SEND_BUTTON = (By.CSS_SELECTOR, "#sendButton, button[type='submit'], .send-button")
    BOT_MESSAGE = (By.CSS_SELECTOR, ".bot-message, .assistant-message, [class*='bot'], [class*='assistant']")
    ACCEPT_BUTTON = (By.XPATH, "//button[contains(text(), 'Accept')]")
    
    def __init__(self, driver):
        """Initialize chat page."""
        super().__init__(driver)
    
    def accept_disclaimer(self, timeout: int = None) -> bool:
        """Accept disclaimer modal if present (uses reliable helper)."""
        return AutomationHelpers.close_disclaimer_reliably(self.driver, max_attempts=3)
    
    def is_page_loaded(self) -> bool:
        """Check if chat page is loaded."""
        self.accept_disclaimer()
        return self.is_element_visible(self.CHAT_INPUT)
    
    def navigate(self, url: str) -> None:
        """Navigate to chat page with full setup and stealth measures."""
        super().navigate(url)
        
        # ВАЖНО: Даем время сайту "успокоиться" после навигации
        # Это помогает избежать детекции быстрых действий автоматизации
        import random
        time.sleep(random.uniform(1.5, 2.5))  # Случайная задержка имитирует пользователя
        
        # Применяем дополнительные stealth скрипты после загрузки
        try:
            self.driver.execute_script("""
                // Дополнительная защита от обнаружения после загрузки страницы
                if (navigator.webdriver) {
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                        configurable: true
                    });
                }
                
                // Скрываем элементы автоматизации из window
                delete window.navigator.__proto__.webdriver;
                
                // Эмуляция реального поведения - небольшие случайные движения мыши
                document.addEventListener('DOMContentLoaded', function() {
                    setTimeout(() => {
                        const event = new MouseEvent('mousemove', {
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: Math.random() * 100,
                            clientY: Math.random() * 100
                        });
                        document.dispatchEvent(event);
                    }, Math.random() * 1000 + 500);
                });
            """)
        except Exception:
            pass
        
        # Close disclaimer с реалистичными задержками
        time.sleep(random.uniform(0.3, 0.7))
        self.accept_disclaimer()
        
        # Close CAPTCHA modals if any (only if blocking)
        # Проверка выполняется внутри close_captcha_modals, задержка не нужна
        AutomationHelpers.close_captcha_modals(self.driver)
        
        # Wait for services to load с реалистичной задержкой
        AutomationHelpers.wait_for_services_to_load(self.driver, max_wait=15)
        
        # Final check for modals (only if blocking)
        AutomationHelpers.close_captcha_modals(self.driver)
    
    def _type_text(self, element, text: str) -> None:
        """
        Helper method to type text into input field (handles contenteditable).
        Uses realistic typing simulation to avoid bot detection.
        """
        logger.info(f"📝 Starting to type text: '{text[:50]}...'")
        
        is_contenteditable = element.get_attribute("contenteditable") == "true"
        logger.info(f"   Element type: contenteditable={is_contenteditable}, tag={element.tag_name}")
        
        if is_contenteditable:
            logger.info("   Using JavaScript method for contenteditable element")
            # Для обхода детекции используем более реалистичный метод
            # Прямая установка текста через JavaScript (самый надежный для защищенных сайтов)
            self.driver.execute_script(
                """
                var el = arguments[0];
                var txt = arguments[1];
                
                // Фокус и активация элемента (имитация клика пользователя)
                el.focus();
                el.click();
                
                // Убираем tabindex если мешает
                var hadTabindex = el.hasAttribute('tabindex') && el.getAttribute('tabindex') == '-1';
                if (hadTabindex) {
                    el.removeAttribute('tabindex');
                }
                
                // Очищаем содержимое
                el.innerText = '';
                el.textContent = '';
                el.innerHTML = '';
                
                // Фокус еще раз (важно для некоторых сайтов)
                el.focus();
                
                // Вставляем текст напрямую (наиболее надежный метод для защищенных сайтов)
                el.innerText = txt;
                el.textContent = txt;
                
                // Диспатчим события как настоящий пользователь (по порядку)
                el.dispatchEvent(new Event('focus', { bubbles: true }));
                el.dispatchEvent(new Event('input', { bubbles: true, cancelable: true }));
                el.dispatchEvent(new Event('change', { bubbles: true, cancelable: true }));
                el.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, key: 'a' }));
                el.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true, key: 'a' }));
                el.dispatchEvent(new KeyboardEvent('keypress', { bubbles: true, key: 'a' }));
                
                // Возвращаем tabindex если был
                if (hadTabindex && !el.hasAttribute('tabindex')) {
                    el.setAttribute('tabindex', '-1');
                }
                """,
                element, text
            )
            
            # Небольшая задержка для обработки событий
            time.sleep(settings.SMALL_DELAY * 2)
            
            # Проверяем что текст действительно введен
            result = self.driver.execute_script(
                "return arguments[0].innerText || arguments[0].textContent || '';",
                element
            )
            
            logger.info(f"   Text check result: '{result[:50]}...'")
            
            if not result or result.strip() != text.strip():
                logger.warning(f"⚠️ Text may not be set correctly. Expected: '{text}', Got: '{result}'")
                # Fallback: пробуем через более простой метод
                try:
                    logger.info("   Trying fallback method...")
                    self.driver.execute_script(
                        "arguments[0].focus(); arguments[0].innerText = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
                        element, text
                    )
                    time.sleep(settings.SMALL_DELAY)
                    
                    # Проверяем снова после fallback
                    result = self.driver.execute_script(
                        "return arguments[0].innerText || arguments[0].textContent || '';",
                        element
                    )
                    logger.info(f"   Fallback result: '{result[:50]}...'")
                except Exception as e:
                    logger.error(f"❌ Fallback text input failed: {e}")
            else:
                logger.info(f"✅ Text successfully entered: '{result[:50]}...'")
        else:
            logger.info("   Using standard send_keys method for regular input")
            element.clear()
            element.send_keys(text)
            
            # Проверяем результат для обычного input
            value = element.get_attribute("value") or ""
            logger.info(f"   Text entered via send_keys: '{value[:50]}...'")
    
    def send_message(self, message: str, wait_for_response: bool = True) -> None:
        """Send message to chatbot (uses reliable helpers with stealth measures)."""
        logger.info(f"Sending message: {message[:50]}...")
        
        # Случайные задержки имитируют поведение реального пользователя
        import random
        time.sleep(random.uniform(0.5, 1.0))
        
        # Close disclaimer
        self.accept_disclaimer()
        
        # Close CAPTCHA modals if any (only if blocking)
        AutomationHelpers.close_captcha_modals(self.driver)
        
        # ВАЖНО: Ждем загрузки динамического контента (реалистичная задержка)
        time.sleep(random.uniform(1.0, 1.5))
        
        # Find chat elements reliably (checks main page, iframes, Shadow DOM)
        elements = AutomationHelpers.find_chat_elements(self.driver)
        
        # Если элементы найдены в iframe, нужно переключиться на него для дальнейших действий
        if elements.get("found_in") == "iframe":
            logger.info("Chat found in iframe, elements should work within iframe context")
            # Elements уже находятся в контексте iframe из helper функции
            # Но для дальнейших действий нужно убедиться что мы в правильном контексте
            if not elements["input_found"]:
                raise ValueError("Input field not found in iframe")
            input_element = elements["input_box"]
        elif elements.get("found_in") == "shadow_dom":
            logger.info("Chat found in Shadow DOM, using JavaScript access")
            if not elements["input_found"]:
                raise ValueError("Input field not found in Shadow DOM")
            input_element = elements["input_box"]
        elif not elements["input_found"]:
            logger.warning("Input not found via helpers, trying direct selector...")
            try:
                wait = WebDriverWait(self.driver, 5, poll_frequency=0.5)
                input_element = wait.until(EC.visibility_of_element_located(self.CHAT_INPUT))
                elements["input_box"] = input_element
                elements["input_found"] = True
                elements["found_in"] = "main_page"
            except Exception as e:
                raise ValueError(f"Input field not found: {e}")
        else:
            input_element = elements["input_box"]
        
        if not elements["send_found"]:
            logger.warning("Send button not found, will try Enter key")
        
        # Type message using our reliable method
        logger.info(f"📝 Preparing to type message into input element...")
        try:
            logger.info(f"   Clicking input element first...")
            input_element.click()
            time.sleep(settings.SMALL_DELAY)
            logger.info(f"   Input element clicked, now typing text...")
        except Exception as e:
            logger.warning(f"   Click failed, trying JavaScript click: {e}")
            try:
                self.driver.execute_script("arguments[0].click();", input_element)
                time.sleep(settings.SMALL_DELAY)
            except Exception as e2:
                logger.error(f"   JavaScript click also failed: {e2}")
        
        # Вызываем _type_text с логированием
        self._type_text(input_element, message)
        
        # Verify text entered
        is_contenteditable = input_element.get_attribute("contenteditable") == "true"
        if is_contenteditable:
            actual_text = self.driver.execute_script(
                "return arguments[0].innerText || arguments[0].textContent || '';",
                input_element
            )
        else:
            actual_text = input_element.get_attribute("value") or ""
        
        if not actual_text or message.strip() not in actual_text.strip():
            logger.warning(f"Text may not be fully entered. Expected: '{message}', Got: '{actual_text}'")
        
        time.sleep(settings.SMALL_DELAY)
        
        # Send message
        if elements["send_found"]:
            elements["send_button"].click()
        else:
            input_element.send_keys(Keys.RETURN)
        
        # Close CAPTCHA if appeared after send (only if blocking)
        time.sleep(0.5)  # Короткая пауза для возможного появления CAPTCHA после отправки
        AutomationHelpers.close_captcha_modals(self.driver)
        
        if wait_for_response:
            self.wait_for_bot_response()
    
    def wait_for_bot_response(self, timeout: Optional[int] = None) -> None:
        """Wait for bot to respond."""
        wait_timeout = timeout or (settings.DEFAULT_TIMEOUT * settings.BOT_RESPONSE_TIMEOUT_MULTIPLIER)
        wait = WebDriverWait(self.driver, wait_timeout, poll_frequency=settings.POLLING_INTERVAL)
        
        def bot_response_appeared(_driver):
            try:
                return len(self.get_bot_messages()) > 0 or self.is_element_visible(
                    self.BOT_MESSAGE, 
                    timeout=settings.ELEMENT_PRESENT_TIMEOUT
                )
            except Exception:
                return False
        
        wait.until(bot_response_appeared)
    
    def get_bot_messages(self) -> List[str]:
        """Get all bot messages from chat."""
        try:
            elements = self.find_elements(self.BOT_MESSAGE)
            return [elem.text for elem in elements if elem.text.strip()]
        except Exception:
            return []
    
    def get_last_bot_message(self) -> Optional[str]:
        """Get the last bot response."""
        messages = self.get_bot_messages()
        return messages[-1] if messages else None
    
    def get_user_messages(self) -> List[str]:
        """Get all user messages from chat."""
        try:
            selector = (By.CSS_SELECTOR, ".user-message, [class*='user']")
            elements = self.find_elements(selector)
            return [elem.text for elem in elements if elem.text.strip()]
        except Exception:
            return []
    
    def is_response_received(self) -> bool:
        """Check if bot response was received."""
        return len(self.get_bot_messages()) > 0
    
    def send_keys(self, locator, text: str, timeout: int = None) -> None:
        """Send text to input element (for compatibility with tests)."""
        element = self.find_element(locator, timeout)
        self._type_text(element, text)
