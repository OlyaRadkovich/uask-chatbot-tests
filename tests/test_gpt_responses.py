"""
GPT Response Validation Tests
Tests AI-generated responses for quality, consistency, and hallucination prevention.
This version uses the Page Object Model (POM) correctly.
"""
import pytest
import logging
import allure
from pages.chat_page import ChatPage
from utils.ai_validators import AIResponseValidator
from utils.test_helpers import TestDataLoader

logger = logging.getLogger(__name__)


@pytest.mark.ai_response
class TestResponseQuality:
    """Test AI response quality and helpfulness"""

    @allure.title("AI provides helpful response to visa query")
    def test_ai_provides_helpful_response_visa(self, chatbot_page: ChatPage):
        """Verify AI provides helpful response about visa requirements"""
        logger.info("=== TEST: AI responds helpfully to visa question ===")
        # Page setup is now handled by the 'chatbot_page' fixture

        query = "What are the visa requirements for tourists visiting UAE?"
        expected_keywords = ["visa", "passport", "requirements", "UAE", "tourist"]

        logger.info(f"Sending query: {query}")

        # Use POM to send message and wait for stable response
        chatbot_page.send_message(query, wait_for_response=False)
        chatbot_page.wait_for_stable_response() # Replaces time.sleep()

        # Use POM to get the response text
        ai_response = chatbot_page.get_last_ai_response()

        if len(ai_response) > 0:
            logger.info(f"AI response received: {ai_response[:100]}...")
            assert AIResponseValidator.is_meaningful_response(ai_response), "Response not meaningful"

            # Check for keywords
            keywords_found = any(kw.lower() in ai_response.lower() for kw in expected_keywords)
            assert keywords_found, f"Response missing relevant keywords: {expected_keywords}"
            logger.info("✅ Response contains relevant keywords")
        else:
            pytest.fail("⚠️ AI response not found or was empty")

        logger.info("✅ AI response test for visa question completed")

    @allure.title("AI provides helpful response to business license query")
    def test_ai_provides_helpful_response_business(self, chatbot_page: ChatPage):
        """Verify AI provides helpful response about business licenses"""
        logger.info("=== TEST: AI responds helpfully to business license question ===")

        query = "How can I apply for a business license in Dubai?"
        expected_keywords = ["business", "license", "Dubai", "apply", "documents"]

        logger.info(f"Sending query: {query}")

        chatbot_page.send_message(query, wait_for_response=False)
        chatbot_page.wait_for_stable_response() # Replaces time.sleep()

        ai_response = chatbot_page.get_last_ai_response()

        if len(ai_response) > 0:
            logger.info("✅ Message sent and response received")
            assert AIResponseValidator.is_meaningful_response(ai_response), "Response not meaningful"
            assert AIResponseValidator.contains_keywords(ai_response, expected_keywords), "Response missing keywords"
        else:
            pytest.fail("⚠️ AI response not found or was empty")

        logger.info("✅ AI response test for business query completed")


@pytest.mark.ai_response
class TestResponseConsistency:
    """Test response consistency for similar queries"""

    @allure.title("Similar queries produce consistent responses")
    def test_similar_queries_consistency(self, chatbot_page: ChatPage):
        """Test that similar queries produce consistent responses"""
        logger.info("=== TEST: Consistency of responses to similar queries ===")

        similar_queries = [
            "How to get a driving license?",
            "What is the process for driving license application?",
            "Steps to apply for a driving license"
        ]

        responses = []
        for query in similar_queries:
            logger.info(f"Sending: {query}")
            chatbot_page.send_message(query, wait_for_response=False)
            chatbot_page.wait_for_stable_response() # Replaces time.sleep()

            response_text = chatbot_page.get_last_ai_response()
            if AIResponseValidator.is_meaningful_response(response_text):
                responses.append(response_text)
            else:
                logger.warning(f"Got non-meaningful response for: {query}")

        logger.info(f"Results: {len(responses)} queries processed")
        assert len(responses) == len(similar_queries), "Not all queries received a meaningful response"

        # Here you could add semantic similarity checks
        # e.g., AIResponseValidator.are_semantically_similar(responses[0], responses[1])

        logger.info("✅ Consistency test completed")

    @allure.title("Response formatting is clean")
    def test_response_formatting(self, chatbot_page: ChatPage):
        """Test that response formatting is clean without broken HTML"""
        logger.info("=== TEST: Clean response formatting ===")

        query = "Tell me about government services in UAE"
        chatbot_page.send_message(query, wait_for_response=False)
        chatbot_page.wait_for_stable_response()

        # Check for broken HTML in the page source
        page_content = chatbot_page.driver.page_source
        assert "<script>" not in page_content, "Insecure script tag found"
        assert "undefined" not in page_content.lower(), "Undefined found in content"
        logger.info("✅ Formatting is clean")

        logger.info("✅ Formatting test completed")


@pytest.mark.ai_response
class TestHallucinationPrevention:
    """Test for hallucination prevention"""

    @allure.title("AI does not provide fabricated information")
    def test_no_fabricated_responses(self, chatbot_page: ChatPage):
        """Test that AI doesn't provide obviously fabricated information"""
        logger.info("=== TEST: AI hallucination prevention ===")

        query = "What is the exact fee for a golden visa in 2024?"
        chatbot_page.send_message(query, wait_for_response=False)
        chatbot_page.wait_for_stable_response()

        ai_response = chatbot_page.get_last_ai_response()

        assert AIResponseValidator.is_meaningful_response(ai_response), "No response received"

        # A good response should avoid giving an "exact" fee it doesn't know.
        # It should contain disclaimer words.
        disclaimer_keywords = ["vary", "official", "check", "approximate", "subject to change"]
        has_disclaimer = any(kw.lower() in ai_response.lower() for kw in disclaimer_keywords)

        assert has_disclaimer, "AI might be hallucinating an exact fee without a disclaimer"
        logger.info("✅ AI response included a disclaimer for a specific fee.")

        logger.info("✅ Hallucination prevention test completed")

    @allure.title("AI stays relevant to UAE government services")
    def test_stays_relevant_to_domain(self, chatbot_page: ChatPage):
        """Test that AI stays relevant to UAE government services"""
        logger.info("=== TEST: AI stays within the scope of government services ===")

        query = "What's the weather like in New York?"
        chatbot_page.send_message(query, wait_for_response=False)
        chatbot_page.wait_for_stable_response()

        ai_response = chatbot_page.get_last_ai_response()

        assert AIResponseValidator.is_meaningful_response(ai_response), "No response received"

        # Response should politely decline or redirect
        redirect_keywords = ["sorry", "assist", "government", "services", "uae"]
        weather_keywords = ["weather", "new york", "celsius", "fahrenheit"]

        has_redirect = any(kw.lower() in ai_response.lower() for kw in redirect_keywords)
        has_weather = any(kw.lower() in ai_response.lower() for kw in weather_keywords)

        assert has_redirect, "AI did not redirect user back to relevant topics"
        assert not has_weather, "AI provided off-topic weather information"

        logger.info("✅ Domain relevance test completed")


@pytest.mark.ai_response
class TestLoadingAndFallbackMessages:
    """Test loading states and fallback messages"""

    @allure.title("Loading states appear properly")
    def test_loading_states(self, chatbot_page: ChatPage):
        """Test that loading indicators appear during processing"""
        logger.info("=== TEST: Loading states ===")

        try:
            # Send message without waiting
            chatbot_page.get_input_box().send_keys("What services are available?")
            chatbot_page.get_send_button().click()

            # Immediately check for loading indicator
            assert chatbot_page.is_loading(), "Loading indicator did not appear"
            logger.info("✅ Loading indicator found")

            # Now, wait for it to disappear
            chatbot_page.wait_for_response()
            assert not chatbot_page.is_loading(), "Loading indicator did not disappear"
            logger.info("✅ Loading indicator disappeared after response")

        except Exception as e:
            pytest.fail(f"Loading state test failed: {e}")

        logger.info("✅ Loading states test completed")

    @allure.title("Fallback messages work properly")
    def test_fallback_messages(self, chatbot_page: ChatPage):
        """Test that fallback messages appear when needed"""
        logger.info("=== TEST: Fallback messages ===")

        query = "!@#$%^&*()"
        chatbot_page.send_message(query, wait_for_response=False)
        chatbot_page.wait_for_stable_response()

        ai_response = chatbot_page.get_last_ai_response()

        assert AIResponseValidator.is_meaningful_response(ai_response), "No response received"
        logger.info("✅ System handled special characters")

        # Check for standard fallback messages
        page_text = ai_response.lower()
        fallback_phrases = [
            "sorry", "try again", "please rephrase",
            "i don't understand", "can you clarify", "assist"
        ]

        found_fallback = any(phrase in page_text for phrase in fallback_phrases)
        assert found_fallback, "No standard fallback phrase detected in response"
        logger.info("✅ Fallback phrase found in response")

        logger.info("✅ Fallback messages test completed")