"""
Test helper utilities (renamed)
"""
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from config import DATA_DIR, SCREENSHOTS_DIR, TEST_DATA_FILE, REPORTS_DIR
import logging

logger = logging.getLogger(__name__)


class TestDataLoader:
    @staticmethod
    def load_test_data(file_path: Optional[Path] = None) -> Dict[str, Any]:
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
        data = TestDataLoader.load_test_data()
        queries = data.get("valid_queries", {}).get(language, [])
        logger.info(f"Loaded {len(queries)} queries for language: {language}")
        return queries

    @staticmethod
    def get_security_tests(category: str = None) -> Dict[str, list]:
        data = TestDataLoader.load_test_data()
        security_tests = data.get("security_tests", {})
        if category:
            return {category: security_tests.get(category, [])}
        return security_tests

    @staticmethod
    def get_edge_cases(language: str = "en") -> list:
        data = TestDataLoader.load_test_data()
        return data.get("edge_cases", {}).get(language, [])


class ScreenshotHelper:
    @staticmethod
    def generate_screenshot_name(test_name: str, status: str = "failed") -> str:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = test_name.replace("/", "_").replace(" ", "_")
        return f"{safe_name}_{status}_{timestamp}.png"

    @staticmethod
    def save_screenshot_metadata(screenshot_path: str, test_name: str, metadata: Dict[str, Any]) -> None:
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
    @staticmethod
    def save_test_execution_summary(test_results: Dict[str, Any], output_file: str = "test_summary.json") -> None:
        output_path = REPORTS_DIR / output_file
        summary = {"execution_time": datetime.datetime.now().isoformat(), "results": test_results}
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            logger.info(f"Test summary saved: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save test summary: {e}")


def wait_with_retry(func, max_retries: int = 3, delay: int = 2, exceptions: tuple = (Exception,)) -> Any:
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
    if not text:
        return ""
    sanitized = text
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    return sanitized
