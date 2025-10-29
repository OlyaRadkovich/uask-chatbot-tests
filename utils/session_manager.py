"""
Session management utilities for saving/loading browser sessions
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
        """
        Save current browser session (cookies) to file
        
        Args:
            driver: Selenium WebDriver instance
            session_file: Path to save session file
            
        Returns:
            True if saved successfully
        """
        try:
            cookies = driver.get_cookies()
            
            # Also try to save localStorage via JavaScript
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
        """
        Load browser session (cookies) from file
        
        Args:
            driver: Selenium WebDriver instance
            session_file: Path to session file
            
        Returns:
            True if loaded successfully
        """
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
            
            # Navigate to target URL (required for setting cookies)
            driver.get(target_url)
            import time
            time.sleep(0.5)  # Brief wait for page to load
            
            # Set cookies - filter out expired cookies and normalize domain
            cookies_set = 0
            for cookie in cookies:
                try:
                    # Remove problematic fields
                    cookie_dict = {k: v for k, v in cookie.items() 
                                 if k not in ('expiry', 'expires') or (v is not None and v > 0)}
                    
                    # Ensure domain is set (cookies should be for ask.u.ae)
                    if 'domain' in cookie_dict:
                        # Normalize domain - remove leading dot if present
                        domain = cookie_dict['domain'].lstrip('.')
                        if not domain.startswith('ask.u.ae'):
                            continue  # Skip cookies for wrong domain
                    else:
                        # Add domain if missing
                        cookie_dict['domain'] = '.ask.u.ae'
                    
                    driver.add_cookie(cookie_dict)
                    cookies_set += 1
                except Exception as e:
                    logger.debug(f"Could not set cookie {cookie.get('name', 'unknown')}: {e}")
                    continue
            
            # Restore localStorage
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
            
            # Reload page to apply cookies
            driver.refresh()
            time.sleep(0.5)
            
            logger.info(f"✓ Session loaded from {session_file} ({cookies_set}/{len(cookies)} cookies set, {len(local_storage)} localStorage items)")
            return cookies_set > 0
            
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return False

