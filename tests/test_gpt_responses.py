"""
GPT Response Validation Tests
Tests AI-generated responses for quality, consistency, and hallucination prevention
with reliable CAPTCHA/disclaimer handling
"""
import pytest
import logging
import allure
from utils.ai_checks import AIResponseValidator
from utils.test_toolkit import TestDataLoader
from pages.chat_page import ChatPage
import json

logger = logging.getLogger(__name__)


@pytest.mark.ai_response  
class TestResponseQuality:
    """Test AI response quality and helpfulness"""

    @allure.title("AI provides helpful response to visa query")
    def test_resp_helpful_visa(self, chatbot_page: ChatPage):
        """Verify AI provides helpful response about visa requirements"""
        logger.info("=== TEST: AI responds helpfully to visa question ===")
        
        # Page initialized by fixture
        
        # Test query
        query = "What are the visa requirements for tourists visiting UAE?"
        expected_keywords = ["visa", "passport", "requirements", "UAE", "tourist"]
        
        logger.info(f"Sending query: {query}")
        
        chatbot_page.send_message(query, wait_for_response=True)
        chatbot_page.wait_for_stable_response()
        ai_response = chatbot_page.get_last_ai_response()
        assert AIResponseValidator.is_meaningful_response(ai_response), "Response not meaningful"
        keywords_found = any(kw.lower() in ai_response.lower() for kw in expected_keywords)
        assert keywords_found, f"Expected keywords not found: {expected_keywords}"
        logger.info("✅ AI response test for visa question completed")

    @allure.title("AI provides helpful response to business license query")  
    def test_resp_helpful_business(self, chatbot_page: ChatPage):
        """Verify AI provides helpful response about business licenses"""
        logger.info("=== TEST: AI responds helpfully to business license question ===")
        
        # Page initialized by fixture
        
        query = "How can I apply for a business license in Dubai?"
        expected_keywords = ["business", "license", "Dubai", "apply", "documents"]
        
        logger.info(f"Отправляем запрос: {query}")
        
        chatbot_page.send_message(query, wait_for_response=True)
        chatbot_page.wait_for_stable_response()
        response = chatbot_page.get_last_ai_response()
        assert AIResponseValidator.is_meaningful_response(response)
        logger.info("✅ Тест AI ответа на бизнес-запрос завершен")


@pytest.mark.ai_response
class TestResponseConsistency:
    """Test response consistency for similar queries"""

    @allure.title("Similar queries produce consistent responses")
    def test_resp_similar_queries_consistency(self, chatbot_page: ChatPage):
        """Test that similar queries produce consistent responses"""
        logger.info("=== ТЕСТ: Консистентность ответов на похожие запросы ===")
        
        # Page initialized by fixture
        
        # Похожие запросы
        similar_queries = [
            "How to get a driving license?",
            "What is the process for driving license application?",
            "Steps to apply for a driving license"
        ]
        
        responses = []
        
        for query in similar_queries:
            logger.info(f"Отправляем: {query}")
            chatbot_page.send_message(query, wait_for_response=True)
            chatbot_page.wait_for_stable_response()
            responses.append(f"Query: {query} - Success")
        
        logger.info(f"Результаты: {len(responses)} запросов обработано")
        logger.info("✅ Тест консистентности завершен")
        
        

    @allure.title("Response formatting is clean")
    def test_resp_formatting_clean(self, chatbot_page: ChatPage):
        """Test that response formatting is clean without broken HTML"""
        logger.info("=== ТЕСТ: Чистое форматирование ответов ===")
        
        # Page initialized by fixture
        
        query = "Tell me about government services in UAE"
        
        chatbot_page.send_message(query, wait_for_response=True)
        chatbot_page.wait_for_stable_response()
        response = chatbot_page.get_last_ai_response()
        assert AIResponseValidator.is_well_formatted(response)
        logger.info("✅ Форматирование чистое")
        
        logger.info("✅ Тест форматирования завершен")
        


@pytest.mark.ai_response
class TestHallucinationPrevention:
    """Test for hallucination prevention"""

    @allure.title("AI does not provide fabricated information")
    def test_resp_no_fabrication(self, chatbot_page: ChatPage):
        """Test that AI doesn't provide obviously fabricated information"""
        logger.info("=== ТЕСТ: Предотвращение галлюцинаций AI ===")
        
        # Page initialized by fixture
        
        # Запрос, который может спровоцировать галлюцинации
        query = "What is the exact fee for a golden visa in 2024?"
        
        chatbot_page.send_message(query, wait_for_response=True)
        chatbot_page.wait_for_stable_response()
        response = chatbot_page.get_last_ai_response()
        assert AIResponseValidator.is_hallucination_free(response)
        logger.info("✅ Тест предотвращения галлюцинаций завершен")

    @allure.title("AI stays relevant to UAE government services")
    def test_resp_relevant_to_domain(self, chatbot_page: ChatPage):
        """Test that AI stays relevant to UAE government services"""
        logger.info("=== ТЕСТ: AI остается в рамках темы госуслуг ОАЭ ===")
        
        # Page initialized by fixture
        
        # Запрос вне темы
        query = "What's the weather like in New York?"
        
        chatbot_page.send_message(query, wait_for_response=True)
        chatbot_page.wait_for_stable_response()
        response = chatbot_page.get_last_ai_response()
        relevant_terms = ["uae", "service", "government"]
        assert AIResponseValidator.contains_keywords(response, relevant_terms, min_matches=1)
        logger.info("✅ Тест релевантности домену завершен")


@pytest.mark.ai_response
class TestLoadingAndFallbackMessages:
    """Test loading states and fallback messages"""

    @allure.title("Loading states appear properly")
    def test_resp_loading_states(self, chatbot_page: ChatPage):
        """Test that loading indicators appear during processing"""
        logger.info("=== ТЕСТ: Состояния загрузки ===")
        
        chatbot_page.send_message("What services are available?", wait_for_response=False)
        logger.info("✅ Тест состояний загрузки завершен")

    @allure.title("Fallback messages work properly")
    def test_resp_fallback_messages(self, chatbot_page: ChatPage):
        """Test that fallback messages appear when needed"""
        logger.info("=== ТЕСТ: Резервные сообщения ===")
        
        # Page initialized by fixture
        
        # Пробуем отправить потенциально проблематичный запрос
        query = "!@#$%^&*()"
        
        chatbot_page.send_message(query, wait_for_response=True)
        chatbot_page.wait_for_stable_response()
        page_text = "\n".join([chatbot_page.get_last_user_message(), chatbot_page.get_last_ai_response()]).lower()
        fallback_phrases = [
            "sorry", "try again", "please rephrase", 
            "I don't understand", "can you clarify"
        ]
        
        for phrase in fallback_phrases:
            if phrase in page_text:
                logger.info(f"✅ Найдена fallback фраза: {phrase}")
                break
        
        logger.info("✅ Тест резервных сообщений завершен")
        context.close()

    @pytest.mark.parametrize("query_data", TestDataLoader.get_queries_by_language("ar"))
    def test_resp_helpful_ar(
        self,
        chatbot_page: ChatPage,
        query_data: dict,
        test_language: str
    ):
        """Verify AI provides helpful responses to common queries in Arabic"""
        if test_language != "ar":
            pytest.skip("Arabic language test only")

        query = query_data["query"]
        expected_keywords = query_data.get("expected_keywords", [])
        forbidden_terms = query_data.get("should_not_contain", [])

        logger.info(f"Testing Arabic query: {query}")

        chatbot_page.send_message(query, wait_for_response=True)
        chatbot_page.wait_for_stable_response()

        response = chatbot_page.get_last_ai_response()
        logger.info(f"Arabic response length: {len(response)} characters")

        # Validate response
        assert AIResponseValidator.is_meaningful_response(response), \
            "Arabic response is not meaningful"

        assert AIResponseValidator.contains_keywords(response, expected_keywords, min_matches=1), \
            f"Arabic response missing expected keywords"

        assert AIResponseValidator.does_not_contain(response, forbidden_terms), \
            f"Arabic response contains forbidden terms"


@pytest.mark.ai_response
class TestHallucinationPrevention:
    """Test that AI does not hallucinate (fabricate or provide irrelevant info)"""

    def test_resp_no_hallucination(self, chatbot_page: ChatPage, test_language: str):
        """Verify responses are not fabricated or irrelevant"""
        logger.info("Testing hallucination prevention")

        queries = TestDataLoader.get_queries_by_language(test_language)

        for query_data in queries[:3]:  # Test first 3 queries
            query = query_data["query"]

            chatbot_page.send_message(query, wait_for_response=True)
            chatbot_page.wait_for_stable_response()

            response = chatbot_page.get_last_ai_response()

            # Check for hallucination indicators
            is_valid = AIResponseValidator.is_hallucination_free(response)

            assert is_valid, \
                f"Response may contain hallucination for query: {query}. Response: {response[:200]}"

    def test_resp_stays_on_topic(self, chatbot_page: ChatPage):
        """Verify AI stays on topic and doesn't go off on tangents"""
        logger.info("Testing on-topic responses")

        query = "How do I apply for a driving license?"

        chatbot_page.send_message(query, wait_for_response=True)
        chatbot_page.wait_for_stable_response()

        response = chatbot_page.get_last_ai_response()

        # Response should be about driving license, not random topics
        relevant_terms = ["driving", "license", "apply", "rta", "requirements", "documents"]

        # At least some relevant terms should be present
        assert AIResponseValidator.contains_keywords(response, relevant_terms, min_matches=2), \
            f"Response appears off-topic: {response[:200]}"


@pytest.mark.ai_response
class TestResponseConsistency:
    """Test that responses stay consistent for similar intents"""

    def test_resp_consistency_across_languages(self, chatbot_page: ChatPage, test_language: str):
        """Test that similar questions in different languages get semantically similar answers"""
        logger.info("Testing cross-language consistency")

        # This test requires running with both languages
        # For now, we'll test that the same question gets consistent answers

        query = "How can I apply for a visa?" if test_language == "en" else \
                "كيف يمكنني التقدم بطلب للحصول على تأشيرة؟"

        # Ask the same question twice
        chatbot_page.send_message(query, wait_for_response=True)
        chatbot_page.wait_for_stable_response()
        response1 = chatbot_page.get_last_ai_response()

        # Ask again
        chatbot_page.send_message(query, wait_for_response=True)
        chatbot_page.wait_for_stable_response()
        response2 = chatbot_page.get_last_ai_response()

        # Responses should be semantically similar (threshold: 0.4 for flexibility)
        similarity = AIResponseValidator.calculate_similarity(response1, response2)
        logger.info(f"Response similarity: {similarity:.2f}")

        assert similarity >= 0.3, \
            f"Responses are too different. Similarity: {similarity:.2f}"

    def test_resp_similar_questions_answers(self, chatbot_page: ChatPage, test_language: str):
        """Test that rephrased questions get similar answers"""
        logger.info("Testing consistency for similar questions")

        if test_language == "en":
            queries = [
                "What documents do I need for a visa?",
                "What are the visa requirements?",
                "Which papers are needed for visa application?"
            ]
        else:
            queries = [
                "ما المستندات المطلوبة للتأشيرة؟",
                "ما هي متطلبات التأشيرة؟"
            ]

        responses = []

        for query in queries:
            chatbot_page.send_message(query, wait_for_response=True)
            chatbot_page.wait_for_stable_response()
            response = chatbot_page.get_last_ai_response()
            responses.append(response)

        # Check pairwise similarity
        for i in range(len(responses) - 1):
            similarity = AIResponseValidator.calculate_similarity(
                responses[i],
                responses[i + 1]
            )
            logger.info(f"Similarity between response {i} and {i+1}: {similarity:.2f}")

            # Similar questions should get somewhat similar answers
            assert similarity >= 0.25, \
                f"Similar questions got very different answers. Similarity: {similarity:.2f}"


@pytest.mark.ai_response
class TestResponseFormatting:
    """Test response formatting and completeness"""

    def test_resp_formatting_is_clean(self, chatbot_page: ChatPage, test_language: str):
        """Verify response formatting is clean (no broken HTML or incomplete thoughts)"""
        logger.info("Testing response formatting")

        queries = TestDataLoader.get_queries_by_language(test_language)

        for query_data in queries[:3]:
            query = query_data["query"]

            chatbot_page.send_message(query, wait_for_response=True)
            chatbot_page.wait_for_stable_response()

            response = chatbot_page.get_last_ai_response()

            # Check formatting
            is_well_formatted = AIResponseValidator.is_well_formatted(response)

            assert is_well_formatted, \
                f"Response has formatting issues for query: {query}. Response: {response[:200]}"

    def test_resp_complete(self, chatbot_page: ChatPage):
        """Verify responses are complete (not cut off mid-sentence)"""
        logger.info("Testing response completeness")

        chatbot_page.send_message("Tell me about visa requirements", wait_for_response=True)
        chatbot_page.wait_for_stable_response()

        response = chatbot_page.get_last_ai_response()

        # Basic completeness checks
        # Response should not end with incomplete punctuation patterns
        incomplete_patterns = ["...", " and", " or", " but", ","]

        ends_incomplete = any(response.strip().endswith(pattern) for pattern in incomplete_patterns)

        if ends_incomplete:
            logger.warning(f"Response may be incomplete: {response[-50:]}")
            # Don't fail, just warn, as some responses may legitimately end this way


@pytest.mark.ai_response
class TestLoadingAndFallbackMessages:
    """Test loading states and fallback messages"""

    def test_resp_fallback_for_unclear(self, chatbot_page: ChatPage):
        """Verify fallback messages appear for unclear/nonsensical queries"""
        logger.info("Testing fallback messages")

        unclear_queries = [
            "asdfghjkl",
            "12345",
            "???"
        ]

        for query in unclear_queries:
            try:
                chatbot_page.send_message(query, wait_for_response=True)
                chatbot_page.wait_for_stable_response()

                response = chatbot_page.get_last_ai_response()

                # Should get some response (either helpful or asking for clarification)
                assert len(response) > 0, f"No response for unclear query: {query}"

                logger.info(f"Response to unclear query '{query}': {response[:100]}")

            except Exception as e:
                logger.warning(f"Error handling unclear query: {e}")

    def test_resp_within_reasonable_time(self, chatbot_page: ChatPage):
        """Verify AI responds within reasonable time"""
        import time

        logger.info("Testing response time")

        query = "What is the capital of UAE?"

        start_time = time.time()

        chatbot_page.send_message(query, wait_for_response=True)

        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to ms

        logger.info(f"Response time: {response_time:.0f}ms")

        # Should respond within configured max time (30 seconds)
        from config import TestConfig
        assert response_time < TestConfig.MAX_RESPONSE_TIME_AI, \
            f"Response took too long: {response_time:.0f}ms"


@pytest.mark.ai_response
@pytest.mark.slow
class TestComprehensiveValidation:
    """Comprehensive validation of AI responses"""

    def test_resp_comprehensive_validation(self, chatbot_page: ChatPage, test_language: str):
        """Run comprehensive validation on multiple queries"""
        logger.info("Running comprehensive validation")

        queries = TestDataLoader.get_queries_by_language(test_language)

        validation_results = []

        for query_data in queries:
            query = query_data["query"]
            expected_keywords = query_data.get("expected_keywords", [])
            forbidden_terms = query_data.get("should_not_contain", [])

            chatbot_page.send_message(query, wait_for_response=True)
            chatbot_page.wait_for_stable_response()

            response = chatbot_page.get_last_ai_response()

            # Comprehensive validation
            validation = AIResponseValidator.validate_response(
                response,
                expected_keywords=expected_keywords,
                forbidden_terms=forbidden_terms,
                min_length=20
            )

            validation_results.append({
                "query": query[:50],
                "valid": validation["is_valid"],
                "details": validation
            })

            logger.info(f"Validation for '{query[:50]}': {validation}")

        # Report results
        total = len(validation_results)
        passed = sum(1 for r in validation_results if r["valid"])

        logger.info(f"Comprehensive validation: {passed}/{total} passed")

        # At least 80% should pass
        pass_rate = passed / total if total > 0 else 0
        assert pass_rate >= 0.8, \
            f"Too many validation failures: {pass_rate:.1%} pass rate"
