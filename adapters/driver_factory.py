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
        """Create Chrome WebDriver instance with maximum stealth settings."""
        options = ChromeOptions()
        
        # ВАЖНО: Не используем headless для сайтов с защитой от ботов
        # Headless режим легко детектируется
        # if settings.HEADLESS:
        #     options.add_argument("--headless=new")
        
        # Базовые опции для стабильности
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--window-size={settings.WINDOW_WIDTH},{settings.WINDOW_HEIGHT}")
        
        # МАКСИМАЛЬНЫЕ СТЕЛС НАСТРОЙКИ для полного обхода детекции автоматизации
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging", "enable-blink-features=AutomationControlled"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Убираем все признаки автоматизации
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-session-crashed-bubble")
        options.add_argument("--disable-component-extensions-with-background-pages")
        
        # Эмуляция настоящего браузера
        options.add_argument("--start-maximized")
        options.add_argument("--lang=en-US,en")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        
        # Предотвращение детекции автоматизации
        options.add_argument("--disable-gpu")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-extensions-file-access-check")
        options.add_argument("--disable-extensions-http-throttling")
        options.add_argument("--disable-plugins-discovery")
        
        # Дополнительные настройки для обхода детекции
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-sync")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--disable-default-apps")
        options.add_argument("--mute-audio")
        
        # User-Agent для имитации настоящего браузера (обновленный)
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        options.add_argument(f"--user-agent={user_agent}")
        
        # Отключаем все логирование
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        
        # Дополнительные настройки для обхода детекции
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 1,
            # Подавляем логирование ошибок ресурсов (404 и т.д.)
            "logging": {
                "level": "WARNING"  # Только предупреждения и ошибки, не INFO/DEBUG
            }
        }
        options.add_experimental_option("prefs", prefs)
        
        # Отключаем логирование сетевых ошибок
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        
        # Отключаем вывод ошибок в консоль (только для автоматизации)
        options.add_argument("--log-level=3")  # Только FATAL ошибки в консоль
        options.add_argument("--disable-logging")
        
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
        
        # Подавляем логирование ошибок ресурсов (404, failed to load и т.д.)
        # Эти ошибки не критичны и засоряют логи
        try:
            driver.execute_cdp_cmd('Runtime.enable', {})
            driver.execute_cdp_cmd('Log.enable', {})
            
            # Игнорируем ошибки загрузки ресурсов и информационные сообщения
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    // Переопределяем console.error чтобы фильтровать 404 ошибки и ошибки webdriver
                    const originalConsoleError = console.error;
                    console.error = function(...args) {
                        const message = args.join(' ');
                        // Игнорируем ошибки 404, failed to load resource, изображения
                        // И ОШИБКИ переопределения webdriver (это нормально и ожидаемо)
                        if (message.includes('404') || 
                            message.includes('Failed to load resource') ||
                            message.includes('net::ERR_') ||
                            message.includes('favicon') ||
                            message.includes('.gif') ||
                            message.includes('.png') ||
                            message.includes('.jpg') ||
                            message.includes('.jpeg') ||
                            message.includes('LoadingTDR') ||
                            message.includes('branding') ||
                            message.includes('Cannot redefine property: webdriver') ||
                            message.includes('Cannot redefine property')) {
                            return; // Пропускаем эти ошибки
                        }
                        originalConsoleError.apply(console, args);
                    };
                    
                    // Переопределяем console.info чтобы фильтровать информационные сообщения reCAPTCHA
                    const originalConsoleInfo = console.info;
                    console.info = function(...args) {
                        const message = args.join(' ');
                        // Игнорируем информационные сообщения reCAPTCHA (не критичные)
                        if (message.includes('ReCaptcha received') ||
                            message.includes('recaptcha') ||
                            message.includes('Normalizing')) {
                            return; // Пропускаем эти информационные сообщения
                        }
                        originalConsoleInfo.apply(console, args);
                    };
                    
                    // Переопределяем console.log для фильтрации
                    const originalConsoleLog = console.log;
                    console.log = function(...args) {
                        const message = args.join(' ');
                        // Игнорируем информационные сообщения
                        if (message.includes('ReCaptcha received') ||
                            message.includes('recaptcha') ||
                            message.includes('Normalizing')) {
                            return;
                        }
                        originalConsoleLog.apply(console, args);
                    };
                    
                    // Игнорируем ошибки Network через Performance API
                    const originalFetch = window.fetch;
                    window.fetch = function(...args) {
                        return originalFetch.apply(this, args).catch(function(error) {
                            // Игнорируем 404 ошибки для ресурсов (изображения, CSS и т.д.)
                            if (error.message && (
                                error.message.includes('404') ||
                                error.message.includes('Failed to fetch') ||
                                args[0] && typeof args[0] === 'string' && (
                                    args[0].includes('.gif') ||
                                    args[0].includes('.png') ||
                                    args[0].includes('.jpg') ||
                                    args[0].includes('favicon')
                                )
                            )) {
                                // Возвращаем пустой ответ вместо ошибки
                                return Promise.resolve(new Response('', { status: 404, statusText: 'Not Found' }));
                            }
                            throw error;
                        });
                    };
                    
                    // Игнорируем ошибки загрузки изображений
                    window.addEventListener('error', function(e) {
                        if (e.target && (
                            (e.target.tagName === 'IMG' && e.target.src) ||
                            (e.message && (
                                e.message.includes('404') ||
                                e.message.includes('Failed to load') ||
                                e.message.includes('favicon') ||
                                e.message.includes('.gif') ||
                                e.message.includes('LoadingTDR')
                            ))
                        )) {
                            e.preventDefault();
                            e.stopPropagation();
                            return false;
                        }
                    }, true);
                '''
            })
        except Exception as e:
            import logging
            logging.debug(f"Failed to suppress console errors: {e}")
        
        # Убираем начальную data: страницу, если она есть
        try:
            current_url = driver.current_url
            if current_url.startswith("data:"):
                driver.get("about:blank")
        except Exception:
            pass
        
        # МАКСИМАЛЬНЫЙ СТЕЛС: Удаляем ВСЕ признаки автоматизации через CDP
        try:
            # Комплексный скрипт для полного обхода детекции
            stealth_script = '''
                // 1. Безопасно удаляем navigator.webdriver (самый важный маркер)
                // Проверяем, можно ли переопределить свойство
                try {
                    // Пытаемся удалить свойство, если оно уже определено
                    if (navigator.hasOwnProperty('webdriver')) {
                        delete navigator.webdriver;
                    }
                    // Удаляем из прототипа
                    delete navigator.__proto__.webdriver;
                } catch(e) {
                    // Игнорируем ошибки удаления
                }
                
                // Теперь безопасно переопределяем
                try {
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                        configurable: true,  // ВАЖНО: разрешаем повторное переопределение
                        enumerable: false
                    });
                } catch(e) {
                    // Если не удалось переопределить, пробуем через Object.defineProperty с configurable
                    try {
                        const descriptor = Object.getOwnPropertyDescriptor(navigator, 'webdriver');
                        if (descriptor) {
                            // Удаляем и создаем заново
                            Object.defineProperty(navigator, 'webdriver', {
                                get: () => undefined,
                                configurable: true,
                                enumerable: false
                            });
                        }
                    } catch(e2) {
                        // Если все равно не получается, используем другой подход
                        Object.defineProperty(navigator, '__webdriver', {
                            value: undefined,
                            configurable: true
                        });
                    }
                }
                
                // 2. Переопределяем chrome объекта
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                // 3. Эмуляция настоящих plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => {
                        return [
                            {
                                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                                description: "Portable Document Format",
                                filename: "internal-pdf-viewer",
                                length: 1,
                                name: "Chrome PDF Plugin"
                            },
                            {
                                0: {type: "application/pdf", suffixes: "pdf", description: ""},
                                description: "",
                                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                                length: 1,
                                name: "Chrome PDF Viewer"
                            }
                        ];
                    }
                });
                
                // 4. Переопределяем languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en', 'ru']
                });
                
                // 5. Эмуляция настоящего разрешения экрана
                Object.defineProperty(screen, 'width', {get: () => 1920});
                Object.defineProperty(screen, 'height', {get: () => 1080});
                Object.defineProperty(screen, 'availWidth', {get: () => 1920});
                Object.defineProperty(screen, 'availHeight', {get: () => 1040});
                
                // 6. Переопределяем permissions API
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // 7. Удаляем признаки автоматизации из WebGL
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter.call(this, parameter);
                };
                
                // 8. Эмуляция настоящего connection
                Object.defineProperty(navigator, 'connection', {
                    get: () => ({
                        effectiveType: '4g',
                        rtt: 50,
                        downlink: 10,
                        saveData: false
                    })
                });
                
                // 9. Переопределяем canvas fingerprint
                const toBlob = HTMLCanvasElement.prototype.toBlob;
                const toDataURL = HTMLCanvasElement.prototype.toDataURL;
                const getImageData = CanvasRenderingContext2D.prototype.getImageData;
                
                // 10. Убираем свойство __driver_evaluate
                delete window.__driver_evaluate;
                delete window.__webdriver_evaluate;
                delete window.__selenium_evaluate;
                delete window.__fxdriver_evaluate;
                delete window._selenium;
                delete window._Selenium_IDE_Recorder;
                delete window._selenium;
                delete window.__driver_unwrapped;
                delete window.__webdriver_unwrapped;
                delete window.__selenium_unwrapped;
                delete window.__fxdriver_unwrapped;
                delete window._Selenium_IDE_Recorder;
                delete window._selenium;
                delete window.calledSelenium;
                delete window.$cdc_asdjflasutopfhvcZLmcfl_;
                delete window.$chrome_asyncScriptInfo;
                
                // 11. Эмуляция реального поведения мыши и клавиатуры
                Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
                Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
            '''
            
            # Применяем stealth скрипт ПЕРЕД загрузкой любой страницы
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': stealth_script
            })
            
            # Дополнительный скрипт для защиты от обнаружения после загрузки
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    // Защита от проверок после загрузки (безопасное переопределение)
                    if (window.document) {
                        try {
                            // Пытаемся безопасно переопределить только если свойство configurable
                            const descriptor = Object.getOwnPropertyDescriptor(navigator, 'webdriver');
                            if (!descriptor || descriptor.configurable) {
                                Object.defineProperty(navigator, 'webdriver', {
                                    get: () => false,
                                    configurable: true,
                                    enumerable: false
                                });
                            } else {
                                // Если свойство не configurable, просто игнорируем
                                // Не пытаемся переопределять, чтобы не вызывать ошибки
                            }
                        } catch(e) {
                            // Игнорируем ошибки переопределения
                            // reCAPTCHA может уже заблокировать это свойство
                        }
                    }
                '''
            })
            
            # 2. Эмуляция настоящего разрешения и viewport
            driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
                'width': settings.WINDOW_WIDTH,
                'height': settings.WINDOW_HEIGHT,
                'deviceScaleFactor': 1,
                'mobile': False
            })
            
            # 3. Эмуляция User-Agent и языков
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                'userAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'platform': 'MacIntel',
                'acceptLanguage': 'en-US,en;q=0.9'
            })
            
            # 4. Отключаем автоматизационные флаги через Runtime
            driver.execute_cdp_cmd('Runtime.addBinding', {
                'name': 'cdp_stealth'
            })
            
        except Exception as e:
            import logging
            logging.warning(f"CDP stealth commands failed: {e}")
            # Продолжаем даже если CDP не работает
        
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

