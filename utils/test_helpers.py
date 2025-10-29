"""
Test helper utilities
"""
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from selenium.common.exceptions import WebDriverException
from config import DATA_DIR, SCREENSHOTS_DIR, TEST_DATA_FILE
import logging

logger = logging.getLogger(__name__)


class TestDataLoader:
    """Load and manage test data"""

    @staticmethod
    def load_test_data(file_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Load test data from JSON file

        Args:
            file_path: Path to test data file (uses default if None)

        Returns:
            Dict containing test data
        """
        file_path = file_path or TEST_DATA_FILE

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded test data from {file_path}")
                return data
        except FileNotFoundError:
            logger.error(f"Test data file not found: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in test data file: {e}")
            return {}

    @staticmethod
    def get_queries_by_language(language: str = "en") -> list:
        """
        Get test queries for specific language

        Args:
            language: Language code ('en' or 'ar')

        Returns:
            List of query objects
        """
        data = TestDataLoader.load_test_data()
        queries = data.get("valid_queries", {}).get(language, [])
        logger.info(f"Loaded {len(queries)} queries for language: {language}")
        return queries

    @staticmethod
    def get_security_tests(category: str = None) -> Dict[str, list]:
        """
        Get security test cases

        Args:
            category: Specific category (xss_attempts, prompt_injection, etc.)

        Returns:
            Dict of security test cases
        """
        data = TestDataLoader.load_test_data()
        security_tests = data.get("security_tests", {})

        if category:
            return {category: security_tests.get(category, [])}

        return security_tests

    @staticmethod
    def get_edge_cases(language: str = "en") -> list:
        """
        Get edge case test data

        Args:
            language: Language code

        Returns:
            List of edge case objects
        """
        data = TestDataLoader.load_test_data()
        return data.get("edge_cases", {}).get(language, [])


class ScreenshotHelper:
    """Helper for managing screenshots"""

    @staticmethod
    def generate_screenshot_name(test_name: str, status: str = "failed") -> str:
        """
        Generate unique screenshot filename

        Args:
            test_name: Name of the test
            status: Test status (passed, failed, error)

        Returns:
            Screenshot filename
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = test_name.replace("/", "_").replace(" ", "_")
        return f"{safe_name}_{status}_{timestamp}.png"

    @staticmethod
    def save_screenshot_metadata(
        screenshot_path: str,
        test_name: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Save metadata alongside screenshot

        Args:
            screenshot_path: Path to screenshot file
            test_name: Test name
            metadata: Additional metadata to save
        """
        meta_path = Path(screenshot_path).with_suffix('.json')

        meta_data = {
            "test_name": test_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "screenshot": screenshot_path,
            **metadata
        }

        try:
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved screenshot metadata: {meta_path}")
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")


class ReportHelper:
    """Helper for generating test reports"""

    @staticmethod
    def save_test_execution_summary(
        test_results: Dict[str, Any],
        output_file: str = "test_summary.json"
    ) -> None:
        """
        Save test execution summary

        Args:
            test_results: Dict containing test results
            output_file: Output filename
        """
        from config import REPORTS_DIR

        output_path = REPORTS_DIR / output_file

        summary = {
            "execution_time": datetime.datetime.now().isoformat(),
            "results": test_results
        }

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            logger.info(f"Test summary saved: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save test summary: {e}")


def wait_with_retry(
    func: Callable,
    max_retries: int = 3,
    delay: int = 2,
    exceptions: tuple = (WebDriverException,)  # Updated for Selenium
) -> Any:
    """
    Execute function with retry logic

    Args:
        func: Function to execute
        max_retries: Maximum retry attempts
        delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to catch (defaults to Selenium's WebDriverException)

    Returns:
        Function result

    Raises:
        Last exception if all retries fail
    """
    import time

    last_exception = None

    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")

            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                logger.error(f"All {max_retries} attempts failed")
                raise last_exception


def sanitize_for_display(text: str, max_length: int = 100) -> str:
    """
    Sanitize text for safe display in logs/reports

    Args:
        text: Text to sanitize
        max_length: Maximum length to display

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove potential sensitive data patterns (basic)
    sanitized = text

    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."

    return sanitized
