# UI Tests for UASK Chatbot

Автоматизированные тесты интерфейса чатбота на базе Selenium и pytest.

## Архитектура проекта

Проект организован по модульному принципу:

```
uask-chatbot-tests/
├── adapters/          # Адаптеры для работы с браузерами
│   └── driver_factory.py  # Фабрика для создания WebDriver
├── config/            # Конфигурация
│   └── settings.py    # Настройки приложения
├── core/              # Основные классы Page Object Model
│   ├── base_page.py   # Базовый класс для страниц
│   └── chat_page.py   # Page Object для чатбота
├── tests/             # Тесты
│   ├── test_chatbot_functionality.py  # Функциональные тесты
│   ├── test_chatbot_ui_elements.py    # Тесты UI элементов
│   └── test_chatbot_responses.py      # Тесты ответов бота
├── utils/             # Утилиты
│   └── screenshot_utils.py  # Утилиты для скриншотов
├── conftest.py        # Pytest конфигурация и фикстуры
└── pytest.ini        # Настройки pytest
```

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Скопируйте `.env.example` в `.env` и настройте параметры:
```bash
cp .env.example .env
```

## Запуск тестов

### Все тесты:
```bash
pytest
```

### Конкретный тест-файл:
```bash
pytest tests/test_chatbot_functionality.py
```

### Конкретный тест:
```bash
pytest tests/test_chatbot_functionality.py::TestChatbotFunctionality::test_send_simple_message
```

### С параллельным выполнением:
```bash
pytest -n auto
```

### С отчетом HTML:
```bash
pytest --html=reports/test_report.html
```

### Headless режим:
Установите в `.env`: `HEADLESS=true`

## Структура тестов

- **test_chatbot_functionality.py** - Основная функциональность чатбота
  - Загрузка страницы
  - Отправка сообщений
  - Получение ответов
  - Множественные сообщения

- **test_chatbot_ui_elements.py** - Тесты UI элементов
  - Интерактивность полей ввода
  - Отображение истории сообщений
  - Функциональность кнопок

- **test_chatbot_responses.py** - Качество ответов бота
  - Время ответа
  - Содержимое ответов
  - Различные типы вопросов
  - Сохранение контекста

## Настройка

Все настройки находятся в `config/settings.py` и управляются через переменные окружения в `.env`:

- `BASE_URL` - URL приложения
- `BROWSER` - браузер (chrome/firefox/edge)
- `HEADLESS` - запуск в headless режиме
- `IMPLICIT_WAIT` - неявное ожидание
- `DEFAULT_TIMEOUT` - таймаут по умолчанию
- `SCREENSHOT_ON_FAILURE` - делать скриншоты при ошибках

## Особенности архитектуры

1. **Page Object Model** - все взаимодействия с элементами страницы инкапсулированы в Page Objects
2. **Factory Pattern** - создание WebDriver через фабрику
3. **Настройки через .env** - гибкая конфигурация без изменения кода
4. **Автоматические скриншоты** - при падении тестов автоматически сохраняются скриншоты
5. **Типизация** - полная типизация для лучшей поддержки и IDE-подсказок

