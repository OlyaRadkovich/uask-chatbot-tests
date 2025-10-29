"""WebDriver factory for creating browser instances."""
from typing import Union
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from config.settings import settings


class DriverFactory:
    """Factory for creating WebDriver instances."""
    
    @staticmethod
    def create_driver() -> Union[webdriver.Remote, webdriver.Chrome, webdriver.Firefox, webdriver.Edge]:
        """
        Create and configure WebDriver instance.
        
        Returns:
            Configured WebDriver instance
        """
        browser = settings.BROWSER.lower()
        
        if browser == "chrome":
            return DriverFactory._create_chrome_driver()
        elif browser == "firefox":
            return DriverFactory._create_firefox_driver()
        elif browser == "edge":
            return DriverFactory._create_edge_driver()
        else:
            raise ValueError(f"Unsupported browser: {browser}")
    
    @staticmethod
    def _create_chrome_driver() -> webdriver.Chrome:
        """Create Chrome WebDriver instance."""
        options = ChromeOptions()
        
        if settings.HEADLESS:
            options.add_argument("--headless=new")
        
        # Базовые опции для стабильности
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--window-size={settings.WINDOW_WIDTH},{settings.WINDOW_HEIGHT}")
        
        # Опции для headless режима
        if settings.HEADLESS:
            options.add_argument("--disable-gpu")
        
        # Опции для скрытия автоматизации (но они не должны мешать навигации)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Добавляем опции для правильной загрузки страниц
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        
        import os
        driver_manager = ChromeDriverManager()
        initial_path = driver_manager.install()
        
        # Исправляем проблему, когда webdriver-manager возвращает путь к THIRD_PARTY_NOTICES
        # вместо исполняемого файла chromedriver
        driver_path = initial_path
        
        if 'THIRD_PARTY' in initial_path or not os.path.basename(initial_path).startswith('chromedriver'):
            driver_dir = os.path.dirname(initial_path)
            # Ищем chromedriver в директории и подпапках
            found = False
            for root, dirs, files in os.walk(driver_dir):
                for filename in files:
                    # Ищем файл chromedriver (без расширений .txt, .md и т.д.)
                    if filename == 'chromedriver' or (filename.startswith('chromedriver') and '.' not in filename):
                        full_path = os.path.join(root, filename)
                        # Проверяем, что это файл, а не директория
                        if os.path.isfile(full_path):
                            driver_path = full_path
                            found = True
                            break
                if found:
                    break
        
        # Убеждаемся, что файл исполняемый (для macOS/Linux)
        if os.path.exists(driver_path) and os.path.isfile(driver_path):
            try:
                os.chmod(driver_path, 0o755)
            except (OSError, PermissionError):
                pass  # Игнорируем ошибки прав доступа
        
        service = ChromeService(driver_path)
        
        # Убираем некоторые опции, которые могут вызывать проблемы с навигацией
        # Но оставляем базовые для безопасности
        
        driver = webdriver.Chrome(service=service, options=options)
        
        # Настройка таймаутов ПЕРЕД любой навигацией
        driver.implicitly_wait(settings.IMPLICIT_WAIT)
        driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
        
        # Убираем начальную data: страницу, если она есть
        try:
            current_url = driver.current_url
            if current_url.startswith("data:"):
                driver.get("about:blank")
        except Exception:
            pass
        
        # Remove webdriver property (выполняем после инициализации)
        try:
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
        except Exception:
            pass  # Если CDP не работает, продолжаем без этого
        
        driver.maximize_window()
        
        return driver
    
    @staticmethod
    def _create_firefox_driver() -> webdriver.Firefox:
        """Create Firefox WebDriver instance."""
        options = FirefoxOptions()
        
        if settings.HEADLESS:
            options.add_argument("--headless")
        
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        
        driver.implicitly_wait(settings.IMPLICIT_WAIT)
        driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
        driver.maximize_window()
        
        return driver
    
    @staticmethod
    def _create_edge_driver() -> webdriver.Edge:
        """Create Edge WebDriver instance."""
        options = EdgeOptions()
        
        if settings.HEADLESS:
            options.add_argument("--headless=new")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--window-size={settings.WINDOW_WIDTH},{settings.WINDOW_HEIGHT}")
        
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        
        driver.implicitly_wait(settings.IMPLICIT_WAIT)
        driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
        driver.maximize_window()
        
        return driver

