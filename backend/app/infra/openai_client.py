import logging
import os
import time
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional

from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

logger = logging.getLogger(__name__)

SUPPORTED_MODELS = {
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-4o",
    "gpt-4o-mini",
}


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class OpenAIClient:
    """
    공용 OpenAI 호출 클라이언트 (Responses API).

    사용 예:
        client = OpenAIClient()
        result = client.send_message(
            system_prompt="...",
            user_input="...",
        )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 20.0,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4.1")
        if self.model not in SUPPORTED_MODELS:
            raise ValueError(
                f"지원하지 않는 모델: '{self.model}'. "
                f"사용 가능: {sorted(SUPPORTED_MODELS)}"
            )

        self.client = OpenAI(api_key=self.api_key, timeout=timeout)
        logger.info("[OpenAIClient] 초기화 완료 | model=%s", self.model)

    def _validate_system_prompt(self, system_prompt: str) -> None:
        if not isinstance(system_prompt, str) or not system_prompt.strip():
            raise ValueError("system_prompt는 비어 있지 않은 문자열이어야 합니다.")

    def _build_input(
        self,
        history: Optional[List[Dict[str, str]]],
        user_input: str,
    ) -> List[Dict]:
        if not isinstance(user_input, str) or not user_input.strip():
            raise ValueError("user_input은 비어 있지 않은 문자열이어야 합니다.")

        history = history or []
        recent = history[-20:]
        if len(recent) % 2 != 0:
            recent = recent[1:]

        input_items = []
        for msg in recent:
            role = msg.get("role")
            content = msg.get("content", "")
            if role not in ("user", "assistant"):
                raise ValueError(f"지원하지 않는 role입니다: '{role}'")
            if not isinstance(content, str) or not content.strip():
                raise ValueError("history의 content는 비어 있지 않은 문자열이어야 합니다.")
            content_type = "input_text" if role == "user" else "output_text"
            input_items.append(
                {"role": role, "content": [{"type": content_type, "text": content}]}
            )

        input_items.append(
            {"role": "user", "content": [{"type": "input_text", "text": user_input}]}
        )
        return input_items

    def _handle_exception(self, e: Exception, attempt: int) -> None:
        if isinstance(e, RateLimitError):
            wait = 2**attempt
            logger.warning(
                "[OpenAIClient] Rate limit, %ss 후 재시도 (attempt=%s)",
                wait,
                attempt,
            )
            time.sleep(wait)
        elif isinstance(e, AuthenticationError):
            raise ValueError(
                "API 키가 유효하지 않습니다. OPENAI_API_KEY를 확인하세요."
            ) from e
        elif isinstance(e, APITimeoutError):
            logger.warning("[OpenAIClient] 응답 시간 초과 (attempt=%s)", attempt)
        elif isinstance(e, APIConnectionError):
            logger.warning("[OpenAIClient] 연결 오류 (attempt=%s): %s", attempt, e)
        else:
            raise RuntimeError(f"OpenAI 호출 실패: {e}") from e

    def send_message(
        self,
        system_prompt: str,
        user_input: str,
        history: Optional[List[Dict[str, str]]] = None,
        max_output_tokens: int = 800,
        max_retries: int = 3,
    ) -> LLMResponse:
        self._validate_system_prompt(system_prompt)
        input_items = self._build_input(history, user_input)

        logger.info(
            "[OpenAIClient] send_message | model=%s max_out=%s history=%s",
            self.model,
            max_output_tokens,
            len(history or []),
        )

        last_exc: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=system_prompt,
                    input=input_items,
                    max_output_tokens=max_output_tokens,
                )
                text = (response.output_text or "").strip()
                if not text:
                    raise RuntimeError("응답은 성공했지만 output_text가 비어 있습니다.")

                usage = response.usage
                result = LLMResponse(
                    text=text,
                    input_tokens=usage.input_tokens if usage else 0,
                    output_tokens=usage.output_tokens if usage else 0,
                )
                logger.info(
                    "[OpenAIClient] 완료 | in=%s out=%s",
                    result.input_tokens,
                    result.output_tokens,
                )
                return result
            except Exception as e:
                last_exc = e
                self._handle_exception(e, attempt)

        raise RuntimeError(
            f"OpenAI 호출 {max_retries}회 모두 실패: {last_exc}"
        ) from last_exc

    def stream_message(
        self,
        system_prompt: str,
        user_input: str,
        history: Optional[List[Dict[str, str]]] = None,
        max_output_tokens: int = 800,
    ) -> Iterator[str]:
        self._validate_system_prompt(system_prompt)
        input_items = self._build_input(history, user_input)
        logger.info("[OpenAIClient] stream_message | model=%s", self.model)

        try:
            with self.client.responses.stream(
                model=self.model,
                instructions=system_prompt,
                input=input_items,
                max_output_tokens=max_output_tokens,
            ) as stream:
                for event in stream:
                    delta = getattr(event, "delta", None)
                    if delta:
                        yield delta
        except Exception as e:
            raise RuntimeError(f"스트리밍 호출 실패: {e}") from e
