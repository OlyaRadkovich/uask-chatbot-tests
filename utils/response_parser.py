"""
Utilities to robustly locate and extract chatbot responses from the DOM (renamed)
"""
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By


BOT_TEXT_XPATHS = [
    (
        "//div[contains(@class,'chat-item') and contains(@class,'chatbot') and contains(@class,'chat-message-in')]"
        "//div[contains(@class,'chat-message-text') and not(ancestor::div[contains(@class,'chat-loading-msg')])]"
    ),
    (
        "//div[contains(@class,'chatbot-container')]"
        "//div[contains(@class,'chat-message-text') and not(ancestor::div[contains(@class,'chat-loading-msg')])]"
    ),
    (
        "//div[contains(@class,'chat-item') and contains(@class,'chatbot')]"
        "//div[contains(@class,'chat-text') and not(ancestor::div[contains(@class,'chat-loading-msg')])]"
    ),
    (
        "//div[contains(@class,'chat-item') and contains(@class,'chatbot')]"
        "//*[self::p or self::li][normalize-space() and not(ancestor::div[contains(@class,'chat-loading-msg')])]"
    ),
]


def find_last_response_element(driver: WebDriver):
    for xp in BOT_TEXT_XPATHS:
        elems = driver.find_elements(By.XPATH, xp)
        if elems:
            return elems[-1]
    return None


def get_element_text(driver: WebDriver, element) -> str:
    try:
        text = driver.execute_script(
            "return (arguments[0].innerText||arguments[0].textContent||'').trim();",
            element,
        )
        if isinstance(text, str):
            return text.strip()
    except Exception:
        pass
    try:
        return (element.text or "").strip()
    except Exception:
        return ""
