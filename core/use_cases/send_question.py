from dataclasses import dataclass
from typing import Optional

from core.domain.messages import UserMessage, BotMessage
from core.domain.ports import ChatPort, ResponseReaderPort, CaptchaPort


@dataclass
class SendQuestionResult:
    success: bool
    response: Optional[BotMessage]
    captcha_detected: bool
    captcha_solved: bool


def send_question(
    chat: ChatPort,
    reader: ResponseReaderPort,
    captcha: CaptchaPort,
    url: str,
    message_text: str,
    wait_response_ms: int = 30000,
) -> SendQuestionResult:
    chat.navigate(url)
    chat.ensure_ready(timeout_ms=10000)

    captcha_detected = captcha.detected()
    captcha_solved = False
    if captcha_detected:
        captcha_solved = captcha.wait_until_solved(timeout_sec=60)
        if captcha_solved:
            captcha.save_session()

    chat.type_and_send(UserMessage(text=message_text))
    reader.wait_for_response(timeout_ms=wait_response_ms)
    bot = reader.read_last()

    return SendQuestionResult(
        success=bot is not None and bool(bot.text.strip()),
        response=bot,
        captcha_detected=captcha_detected,
        captcha_solved=captcha_solved,
    )


