"""
Centralized CAPTCHA detection, waiting and session save hooks
"""
from typing import Dict, Any
import time
from pathlib import Path


def pause_after_captcha(seconds: int = 2):
    try:
        time.sleep(seconds)
    except Exception:
        pass


def handle_captcha_if_needed(chatbot_page, session_file: Path, wait_timeout: int = 30) -> Dict[str, Any]:
    info = chatbot_page.check_for_captcha()
    if info.get("captcha_detected"):
        solved = chatbot_page.wait_for_manual_captcha_solution(timeout=wait_timeout)
        if solved:
            try:
                chatbot_page.save_session_after_captcha(session_file)
            except Exception:
                pass
            pause_after_captcha(2)
        return {"detected": True, "solved": solved}
    return {"detected": False, "solved": False}


