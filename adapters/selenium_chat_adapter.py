from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.domain.messages import UserMessage, BotMessage
from core.domain.ports import ChatPort, ResponseReaderPort, CaptchaPort
from utils.response_parser import find_last_response_element, get_element_text


class SeleniumChatPort(ChatPort):
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def navigate(self, url: str) -> None:
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def ensure_ready(self, timeout_ms: int) -> None:
        WebDriverWait(self.driver, max(1, timeout_ms // 1000)).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".textarea-container, .chat-container"))
        )

    def type_and_send(self, message: UserMessage) -> None:
        # Use known selectors
        input_sel = ".expando-textarea.chat-input-question, [contenteditable='true']"
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, input_sel))
        )
        el = self.driver.find_element(By.CSS_SELECTOR, input_sel)
        self.driver.execute_script(
            "arguments[0].textContent = arguments[1]; arguments[0].innerText = arguments[1];",
            el,
            message.text,
        )
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles:true}));", el)
        send_btn = self.driver.find_element(By.CSS_SELECTOR, "#sendButton, .chat-send-btn")
        send_btn.click()


class SeleniumResponseReader(ResponseReaderPort):
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def wait_for_response(self, timeout_ms: int) -> None:
        timeout_s = max(1, timeout_ms // 1000)
        WebDriverWait(self.driver, timeout_s).until(
            lambda d: find_last_response_element(d) is not None
        )

    def read_last(self) -> Optional[BotMessage]:
        el = find_last_response_element(self.driver)
        if not el:
            return None
        text = get_element_text(self.driver, el)
        return BotMessage(text=text)


class SeleniumCaptchaPort(CaptchaPort):
    def __init__(self, driver: WebDriver, chatbot_page):
        self.driver = driver
        self.chatbot_page = chatbot_page

    def detected(self) -> bool:
        info = self.chatbot_page.check_for_captcha()
        return bool(info.get("captcha_detected"))

    def wait_until_solved(self, timeout_sec: int) -> bool:
        return self.chatbot_page.wait_for_manual_captcha_solution(timeout=timeout_sec)

    def save_session(self) -> bool:
        from config import SESSION_FILE
        return self.chatbot_page.save_session_after_captcha(SESSION_FILE)


