from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UserMessage:
    text: str


@dataclass(frozen=True)
class BotMessage:
    text: str
    raw_html: Optional[str] = None


