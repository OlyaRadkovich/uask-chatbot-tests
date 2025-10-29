from typing import Protocol, Optional
from .messages import UserMessage, BotMessage


class ChatPort(Protocol):
    """Low-level port to interact with chat UI"""

    def navigate(self, url: str) -> None: ...
    def ensure_ready(self, timeout_ms: int) -> None: ...
    def type_and_send(self, message: UserMessage) -> None: ...


class ResponseReaderPort(Protocol):
    """Reads last bot response from UI"""

    def wait_for_response(self, timeout_ms: int) -> None: ...
    def read_last(self) -> Optional[BotMessage]: ...


class CaptchaPort(Protocol):
    """Detects and resolves CAPTCHA (manual wait hook)"""

    def detected(self) -> bool: ...
    def wait_until_solved(self, timeout_sec: int) -> bool: ...
    def save_session(self) -> bool: ...


