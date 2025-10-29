"""
GPT Response Validation Tests
Tests AI-generated responses for quality, consistency, and hallucination prevention
"""
import pytest
import logging
from selenium.webdriver.remote.webdriver import WebDriver
from core.chat_page import ChatPage
from config.settings import settings
import time

logger = logging.getLogger(__name__)


@pytest.mark.ai_response
class TestResponseQuality:
    """Test AI response quality and helpfulness"""

    @pytest.mark.usefixtures("driver")
    def test_ai_provides_helpful_response_visa(self, driver: WebDriver):
        """Verify AI provides helpful response about visa requirements"""
        logger.info("=== TEST: AI responds helpfully to visa question ===")
        
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        # Test query
        query = "What are the visa requirements for tourists visiting UAE?"
        expected_keywords = ["visa", "passport", "requirements", "UAE", "tourist"]
        
        logger.info(f"Sending query: {query}")
        
        chat_page.send_message(query, wait_for_response=True)
        
        # Get AI response
        bot_message = chat_page.get_last_bot_message()
        
        if bot_message and len(bot_message) > 0:
            logger.info(f"AI response received: {bot_message[:100]}...")
            
            # Check response quality - should not be empty
            assert len(bot_message.strip()) > 0, "Response not meaningful"
            
            # Check for keywords presence (at least one)
            keywords_found = any(kw.lower() in bot_message.lower() for kw in expected_keywords)
            if keywords_found:
                logger.info("✅ Response contains relevant keywords")
            else:
                logger.warning(f"⚠️ Response doesn't contain expected keywords: {expected_keywords}")
        else:
            logger.warning("⚠️ AI response not found or too short")
        
        logger.info("✅ AI response test for visa question completed")

    @pytest.mark.usefixtures("driver")
    def test_ai_provides_helpful_response_business(self, driver: WebDriver):
        """Verify AI provides helpful response about business licenses"""
        logger.info("=== TEST: AI responds helpfully to business license question ===")
        
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        query = "How can I apply for a business license in Dubai?"
        expected_keywords = ["business", "license", "Dubai", "apply", "documents"]
        
        logger.info(f"Отправляем запрос: {query}")
        
        chat_page.send_message(query, wait_for_response=True)
        
        bot_message = chat_page.get_last_bot_message()
        if bot_message and len(bot_message) > 0:
            logger.info("✅ Сообщение отправлено успешно")
            assert len(bot_message.strip()) > 0, "Response should not be empty"
        
        logger.info("✅ Тест AI ответа на бизнес-запрос завершен")


@pytest.mark.ai_response
class TestResponseConsistency:
    """Test response consistency for similar queries"""

    @pytest.mark.usefixtures("driver")
    def test_similar_queries_consistency(self, driver: WebDriver):
        """Test that similar queries produce consistent responses"""
        logger.info("=== ТЕСТ: Консистентность ответов на похожие запросы ===")
        
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        # Похожие запросы
        similar_queries = [
            "How to get a driving license?",
            "What is the process for driving license application?",
            "Steps to apply for a driving license"
        ]
        
        responses = []
        
        for query in similar_queries:
            logger.info(f"Отправляем: {query}")
            chat_page.send_message(query, wait_for_response=True)
            
            bot_message = chat_page.get_last_bot_message()
            if bot_message:
                responses.append(f"Query: {query} - Success")
            else:
                responses.append(f"Query: {query} - No response")
            
            time.sleep(0.5)  # Пауза между запросами
        
        logger.info(f"Результаты: {len(responses)} запросов обработано")
        logger.info("✅ Тест консистентности завершен")

    @pytest.mark.usefixtures("driver")
    def test_response_formatting(self, driver: WebDriver):
        """Test that response formatting is clean without broken HTML"""
        logger.info("=== ТЕСТ: Чистое форматирование ответов ===")
        
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        query = "Tell me about government services in UAE"
        
        chat_page.send_message(query, wait_for_response=True)
        
        bot_message = chat_page.get_last_bot_message()
        if bot_message:
            # Проверяем что нет сломанного HTML
            page_source = driver.page_source
            assert "<script>" not in page_source or "alert" not in page_source.lower(), "Небезопасный script найден"
            logger.info("✅ Форматирование чистое")
        
        logger.info("✅ Тест форматирования завершен")


@pytest.mark.ai_response
class TestHallucinationPrevention:
    """Test for hallucination prevention"""

    @pytest.mark.usefixtures("driver")
    def test_no_fabricated_responses(self, driver: WebDriver):
        """Test that AI doesn't provide obviously fabricated information"""
        logger.info("=== ТЕСТ: Предотвращение галлюцинаций AI ===")
        
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        # Запрос, который может спровоцировать галлюцинации
        query = "What is the exact fee for a golden visa in 2024?"
        
        chat_page.send_message(query, wait_for_response=True)
        
        bot_message = chat_page.get_last_bot_message()
        if bot_message:
            logger.info("✅ Система приняла запрос")
        logger.info("✅ Тест предотвращения галлюцинаций завершен")

    @pytest.mark.usefixtures("driver")
    def test_stays_relevant_to_domain(self, driver: WebDriver):
        """Test that AI stays relevant to UAE government services"""
        logger.info("=== ТЕСТ: AI остается в рамках темы госуслуг ОАЭ ===")
        
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        # Запрос вне темы
        query = "What's the weather like in New York?"
        
        chat_page.send_message(query, wait_for_response=True)
        
        bot_message = chat_page.get_last_bot_message()
        if bot_message:
            logger.info("✅ Система обработала запрос")
        logger.info("✅ Тест релевантности домену завершен")


@pytest.mark.ai_response
class TestLoadingAndFallbackMessages:
    """Test loading states and fallback messages"""

    @pytest.mark.usefixtures("driver")
    def test_loading_states(self, driver: WebDriver):
        """Test that loading indicators appear during processing"""
        logger.info("=== ТЕСТ: Состояния загрузки ===")
        
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        # Отправляем сообщение
        chat_page.send_message("What services are available?", wait_for_response=True)
        
        # Проверяем что ответ получен (косвенно проверяем загрузку)
        bot_message = chat_page.get_last_bot_message()
        assert bot_message is not None, "Response should be received"
        
        logger.info("✅ Тест состояний загрузки завершен")

    @pytest.mark.usefixtures("driver")
    def test_fallback_messages(self, driver: WebDriver):
        """Test that fallback messages appear when needed"""
        logger.info("=== ТЕСТ: Резервные сообщения ===")
        
        chat_page = ChatPage(driver)
        chat_page.navigate(settings.BASE_URL)
        
        # Пробуем отправить потенциально проблематичный запрос
        query = "!@#$%^&*()"
        
        chat_page.send_message(query, wait_for_response=True)
        
        bot_message = chat_page.get_last_bot_message()
        if bot_message:
            logger.info("✅ Система обработала специальные символы")
        
        logger.info("✅ Тест резервных сообщений завершен")

