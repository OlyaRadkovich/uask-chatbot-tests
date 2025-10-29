"""
Session management utilities for saving/loading browser sessions (renamed)
Helps avoid repeated CAPTCHA challenges by reusing authenticated sessions
"""
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages browser session storage and retrieval"""

    @staticmethod
    def save_session(driver: WebDriver, session_file: Path) -> bool:
        try:
            cookies = driver.get_cookies()
            try:
                local_storage = driver.execute_script(
                    "return Object.keys(localStorage).reduce((acc, key) => {"
                    "  acc[key] = localStorage.getItem(key);"
                    "  return acc;"
                    "}, {});"
                )
            except Exception as e:
                logger.debug(f"Could not save localStorage: {e}")
                local_storage = {}
            session_data = {
                "cookies": cookies,
                "local_storage": local_storage,
                "url": driver.current_url
            }
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            logger.info(f"✓ Session saved to {session_file} ({len(cookies)} cookies, {len(local_storage)} localStorage items)")
            return True
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False

    @staticmethod
    def load_session(driver: WebDriver, session_file: Path, target_url: str = "https://ask.u.ae/") -> bool:
        if not session_file.exists():
            logger.debug(f"Session file not found: {session_file}")
            return False
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            cookies = session_data.get("cookies", [])
            local_storage = session_data.get("local_storage", {})
            if not cookies:
                logger.warning("Session file exists but contains no cookies")
                return False
            driver.get(target_url)
            import time
            time.sleep(0.5)
            cookies_set = 0
            for cookie in cookies:
                try:
                    cookie_dict = {k: v for k, v in cookie.items()
                                   if k not in ('expiry', 'expires') or (v is not None and v > 0)}
                    if 'domain' in cookie_dict:
                        domain = cookie_dict['domain'].lstrip('.')
                        if not domain.startswith('ask.u.ae'):
                            continue
                    else:
                        cookie_dict['domain'] = '.ask.u.ae'
                    driver.add_cookie(cookie_dict)
                    cookies_set += 1
                except Exception as e:
                    logger.debug(f"Could not set cookie {cookie.get('name', 'unknown')}: {e}")
                    continue
            if local_storage:
                try:
                    driver.execute_script(
                        "const storage = arguments[0];"
                        "Object.keys(storage).forEach(key => {"
                        "  localStorage.setItem(key, storage[key]);"
                        "});",
                        local_storage
                    )
                except Exception as e:
                    logger.debug(f"Could not restore localStorage: {e}")
            driver.refresh()
            time.sleep(0.5)
            logger.info(f"✓ Session loaded from {session_file} ({cookies_set}/{len(cookies)} cookies set, {len(local_storage)} localStorage items)")
            return cookies_set > 0
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return False
