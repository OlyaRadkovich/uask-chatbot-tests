"""
Test automation helper functions adapted from Playwright to Selenium
Disclaimer, CAPTCHA handling and reliable interactions
"""
import logging
import time
from typing import Dict, Any, Optional, List
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config.settings import settings

logger = logging.getLogger(__name__)


class AutomationHelpers:
    """Helper functions for test automation with Selenium"""
    
    @staticmethod
    def close_disclaimer_reliably(driver: WebDriver, max_attempts: int = 3) -> bool:
        """
        Reliably closes disclaimer with multiple attempts.
        
        Args:
            driver: WebDriver instance
            max_attempts: Maximum number of attempts
            
        Returns:
            bool: True if disclaimer is closed or not found
        """
        # Только один локатор как указано пользователем
        disclaimer_selector = (By.XPATH, "/html/body/div[1]/div/div/button")
        
        for attempt in range(max_attempts):
            logger.info(f"Attempt {attempt + 1}/{max_attempts} to close disclaimer...")
            
            try:
                wait = WebDriverWait(driver, settings.DISCLAIMER_TIMEOUT, poll_frequency=settings.POLLING_INTERVAL)
                disclaimer_btn = wait.until(EC.element_to_be_clickable(disclaimer_selector))
                if disclaimer_btn.is_displayed():
                    logger.info(f"✓ Found disclaimer button")
                    disclaimer_btn.click()
                    logger.info("✓ Clicked disclaimer button")
                    time.sleep(settings.SMALL_DELAY)
                    
                    # Check that disclaimer disappeared
                    try:
                        wait.until(EC.invisibility_of_element_located(disclaimer_selector))
                        logger.info("✓ Disclaimer successfully closed and disappeared")
                        logger.info("📋 Next step: Waiting for chat elements to be available...")
                        return True
                    except TimeoutException:
                        logger.debug("⚠️ Disclaimer button still visible after click, trying again...")
                        time.sleep(settings.MEDIUM_DELAY)
                        continue
                        
            except (NoSuchElementException, TimeoutException) as e:
                logger.debug(f"Disclaimer button not found (attempt {attempt + 1}): {e}")
                if attempt < max_attempts - 1:
                    time.sleep(settings.MEDIUM_DELAY)
                    continue
                else:
                    logger.info("✓ Disclaimer not found or already closed - proceeding")
                    return True
        
        logger.info("✓ Disclaimer handling completed")
        return True
    
    @staticmethod
    def close_captcha_modals(driver: WebDriver, max_attempts: int = 3, wait_for_manual: bool = True) -> bool:
        """
        Closes CAPTCHA modal windows that block the interface.
        Enhanced to detect and handle reCAPTCHA more reliably.
        If modalRecaptcha is detected, waits for manual solution by user.
        
        Args:
            driver: WebDriver instance
            max_attempts: Maximum number of attempts (not used if manual solve)
            wait_for_manual: If True, waits for user to manually solve modalRecaptcha
            
        Returns:
            bool: True if modal windows are closed or not found
        """
        # ВАЖНО: Сначала проверяем, есть ли modalRecaptcha (требует ручного решения)
        try:
            modal_recaptcha = driver.find_element(By.ID, "modalRecaptcha")
            style = driver.execute_script("""
                var el = arguments[0];
                var style = window.getComputedStyle(el);
                return style.display !== 'none' && style.visibility !== 'hidden';
            """, modal_recaptcha)
            
            if style:
                if wait_for_manual:
                    logger.warning("🔴 modalRecaptcha detected - waiting for manual solution...")
                    logger.warning("=" * 60)
                    logger.warning("👆 PLEASE SOLVE THE CAPTCHA IN THE BROWSER WINDOW")
                    logger.warning("⏳ Automation will continue automatically when CAPTCHA is solved")
                    logger.warning("=" * 60)
                    print("\n" + "=" * 60)
                    print("🔴 CAPTCHA DETECTED - MANUAL SOLUTION REQUIRED")
                    print("=" * 60)
                    print("👆 Solve the CAPTCHA in the browser window")
                    print("⏳ Test will automatically continue when CAPTCHA disappears")
                    print("=" * 60 + "\n")
                    
                    # Ждем ручного решения
                    return AutomationHelpers.wait_for_manual_captcha_solution(driver, timeout=120)
                else:
                    logger.info("modalRecaptcha found but wait_for_manual=False, skipping")
                    return True
        except (NoSuchElementException, TimeoutException):
            pass  # modalRecaptcha не найден, продолжаем обычную проверку
        except Exception as e:
            logger.debug(f"Error checking modalRecaptcha: {e}")
        
        # ВАЖНО: Сначала проверяем, есть ли CAPTCHA модальные окна (обычная проверка)
        captcha_info = AutomationHelpers.check_for_captcha(driver)
        
        # Если CAPTCHA не найдена или не блокирует - сразу возвращаемся
        if not captcha_info["captcha_detected"]:
            logger.debug("No CAPTCHA detected, skipping modal close")
            return True
        
        if not (captcha_info["blocking"] or captcha_info["visible"]):
            logger.debug(f"CAPTCHA detected but not blocking (hidden), skipping modal close")
            return True
        
        # Только если CAPTCHA блокирует - пробуем закрыть
        logger.info(f"CAPTCHA detected and blocking, attempting to close modals...")
        
        # Сначала проверяем через JavaScript для более точного определения
        try:
            has_modal = driver.execute_script("""
                var modal = document.getElementById('modalRecaptcha');
                if (modal) {
                    var style = window.getComputedStyle(modal);
                    return style.display !== 'none' && style.visibility !== 'hidden';
                }
                return false;
            """)
            
            if has_modal:
                logger.info("🔍 Found modalRecaptcha via JavaScript")
        except:
            pass
        
        modal_selectors = [
            (By.ID, "modalRecaptcha"),
            (By.CSS_SELECTOR, ".modal.show"),
            (By.CSS_SELECTOR, ".swal2-container"),
            (By.CSS_SELECTOR, ".modal-backdrop"),
            (By.CSS_SELECTOR, "[role='dialog'][aria-modal='true']"),
            (By.CSS_SELECTOR, ".captcha-modal"),
            (By.CSS_SELECTOR, ".recaptcha-modal"),
            (By.CSS_SELECTOR, ".grecaptcha-badge")  # Badge также может блокировать
        ]
        
        close_selectors = [
            (By.CSS_SELECTOR, "#modalRecaptcha button"),
            (By.CSS_SELECTOR, "#modalRecaptcha .btn-close"),
            (By.CSS_SELECTOR, "#modalRecaptcha [aria-label*='close' i]"),
            (By.CSS_SELECTOR, ".swal2-close"),
            (By.CSS_SELECTOR, ".swal2-cancel"),
            (By.CSS_SELECTOR, ".modal .close"),
            (By.CSS_SELECTOR, ".modal .btn-close"),
            (By.CSS_SELECTOR, ".modal button[data-dismiss='modal']"),
            (By.XPATH, "//button[contains(text(), 'Close')]"),
            (By.XPATH, "//button[contains(text(), 'Cancel')]"),
            (By.XPATH, "//button[contains(text(), 'OK')]")
        ]
        
        for attempt in range(max_attempts):
            logger.info(f"Attempt {attempt + 1} to close CAPTCHA modals...")
            
            # Check for modal windows
            modals_found = False
            for by, selector in modal_selectors:
                try:
                    element = driver.find_element(by, selector)
                    if element.is_displayed():
                        logger.warning(f"🔍 Found modal window: {selector}")
                        modals_found = True
                        break
                except (NoSuchElementException, TimeoutException):
                    continue
            
            if not modals_found:
                logger.info("✓ CAPTCHA modal windows not found")
                return True
            
            # Try to close modal windows
            for by, selector in close_selectors:
                try:
                    wait = WebDriverWait(driver, 2, poll_frequency=0.3)
                    close_btn = wait.until(EC.element_to_be_clickable((by, selector)))
                    if close_btn.is_displayed():
                        logger.info(f"✓ Found close button: {selector}")
                        close_btn.click()
                        time.sleep(2)
                        
                        # Check that modal window disappeared
                        try:
                            wait.until(EC.invisibility_of_element_located((by, selector)))
                            logger.info("✓ Modal window closed")
                            return True
                        except TimeoutException:
                            pass
                            
                except (TimeoutException, NoSuchElementException):
                    continue
            
            # Additional attempts
            try:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                time.sleep(1)
                
                backdrop = driver.find_element(By.CSS_SELECTOR, ".modal-backdrop, .swal2-backdrop")
                if backdrop.is_displayed():
                    backdrop.click()
                    time.sleep(1)
            except:
                pass
            
            time.sleep(2)
        
        logger.warning("⚠️ CAPTCHA modal windows remain open")
        return False
    
    @staticmethod
    def wait_for_services_to_load(driver: WebDriver, max_wait: int = 30) -> bool:
        """
        Waits for services to load.
        
        Args:
            driver: WebDriver instance
            max_wait: Maximum waiting time in seconds
            
        Returns:
            bool: True if services loaded
        """
        logger.info("Waiting for services to load...")
        
        loading_indicators = [
            "Connecting to Services...",
            "Loading...",
            "Please wait...",
            "Initializing...",
            "Connecting to services..."
        ]
        
        for i in range(max_wait):
            time.sleep(1)
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text
                
                # Check that loading is completed
                is_loading = any(indicator in body_text for indicator in loading_indicators)
                
                if not is_loading:
                    logger.info(f"✓ Services loaded in {i+1} seconds!")
                    return True
                    
            except Exception as e:
                logger.debug(f"Error checking loading: {e}")
                
            if (i + 1) % 10 == 0:
                logger.info(f"Waiting for loading... {i+1}/{max_wait} seconds")
        
        logger.warning("Loading did not complete within the allotted time")
        return False
    
    @staticmethod
    def find_iframes(driver: WebDriver) -> List[Any]:
        """
        Find all iframes on the page that might contain chat.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            List of iframe elements
        """
        try:
            wait = WebDriverWait(driver, 3, poll_frequency=0.3)
            iframes = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "iframe")))
            logger.info(f"Found {len(iframes)} iframes on page")
            return iframes
        except Exception as e:
            logger.debug(f"No iframes found or error: {e}")
            return []
    
    @staticmethod
    def find_elements_in_shadow_dom(driver: WebDriver, shadow_host_selector: str, inner_selector: str) -> List[Any]:
        """
        Find elements inside Shadow DOM.
        
        Args:
            driver: WebDriver instance
            shadow_host_selector: CSS selector for shadow host element
            inner_selector: CSS selector for element inside shadow DOM
            
        Returns:
            List of found elements
        """
        try:
            result = driver.execute_script(f"""
                var host = document.querySelector('{shadow_host_selector}');
                if (!host || !host.shadowRoot) return null;
                return host.shadowRoot.querySelectorAll('{inner_selector}');
            """)
            return result if result else []
        except Exception as e:
            logger.debug(f"Shadow DOM search failed: {e}")
            return []
    
    @staticmethod
    def find_chat_elements_in_iframe(driver: WebDriver, iframe) -> Dict[str, Any]:
        """
        Find chat elements inside a specific iframe.
        
        Args:
            driver: WebDriver instance
            iframe: iframe WebElement
            
        Returns:
            Dict with found elements or empty dict if not found
        """
        original_frame = None
        try:
            # Сохраняем текущий контекст
            original_frame = driver.current_window_handle
            
            # Переключаемся на iframe
            driver.switch_to.frame(iframe)
            logger.info(f"Switched to iframe: {iframe.get_attribute('src') or 'no src'}")
            
            # Пробуем найти элементы внутри iframe
            input_selectors = [
                (By.CSS_SELECTOR, ".expando-textarea.chat-input-question.ask-input"),
                (By.CSS_SELECTOR, ".expando-textarea.chat-input-question"),
                (By.CSS_SELECTOR, ".chat-input-question"),
                (By.CSS_SELECTOR, "[contenteditable='true']"),
                (By.CSS_SELECTOR, "textarea"),
                (By.CSS_SELECTOR, "input[type='text']")
            ]
            
            send_selectors = [
                (By.ID, "sendButton"),
                (By.CSS_SELECTOR, ".send-button"),
                (By.CSS_SELECTOR, "button[type='submit']")
            ]
            
            # Ищем input
            input_element = None
            input_selector = None
            for by, selector in input_selectors:
                try:
                    wait = WebDriverWait(driver, 2, poll_frequency=0.3)
                    element = wait.until(EC.visibility_of_element_located((by, selector)))
                    if element.is_displayed():
                        input_element = element
                        input_selector = selector
                        logger.info(f"✓ Found input in iframe: {selector}")
                        break
                except:
                    continue
            
            # Ищем send button
            send_element = None
            send_selector = None
            for by, selector in send_selectors:
                try:
                    wait = WebDriverWait(driver, 2, poll_frequency=0.3)
                    element = wait.until(EC.visibility_of_element_located((by, selector)))
                    if element.is_displayed():
                        send_element = element
                        send_selector = selector
                        logger.info(f"✓ Found send button in iframe: {selector}")
                        break
                except:
                    continue
            
            if input_element:
                return {
                    "input_box": input_element,
                    "send_button": send_element,
                    "input_found": True,
                    "send_found": send_element is not None,
                    "input_selector": input_selector,
                    "send_selector": send_selector,
                    "found_in": "iframe"
                }
            
        except Exception as e:
            logger.debug(f"Error searching in iframe: {e}")
        finally:
            # ВАЖНО: Возвращаемся в основной контекст
            try:
                driver.switch_to.default_content()
            except:
                pass
        
        return {}
    
    @staticmethod
    def find_chat_elements(driver: WebDriver) -> Dict[str, Any]:
        """
        Reliably finds chat elements with fallback selectors.
        Checks main page, iframes, and Shadow DOM.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            Dict with found elements
        """
        # Только один локатор как указано пользователем
        input_selector = (By.XPATH, "/html/body/div[1]/div/div/div[3]/div/div[1]/div[1]")
        
        # Priority selectors for send button (most specific first)
        # Обновлено на основе реального HTML и Playwright селекторов
        send_selectors = [
            # Из реального HTML - самый точный ID
            (By.ID, "sendButton"),
            # По классам
            (By.CSS_SELECTOR, ".chat-send-btn"),
            (By.CSS_SELECTOR, ".send-button"),
            (By.CSS_SELECTOR, ".btn-send"),
            # По атрибутам (из исходника)
            (By.CSS_SELECTOR, "button[aria-label*='send' i]"),
            (By.CSS_SELECTOR, "button[title*='send' i]"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            # По тексту (адаптировано из Playwright has-text)
            (By.XPATH, "//button[contains(text(), 'Send')]"),
            (By.XPATH, "//button[contains(text(), 'Отправить')]"),
            # По SVG внутри (адаптировано из Playwright has(svg))
            (By.CSS_SELECTOR, "button svg[class*='send']"),
            (By.XPATH, "//button[.//svg]"),  # Selenium эквивалент button:has(svg)
            # Другие варианты из исходника
            (By.CSS_SELECTOR, ".chat-send"),
            (By.CSS_SELECTOR, "[data-testid*='send']")
        ]
        
        result = {
            "input_box": None,
            "send_button": None,
            "input_found": False,
            "send_found": False,
            "input_selector": None,
            "send_selector": None,
            "found_in": "unknown",  # "main_page", "iframe", "shadow_dom"
            "all_input_candidates": [],
            "all_send_candidates": []
        }
        
        logger.info("🔍 Searching for chat input field...")
        logger.info("📋 Step 1: Checking for blocking reCAPTCHA...")
        
        # ВАЖНО: Проверяем reCAPTCHA ПЕРЕД поиском элементов
        captcha_info = AutomationHelpers.check_for_captcha(driver)
        if captcha_info["captcha_detected"]:
            if captcha_info["blocking"] or captcha_info["visible"]:
                logger.warning(f"⚠️ reCAPTCHA detected and may block elements! types={captcha_info['captcha_types']}")
                # Проверяем modalRecaptcha и даем пользователю решить вручную
                AutomationHelpers.close_captcha_modals(driver, max_attempts=3, wait_for_manual=True)
                time.sleep(0.5)  # Даем время после решения CAPTCHA
            elif captcha_info["hidden"]:
                logger.info(f"ℹ️ Hidden reCAPTCHA detected (not blocking): types={captcha_info['captcha_types']}")
        else:
            logger.info("✓ No blocking reCAPTCHA detected")
        
        # ВАЖНО: Ждем немного для загрузки динамического контента
        logger.info("📋 Step 2: Waiting for dynamic content to load...")
        time.sleep(1)
        
        # ШАГ 1: Проверяем Shadow DOM (быстрая проверка)
        logger.info("📋 Step 3: Checking Shadow DOM for chat input...")
        shadow_selectors = [
            ("[class*='chat']", "[contenteditable='true']"),
            ("[class*='message']", "[contenteditable='true']"),
            ("[id*='chat']", "[contenteditable='true']"),
        ]
        
        for host_sel, inner_sel in shadow_selectors:
            try:
                elements = AutomationHelpers.find_elements_in_shadow_dom(driver, host_sel, inner_sel)
                if elements and len(elements) > 0:
                    logger.info(f"✓ Found element in Shadow DOM: {host_sel} > {inner_sel}")
                    # Возвращаем первый найденный элемент (нужно будет доработать для реального использования)
                    result["input_box"] = elements[0] if elements else None
                    result["input_found"] = True
                    result["input_selector"] = f"shadow:{host_sel}>{inner_sel}"
                    break
            except Exception as e:
                logger.debug(f"Shadow DOM check failed: {e}")
        
        # Если нашли в Shadow DOM, продолжаем поиск остальных элементов
        if result["input_found"]:
            logger.info("Found input in Shadow DOM, continuing search for send button...")
        
        # ШАГ 2: Проверяем iframe (если не нашли в Shadow DOM или на основной странице)
        if not result["input_found"]:
            logger.info("📋 Step 4: Checking iframes for chat input...")
            iframes = AutomationHelpers.find_iframes(driver)
            
            for iframe in iframes:
                try:
                    iframe_result = AutomationHelpers.find_chat_elements_in_iframe(driver, iframe)
                    if iframe_result.get("input_found"):
                        logger.info(f"✓ Found chat elements in iframe!")
                        result.update(iframe_result)
                        break
                except Exception as e:
                    logger.debug(f"Error checking iframe: {e}")
                    continue
        
        # ШАГ 3: Поиск на основной странице (только если не нашли в iframe/Shadow DOM)
        if not result["input_found"]:
            logger.info("📋 Step 5: Searching on main page with XPath: /html/body/div[1]/div/div/div[3]/div/div[1]/div[1]...")
        
        # Search for input field (only if not found in iframe/Shadow DOM)
        if not result["input_found"]:
            try:
                wait = WebDriverWait(driver, 5, poll_frequency=0.5)
                element = wait.until(EC.presence_of_element_located(input_selector))
                
                # Check if element exists and get info
                is_present = element is not None
                is_displayed = element.is_displayed() if is_present else False
                tag = element.tag_name if is_present else None
                classes = element.get_attribute("class") if is_present else None
                
                result["all_input_candidates"].append({
                    "selector": str(input_selector[1]),
                    "present": is_present,
                    "displayed": is_displayed,
                    "tag": tag,
                    "classes": classes
                })
                
                # Принимаем элемент если он существует (XPath может найти даже скрытый элемент)
                if is_present:
                    logger.info(f"✅ SUCCESS: Found input field!")
                    logger.info(f"   Location: {input_selector[1]}")
                    logger.info(f"   Tag: {tag}, Classes: {classes}")
                    logger.info(f"   Displayed: {is_displayed}")
                    result["input_box"] = element
                    result["input_found"] = True
                    result["input_selector"] = str(input_selector[1])
                    result["found_in"] = "main_page"
                    # Дополнительная проверка - убеждаемся что элемент действительно доступен
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        logger.info("   ✓ Scrolled element into view")
                        time.sleep(0.3)
                    except:
                        pass
                else:
                    logger.warning(f"⚪ Input element found but is None")
                    
            except (NoSuchElementException, TimeoutException) as e:
                result["all_input_candidates"].append({
                    "selector": str(input_selector[1]),
                    "present": False,
                    "error": str(e)[:50]
                })
                logger.error(f"✗ Input field not found: {input_selector[1]} - {str(e)[:50]}")
            except Exception as e:
                logger.error(f"✗ Unexpected error finding input: {e}")
        
        if not result["input_found"]:
            logger.error("❌ Input field not found!")
            logger.error(f"Selector: {input_selector[1]}")
        
        # Search for send button (only if not found in iframe/Shadow DOM)
        if not result["send_found"]:
            logger.info("🔍 Searching for send button...")
            
            # Проверяем Shadow DOM для send button
            for host_sel, inner_sel in [("button", "#sendButton"), ("*", "button[type='submit']")]:
                try:
                    elements = AutomationHelpers.find_elements_in_shadow_dom(driver, host_sel, inner_sel)
                    if elements and len(elements) > 0:
                        logger.info(f"✓ Found send button in Shadow DOM")
                        result["send_button"] = elements[0]
                        result["send_found"] = True
                        break
                except:
                    pass
        
        # Search for send button with detailed logging
        if not result["send_found"]:
            for idx, (by, selector) in enumerate(send_selectors):
                try:
                    wait = WebDriverWait(driver, settings.ELEMENT_PRESENT_TIMEOUT, poll_frequency=settings.POLLING_INTERVAL)
                    element = wait.until(EC.presence_of_element_located((by, selector)))
                    
                    # Check if element exists and get info
                    is_present = element is not None
                    is_displayed = element.is_displayed() if is_present else False
                    tag = element.tag_name if is_present else None
                    text = element.text[:30] if is_present and element.text else None
                    
                    result["all_send_candidates"].append({
                        "selector": selector,
                        "present": is_present,
                        "displayed": is_displayed,
                        "tag": tag,
                        "text": text
                    })
                    
                    if is_displayed:
                        logger.info(f"✓ Found send button (#{idx+1}): {selector} (tag: {tag}, text: {text})")
                        result["send_button"] = element
                        result["send_found"] = True
                        result["send_selector"] = selector
                        break
                    elif is_present:
                        logger.debug(f"⚪ Send button found but not visible (#{idx+1}): {selector}")
                        
                except (NoSuchElementException, TimeoutException) as e:
                    result["all_send_candidates"].append({
                        "selector": selector,
                        "present": False,
                        "error": str(e)[:50]
                    })
                    logger.debug(f"✗ Send selector #{idx+1} failed: {selector} - {str(e)[:50]}")
                    continue
                except Exception as e:
                    logger.debug(f"✗ Unexpected error with selector #{idx+1} {selector}: {e}")
                    continue
        
        if not result["send_found"]:
            logger.warning("⚠️ Send button not found with any selector!")
            logger.warning(f"Tried {len(send_selectors)} selectors. Candidates: {result['all_send_candidates'][:5]}")
        
        logger.info(f"📊 Search results: input={result['input_found']}, send={result['send_found']}")
        return result
    
    @staticmethod
    def check_for_captcha(driver: WebDriver) -> Dict[str, Any]:
        """
        Comprehensive check for active CAPTCHA (including hidden ones that might block elements).
        
        Args:
            driver: WebDriver instance
            
        Returns:
            Dict with CAPTCHA information
        """
        captcha_results = {
            "captcha_detected": False,
            "captcha_types": [],
            "visible": False,
            "hidden": False,
            "blocking": False
        }
        
        # Расширенный список селекторов для reCAPTCHA (включая скрытые)
        captcha_selectors = [
            (By.CSS_SELECTOR, "iframe[src*='recaptcha']"),
            (By.CSS_SELECTOR, "iframe[src*='google.com/recaptcha']"),
            (By.CSS_SELECTOR, ".g-recaptcha"),
            (By.CSS_SELECTOR, "#g-recaptcha"),
            (By.ID, "modalRecaptcha"),
            (By.CSS_SELECTOR, "[data-sitekey]"),  # reCAPTCHA обычно имеет data-sitekey
            (By.CSS_SELECTOR, ".recaptcha"),
            (By.CSS_SELECTOR, ".grecaptcha-badge")
        ]
        
        # Проверяем через JavaScript для более глубокого поиска
        try:
            js_check = driver.execute_script("""
                var captchaInfo = {
                    found: false,
                    visible: false,
                    hidden: false,
                    types: []
                };
                
                // Проверяем iframe с reCAPTCHA
                var iframes = document.querySelectorAll('iframe');
                for (var i = 0; i < iframes.length; i++) {
                    var src = iframes[i].src || '';
                    if (src.includes('recaptcha') || src.includes('google.com/recaptcha')) {
                        captchaInfo.found = true;
                        captchaInfo.types.push('iframe');
                        if (iframes[i].offsetWidth > 0 && iframes[i].offsetHeight > 0) {
                            captchaInfo.visible = true;
                        } else {
                            captchaInfo.hidden = true;
                        }
                    }
                }
                
                // Проверяем элементы с классом reCAPTCHA
                var recaptchaElements = document.querySelectorAll('.g-recaptcha, #g-recaptcha, .recaptcha, .grecaptcha-badge');
                if (recaptchaElements.length > 0) {
                    captchaInfo.found = true;
                    captchaInfo.types.push('element');
                    for (var i = 0; i < recaptchaElements.length; i++) {
                        var rect = recaptchaElements[i].getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            captchaInfo.visible = true;
                        } else {
                            captchaInfo.hidden = true;
                        }
                    }
                }
                
                // Проверяем modal
                var modal = document.getElementById('modalRecaptcha');
                if (modal) {
                    captchaInfo.found = true;
                    captchaInfo.types.push('modal');
                    var style = window.getComputedStyle(modal);
                    if (style.display !== 'none' && style.visibility !== 'hidden') {
                        captchaInfo.visible = true;
                    } else {
                        captchaInfo.hidden = true;
                    }
                }
                
                return captchaInfo;
            """)
            
            if js_check and js_check.get('found'):
                captcha_results["captcha_detected"] = True
                captcha_results["captcha_types"] = js_check.get('types', [])
                captcha_results["visible"] = js_check.get('visible', False)
                captcha_results["hidden"] = js_check.get('hidden', False)
                captcha_results["blocking"] = js_check.get('visible', False)  # Видимая CAPTCHA может блокировать
                
                logger.info(f"🔍 CAPTCHA detected: types={captcha_results['captcha_types']}, visible={captcha_results['visible']}, hidden={captcha_results['hidden']}")
        except Exception as e:
            logger.debug(f"JavaScript CAPTCHA check failed: {e}")
        
        # Дополнительная проверка через Selenium (fallback)
        if not captcha_results["captcha_detected"]:
            for by, selector in captcha_selectors:
                try:
                    elements = driver.find_elements(by, selector)
                    if elements:
                        first_element = elements[0]
                        is_displayed = first_element.is_displayed()
                        
                        captcha_results["captcha_detected"] = True
                        captcha_results["captcha_types"].append(selector)
                        
                        if is_displayed:
                            captcha_results["visible"] = True
                            captcha_results["blocking"] = True
                        else:
                            captcha_results["hidden"] = True
                        
                        logger.info(f"🔍 CAPTCHA found via Selenium: {selector}, visible={is_displayed}")
                        break
                        
                except Exception as e:
                    logger.debug(f"Error checking {selector}: {e}")
                    continue
        
        # Проверяем, блокирует ли CAPTCHA элементы (overlay/modal)
        if captcha_results["captcha_detected"]:
            try:
                blocking_elements = driver.execute_script("""
                    var blocking = false;
                    var modals = document.querySelectorAll('.modal.show, [class*="modal"][style*="display: block"], .swal2-container');
                    if (modals.length > 0) {
                        blocking = true;
                    }
                    return blocking;
                """)
                if blocking_elements:
                    captcha_results["blocking"] = True
                    logger.warning("⚠️ CAPTCHA modal detected - may block element interaction")
            except:
                pass
        
        return captcha_results
    
    @staticmethod
    def wait_for_manual_captcha_solution(driver: WebDriver, timeout: int = 120) -> bool:
        """
        Waits for user to manually solve CAPTCHA (especially modalRecaptcha).
        Continuously checks if modalRecaptcha or blocking CAPTCHA disappeared.
        
        Args:
            driver: WebDriver instance
            timeout: maximum waiting time in seconds (default 120)
            
        Returns:
            bool: True if CAPTCHA disappeared
        """
        start_time = time.time()
        check_interval = 2  # Check every 2 seconds for faster response
        last_log_time = start_time
        log_interval = 10  # Log progress every 10 seconds
        
        while time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            
            # Проверяем modalRecaptcha напрямую (самый быстрый способ)
            try:
                modal_recaptcha = driver.find_element(By.ID, "modalRecaptcha")
                style = driver.execute_script("""
                    var el = arguments[0];
                    var style = window.getComputedStyle(el);
                    return style.display !== 'none' && style.visibility !== 'hidden';
                """, modal_recaptcha)
                
                if not style:
                    # modalRecaptcha исчез
                    logger.info(f"✅ modalRecaptcha disappeared after {elapsed} seconds")
                    print(f"\n✅ CAPTCHA SOLVED! Continuing automation...\n")
                    return True
            except (NoSuchElementException, TimeoutException):
                # modalRecaptcha не найден - значит решен
                logger.info(f"✅ modalRecaptcha not found after {elapsed} seconds (solved)")
                print(f"\n✅ CAPTCHA SOLVED! Continuing automation...\n")
                return True
            except Exception as e:
                logger.debug(f"Error checking modalRecaptcha: {e}")
            
            # Дополнительная проверка через check_for_captcha
            try:
                captcha_info = AutomationHelpers.check_for_captcha(driver)
                if not captcha_info["blocking"] and not captcha_info["visible"]:
                    logger.info(f"✅ Blocking CAPTCHA disappeared after {elapsed} seconds")
                    print(f"\n✅ CAPTCHA SOLVED! Continuing automation...\n")
                    return True
            except Exception as e:
                logger.debug(f"CAPTCHA check error: {e}")
            
            # Показываем прогресс каждые 10 секунд
            if time.time() - last_log_time >= log_interval:
                logger.info(f"⏳ Waiting for manual CAPTCHA solution... ({elapsed}s / {timeout}s)")
                last_log_time = time.time()
            
            # Небольшая задержка перед следующей проверкой
            time.sleep(check_interval)
        
        # Final check
        try:
            modal_recaptcha = driver.find_element(By.ID, "modalRecaptcha")
            style = driver.execute_script("""
                var el = arguments[0];
                var style = window.getComputedStyle(el);
                return style.display !== 'none' && style.visibility !== 'hidden';
            """, modal_recaptcha)
            
            if not style:
                logger.info("✅ CAPTCHA solved at the last moment")
                print(f"\n✅ CAPTCHA SOLVED! Continuing automation...\n")
                return True
        except (NoSuchElementException, TimeoutException):
            logger.info("✅ CAPTCHA solved (modalRecaptcha not found)")
            print(f"\n✅ CAPTCHA SOLVED! Continuing automation...\n")
            return True
        except Exception:
            pass
        
        logger.warning(f"⏰ CAPTCHA not solved within {timeout} seconds - continuing anyway")
        print(f"\n⏰ Time expired ({timeout}s) - continuing automation\n")
        return False


# Alias for convenient import
RTH = AutomationHelpers

