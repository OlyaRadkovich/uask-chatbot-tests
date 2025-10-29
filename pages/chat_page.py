"""
Page Object Model for U-Ask Chatbot (Selenium)
"""
from typing import Optional, List, Dict, Any
import logging
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import Selectors, TestConfig

logger = logging.getLogger(__name__)


class ChatPage:
    """Selenium-based Page Object for U-Ask chatbot interface"""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.timeout_seconds = max(1, int(TestConfig.MAX_RESPONSE_TIME / 1000))

    def _find_first(self, css_selector: str):
        """Try to find element with multiple selectors if needed."""
        selectors = css_selector.split(", ")
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector.strip())
                if element:
                    return element
            except NoSuchElementException:
                continue
        return None

    def _find_all(self, css_selector: str):
        return self.driver.find_elements(By.CSS_SELECTOR, css_selector)

    def _switch_into_chat_iframe_if_present(self) -> bool:
        """Attempt to switch into the iframe that contains the chat input and stay there.

        Returns True if already in correct context or switched successfully.
        """
        try:
            # If input is already accessible in current context, we're good
            if self._find_first(f"{Selectors.INPUT_BOX}, textarea, input[placeholder]"):
                return True

            # Always start from top before searching
            self.driver.switch_to.default_content()

            def try_switch_in_frames(frames) -> bool:
                for frame in frames:
                    try:
                        # Use Selenium's built-in wait to switch
                        WebDriverWait(self.driver, 5).until(EC.frame_to_be_available_and_switch_to_it(frame))
                    except Exception:
                        continue

                    # Check inside this frame
                    if self._find_first(f"{Selectors.INPUT_BOX}, textarea, input[placeholder]"):
                        logger.info("Switched into chat iframe")
                        return True  # Remain inside this frame

                    # Try nested frames (depth 1)
                    inner_frames = self._find_all("iframe")
                    if inner_frames:
                        if try_switch_in_frames(inner_frames):
                            return True

                    # Not found here; go back up and continue
                    self.driver.switch_to.parent_frame()

                return False

            # Prefer frames with likely attributes first
            candidate_iframes = self._find_all("iframe[title*='chat' i], iframe[src*='chat' i], iframe[id*='chat' i], iframe[class*='chat' i]")
            other_iframes = [f for f in self._find_all("iframe") if f not in candidate_iframes]

            if try_switch_in_frames(candidate_iframes) or try_switch_in_frames(other_iframes):
                return True

            # Fallback: remain at top-level
            self.driver.switch_to.default_content()
            return False
        except Exception:
            try:
                self.driver.switch_to.default_content()
            except Exception:
                pass
            return False

    @property
    def input_box(self):
        # Real selector from HTML: contenteditable div with class "expando-textarea chat-input-question"
        # Try multiple selector strategies
        selectors_to_try = [
            ".expando-textarea.chat-input-question",
            ".expando-textarea",
            ".chat-input-question",
            ".ask-input",
            "[contenteditable='true'][placeholder*='ask' i]",
            "[contenteditable='true'][placeholder*='question' i]",
            "[contenteditable='true']",
            ".textarea-container .expando-textarea",
            ".textarea-container [contenteditable='true']",
            "div[contenteditable='true'][data-placeholder]",
            "textarea",
            "input[placeholder*='ask' i]"
        ]
        for selector in selectors_to_try:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element and element.is_displayed():
                    logger.info(f"Found input box with selector: {selector}")
                    return element
            except (NoSuchElementException, Exception):
                continue
        logger.warning("Input box not found with any selector")
        return None

    @property
    def send_button(self):
        # Real selector from HTML: button#sendButton or .chat-send-btn
        selector = "#sendButton, .chat-send-btn, button[aria-label='Send'], button[aria-label*='send' i]"
        return self._find_first(selector)

    @property
    def message_container(self):
        selector = f"{Selectors.MESSAGE_CONTAINER}, .messages, [role='log']"
        return self._find_first(selector)

    @property
    def user_messages(self):
        # Real selector from HTML: .chat-message-out
        selector = ".chat-message-out, .chat-item[class*='out']"
        return self._find_all(selector)

    @property
    def ai_responses(self):
        # Real selector from HTML: take the text node of incoming bot message
        selector = ".chat-item.chatbot.chat-message-in .chat-message-text"
        return self._find_all(selector)

    @property
    def loading_indicators(self):
        selector = f"{Selectors.LOADING_INDICATOR}, .spinner, [role='progressbar']"
        return self._find_all(selector)

    @property
    def error_message(self):
        selector = f"{Selectors.ERROR_MESSAGE}, .error, [role='alert']"
        return self._find_first(selector)

    def navigate(self, url: str) -> None:
        logger.info(f"Navigating to {url}")
        self.driver.get(url)
        WebDriverWait(self.driver, self.timeout_seconds).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def wait_for_chat_widget(self, timeout: Optional[int] = None) -> None:
        wait_seconds = max(1, int((timeout or TestConfig.MAX_RESPONSE_TIME) / 1000))
        logger.info("Waiting for chat widget to load")
        try:
            # Try switching into iframe if chat is embedded
            self._switch_into_chat_iframe_if_present()
            # Wait for any of multiple indicators that chat is loaded
            WebDriverWait(self.driver, wait_seconds).until(
                lambda d: (
                    d.find_elements(By.CSS_SELECTOR, ".expando-textarea.chat-input-question") or
                    d.find_elements(By.CSS_SELECTOR, ".expando-textarea") or
                    d.find_elements(By.CSS_SELECTOR, ".chat-input-question") or
                    d.find_elements(By.CSS_SELECTOR, ".textarea-container") or
                    d.find_elements(By.CSS_SELECTOR, ".chat-container") or
                    d.find_elements(By.CSS_SELECTOR, "[contenteditable='true'][placeholder*='ask' i]")
                )
            )
            # Additional small wait to ensure element is fully rendered
            import time
            time.sleep(0.5)
        except TimeoutException as e:
            logger.error(f"Chat widget not found within {wait_seconds} seconds")
            raise e

    def send_message(self, message: str, wait_for_response: bool = True) -> None:
        logger.info(f"Sending message: {message[:50]}...")
        # Chat is directly on page, no iframe
        # Wait for input to be available with multiple strategies
        try:
            # Try to switch into iframe first if present
            self._switch_into_chat_iframe_if_present()
            WebDriverWait(self.driver, self.timeout_seconds).until(
                lambda d: (
                    d.find_elements(By.CSS_SELECTOR, ".expando-textarea.chat-input-question") or
                    d.find_elements(By.CSS_SELECTOR, ".expando-textarea") or
                    d.find_elements(By.CSS_SELECTOR, "[contenteditable='true'][placeholder*='ask' i]") or
                    d.find_elements(By.CSS_SELECTOR, "[contenteditable='true'][placeholder*='question' i]")
                )
            )
        except TimeoutException:
            logger.warning("Input not found with standard wait, trying alternative selectors")
        
        input_el = self.input_box
        if input_el is None:
            # Try one more time with explicit wait on alternative selectors
            try:
                WebDriverWait(self.driver, 5).until(
                    lambda d: d.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
                )
                input_el = self.input_box
            except TimeoutException:
                pass
        
        if input_el is None:
            raise NoSuchElementException("Input box not found. Tried multiple selectors.")
        
        # Check for CAPTCHA before sending
        captcha_before = self.check_for_captcha()
        if captcha_before["captcha_detected"]:
            logger.warning("🔴 CAPTCHA detected before sending message - waiting for manual solution")
            captcha_solved = self.wait_for_manual_captcha_solution(timeout=30)
            if captcha_solved:
                # Save session after CAPTCHA is solved
                from config import SESSION_FILE
                if self.save_session_after_captcha(SESSION_FILE):
                    logger.info("✓ Session saved after CAPTCHA solution")
                # Small pause to let the app fully unlock UI after CAPTCHA
                import time
                time.sleep(2)
        
        # For contenteditable div, use JavaScript to set text
        self.driver.execute_script("arguments[0].textContent = arguments[1]; arguments[0].innerText = arguments[1];", input_el, message)
        # Trigger input event to notify the app
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", input_el)
        send_btn = self.send_button
        if send_btn is None:
            raise NoSuchElementException("Send button not found")
        send_btn.click()
        
        # Check for CAPTCHA after sending
        import time
        time.sleep(1)  # Brief wait for any modal to appear
        captcha_after = self.check_for_captcha()
        if captcha_after["captcha_detected"]:
            logger.warning("🔴 CAPTCHA detected after sending message - waiting for manual solution")
            captcha_solved = self.wait_for_manual_captcha_solution(timeout=30)
            if captcha_solved:
                # Save session after CAPTCHA is solved
                from config import SESSION_FILE
                if self.save_session_after_captcha(SESSION_FILE):
                    logger.info("✓ Session saved after CAPTCHA solution")
                # Small pause to allow UI to update
                import time
                time.sleep(2)

        if wait_for_response:
            self.wait_for_response()

    def wait_for_response(self, timeout: Optional[int] = None) -> None:
        total_seconds = max(1, int((timeout or TestConfig.MAX_RESPONSE_TIME_AI) / 1000))
        logger.info("Waiting for AI response")
        # Chat is on main page, no iframe
        try:
            # Try to switch into iframe context if used by widget
            self._switch_into_chat_iframe_if_present()
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_any_elements_located(
                    (By.CSS_SELECTOR, ".chat-loading-div, .chatloading, [role='progressbar']")
                )
            )
        except TimeoutException:
            # Loading may be too fast, continue
            pass

        # Wait for any bot message element (exclude loading container) to appear
        bot_xpaths = [
            # Primary: explicit message text in incoming bot message
            (
                "//div[contains(@class,'chat-item') and contains(@class,'chatbot') and contains(@class,'chat-message-in')]"
                "//div[contains(@class,'chat-message-text') and not(ancestor::div[contains(@class,'chat-loading-msg')])]"
            ),
            # Fallback: any chat-message-text inside chatbot-container
            (
                "//div[contains(@class,'chatbot-container')]"
                "//div[contains(@class,'chat-message-text') and not(ancestor::div[contains(@class,'chat-loading-msg')])]"
            ),
            # Fallback: any .chat-text within bot item
            (
                "//div[contains(@class,'chat-item') and contains(@class,'chatbot')]"
                "//div[contains(@class,'chat-text') and not(ancestor::div[contains(@class,'chat-loading-msg')])]"
            ),
            # Fallback: textual paragraphs/list items inside bot item
            (
                "//div[contains(@class,'chat-item') and contains(@class,'chatbot')]"
                "//*[self::p or self::li][normalize-space() and not(ancestor::div[contains(@class,'chat-loading-msg')])]"
            ),
        ]
        # Wait for any of the above to be present
        WebDriverWait(self.driver, total_seconds).until(
            lambda d: any(d.find_elements(By.XPATH, xp) for xp in bot_xpaths)
        )

        # Now wait until the last bot message has non-empty text and stabilizes
        import time
        last_text = ""
        stable_checks = 0
        end_time = time.time() + total_seconds
        while time.time() < end_time:
            # Gather candidates from all xpaths
            elems = []
            for xp in bot_xpaths:
                found = self.driver.find_elements(By.XPATH, xp)
                if found:
                    elems.extend(found)
            if elems:
                last_el = elems[-1]
                try:
                    current_text = (self.driver.execute_script(
                        "return (arguments[0].innerText||arguments[0].textContent||'').trim();",
                        last_el,
                    ) or "").strip()
                except Exception:
                    current_text = ""

                if current_text:
                    if current_text == last_text:
                        stable_checks += 1
                        if stable_checks >= 2:  # text unchanged in two consecutive checks
                            return
                    else:
                        stable_checks = 0
                        last_text = current_text
            else:
                # Try to scroll a bit to force lazy rendering
                try:
                    self.driver.execute_script("window.scrollBy(0, 300)")
                except Exception:
                    pass
            time.sleep(0.5)
        logger.warning("Response did not stabilize within allotted time; proceeding anyway")
        # Diagnostic: capture screenshot and small DOM dump to help debugging
        try:
            self.take_screenshot("response_wait_timeout")
        except Exception:
            pass

    def get_last_ai_response(self) -> str:
        bot_xpaths = [
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
        responses = []
        for xp in bot_xpaths:
            found = self.driver.find_elements(By.XPATH, xp)
            if found:
                responses.extend(found)
        if not responses:
            logger.warning("No AI responses found")
            return ""
        last_el = responses[-1]
        # Try innerText/textContent to include any HTML content rendered
        try:
            text = (self.driver.execute_script(
                "return (arguments[0].innerText||arguments[0].textContent||'').trim();",
                last_el,
            ) or "").strip()
        except Exception:
            text = (last_el.text or "").strip()
        logger.info(f"Last response: {text[:100]}...")
        return text

    def get_all_ai_responses(self) -> List[str]:
        return [el.text for el in self.ai_responses]

    def get_last_user_message(self) -> str:
        messages = self.user_messages
        return messages[-1].text if messages else ""

    def is_input_cleared(self) -> bool:
        el = self.input_box
        if el is None:
            return True
        # For contenteditable div, check textContent or innerText
        text = el.text or el.get_attribute("textContent") or ""
        return len(text.strip()) == 0

    def get_text_direction(self) -> str:
        direction = None
        try:
            direction = self.driver.execute_script("return document.dir || document.documentElement.dir")
        except Exception:
            pass
        return direction or "ltr"

    def is_rtl_layout(self) -> bool:
        return self.get_text_direction() == "rtl"

    def scroll_to_bottom(self) -> None:
        try:
            container = self.message_container
            if container is not None:
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", container)
            else:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except Exception:
            pass

    def get_message_count(self) -> dict:
        return {"user": len(self.user_messages), "ai": len(self.ai_responses)}

    def is_error_displayed(self) -> bool:
        el = self.error_message
        return bool(el and el.is_displayed())

    def get_error_message(self) -> str:
        el = self.error_message
        return el.text if el and el.is_displayed() else ""

    def is_loading(self) -> bool:
        try:
            return any(ind.is_displayed() for ind in self.loading_indicators)
        except Exception:
            return False

    def take_screenshot(self, name: str) -> str:
        from config import SCREENSHOTS_DIR
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename
        logger.info(f"Taking screenshot: {filepath}")
        self.driver.save_screenshot(str(filepath))
        return str(filepath)

    def check_accessibility(self) -> dict:
        results = {"has_labels": False, "has_aria_attributes": False, "keyboard_navigable": False}
        try:
            el = self.input_box
            if el:
                aria_label = el.get_attribute("aria-label")
                placeholder = el.get_attribute("placeholder")
            results["has_labels"] = bool(aria_label or placeholder)
        except Exception:
            pass
        try:
            container = self.message_container
            if container:
                role = container.get_attribute("role")
            results["has_aria_attributes"] = bool(role)
        except Exception:
            pass
        try:
            btn = self.send_button
            if btn:
                tabindex = btn.get_attribute("tabindex")
                results["keyboard_navigable"] = tabindex is None or int(tabindex) >= 0
        except Exception:
            pass
        return results

    def wait_for_stable_response(self, timeout: int = 5000) -> None:
        logger.info("Waiting for response to stabilize")
        previous_text = ""
        stable_count = 0
        checks = max(1, timeout // 500)
        for _ in range(checks):
            current_text = self.get_last_ai_response()
            if current_text == previous_text and len(current_text) > 0:
                stable_count += 1
                if stable_count >= 3:
                    return
            else:
                stable_count = 0
            previous_text = current_text
            WebDriverWait(self.driver, 0.5).until(lambda d: True)

    def close_disclaimer_reliably(self, max_attempts: int = 3) -> bool:
        """Attempt to close disclaimer/overlay modals with multiple selectors."""
        selectors = [
            ".overlay-disclaimer button",
            ".disclaimer button",
            ".overlay button",
            "[data-dismiss='modal']",
            ".modal button",
            ".close-btn",
            "button[aria-label*='close' i]",
            ".btn-close",
            ".disclaimer-close",
            ".popup-close",
            "button:contains('Close')",
            "button:contains('Accept')",
            "button:contains('Continue')",
        ]

        for attempt in range(max_attempts):
            logger.info(f"Attempt {attempt + 1} to close disclaimer")
            # Try buttons
            for css in selectors:
                try:
                    elems = self._find_all(css)
                    for el in elems:
                        if el.is_displayed() and el.is_enabled():
                            try:
                                el.click()
                                WebDriverWait(self.driver, 1).until(lambda d: True)
                                return True
                            except Exception:
                                continue
                except Exception:
                    continue

            # Try pressing Escape
            try:
                self.driver.switch_to.active_element
                self.driver.execute_script("document.dispatchEvent(new KeyboardEvent('keydown', {key:'Escape'}));")
            except Exception:
                pass

            # Try clicking overlays/backdrops
            try:
                overlays = self._find_all(".overlay, .modal-backdrop, .swal2-container")
                for ov in overlays:
                    if ov.is_displayed():
                        try:
                            self.driver.execute_script("arguments[0].click();", ov)
                            WebDriverWait(self.driver, 1).until(lambda d: True)
                            return True
                        except Exception:
                            continue
            except Exception:
                pass

        logger.info("Disclaimer not found or already closed")
        return True

    def check_for_captcha(self) -> Dict[str, Any]:
        """
        Check if CAPTCHA is currently visible/active
        
        Returns:
            Dict with captcha_detected boolean and captcha_types list
        """
        captcha_results = {
            "captcha_detected": False,
            "captcha_types": []
        }
        
        # Check for CAPTCHA modal (from HTML: #modalRecaptcha)
        captcha_selectors = [
            ("#modalRecaptcha", "CAPTCHA Modal"),
            (".modal#modalRecaptcha", "CAPTCHA Modal"),
            ("iframe[src*='recaptcha']", "reCAPTCHA iframe"),
            (".g-recaptcha", "Google reCAPTCHA"),
        ]
        
        for selector, description in captcha_selectors:
            try:
                elements = self._find_all(selector)
                if elements:
                    # Check if any element is visible
                    for el in elements:
                        try:
                            if el.is_displayed():
                                captcha_results["captcha_detected"] = True
                                captcha_results["captcha_types"].append(description)
                                logger.debug(f"Active CAPTCHA detected: {description}")
                                break
                        except Exception:
                            continue
                    if captcha_results["captcha_detected"]:
                        break
            except Exception:
                continue
        
        return captcha_results

    def wait_for_manual_captcha_solution(self, timeout: int = 30) -> bool:
        """
        Wait for user to manually solve CAPTCHA
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if CAPTCHA was solved (disappeared)
        """
        import time
        
        print("\n" + "="*60)
        print("🔴 CAPTCHA detected - manual solution required")
        print("="*60)
        print("👆 Solve CAPTCHA in browser window")
        print("⏳ Test will automatically continue when CAPTCHA disappears")
        print(f"⏰ Timeout: {timeout} seconds")
        print("="*60 + "\n")
        
        start_time = time.time()
        check_interval = 2
        
        while time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            
            captcha_info = self.check_for_captcha()
            if not captcha_info["captcha_detected"]:
                logger.info(f"✅ CAPTCHA solved after {elapsed} seconds")
                print(f"\n✅ CAPTCHA SOLVED! Continuing test...\n")
                return True
            
            if elapsed % 5 == 0:  # Log every 5 seconds
                logger.info(f"Waiting for CAPTCHA solution... ({remaining}s remaining)")
            
            time.sleep(check_interval)
        
        # Final check
        captcha_info = self.check_for_captcha()
        if not captcha_info["captcha_detected"]:
            logger.info("✅ CAPTCHA solved at the last moment")
            print(f"\n✅ CAPTCHA SOLVED! Continuing test...\n")
            return True
        
        logger.warning(f"⏰ CAPTCHA not solved within {timeout} seconds")
        print(f"\n⏰ Time expired - continuing test\n")
        return False

    def save_session_after_captcha(self, session_file_path) -> bool:
        """
        Save browser session after CAPTCHA is solved
        
        Args:
            session_file_path: Path where to save session file
            
        Returns:
            True if saved successfully
        """
        from utils.session_manager import SessionManager
        from pathlib import Path
        
        return SessionManager.save_session(self.driver, Path(session_file_path))
