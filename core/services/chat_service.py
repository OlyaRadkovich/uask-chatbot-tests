from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver

from core.use_cases.send_question import send_question, SendQuestionResult
from adapters.selenium_chat_adapter import (
    SeleniumChatPort,
    SeleniumResponseReader,
    SeleniumCaptchaPort,
)


def send_and_read(driver: WebDriver, chatbot_page, url: str, text: str) -> SendQuestionResult:
    chat = SeleniumChatPort(driver)
    reader = SeleniumResponseReader(driver)
    captcha = SeleniumCaptchaPort(driver, chatbot_page)
    return send_question(chat=chat, reader=reader, captcha=captcha, url=url, message_text=text)


