"""Application settings and configuration."""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings."""
    
    # Base URL
    BASE_URL: str = os.getenv("BASE_URL", "https://ask.u.ae")
    
    # Browser settings
    BROWSER: str = os.getenv("BROWSER", "chrome").lower()
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
    IMPLICIT_WAIT: int = int(os.getenv("IMPLICIT_WAIT", "5"))
    PAGE_LOAD_TIMEOUT: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "15"))
    
    # Window settings
    WINDOW_WIDTH: int = int(os.getenv("WINDOW_WIDTH", "1920"))
    WINDOW_HEIGHT: int = int(os.getenv("WINDOW_HEIGHT", "1080"))
    
    # Test settings
    SCREENSHOT_ON_FAILURE: bool = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
    SCREENSHOT_DIR: Path = Path(__file__).parent.parent / "reports" / "screenshots"
    
    # Wait settings - централизованное управление таймаутами
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "3"))  # Основной таймаут для элементов
    ELEMENT_PRESENT_TIMEOUT: int = int(os.getenv("ELEMENT_PRESENT_TIMEOUT", "2"))  # Быстрая проверка наличия
    ELEMENT_VISIBLE_TIMEOUT: int = int(os.getenv("ELEMENT_VISIBLE_TIMEOUT", "2"))  # Проверка видимости
    CLICK_TIMEOUT: int = int(os.getenv("CLICK_TIMEOUT", "2"))  # Ожидание кликабельности
    DISCLAIMER_TIMEOUT: int = int(os.getenv("DISCLAIMER_TIMEOUT", "2"))  # Таймаут для disclaimer
    SEND_BUTTON_TIMEOUT: int = int(os.getenv("SEND_BUTTON_TIMEOUT", "1"))  # Быстрая проверка кнопки отправки
    BOT_RESPONSE_TIMEOUT_MULTIPLIER: int = int(os.getenv("BOT_RESPONSE_TIMEOUT_MULTIPLIER", "2"))  # Множитель для ответа бота
    PAGE_LOAD_TIMEOUT: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "10"))  # Загрузка страницы
    
    # Задержки (минимальные)
    SMALL_DELAY: float = float(os.getenv("SMALL_DELAY", "0.1"))  # Минимальная задержка
    MEDIUM_DELAY: float = float(os.getenv("MEDIUM_DELAY", "0.2"))  # Средняя задержка
    
    # Polling settings
    POLLING_INTERVAL: float = float(os.getenv("POLLING_INTERVAL", "0.2"))  # Интервал опроса


# Global settings instance
settings = Settings()

