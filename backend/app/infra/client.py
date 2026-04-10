import logging
import os
import time
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional

# OpenAI 공식 SDK에서 클라이언트와 발생 가능한 에러 타입들을 가져옴
from openai import (
    APIConnectionError,   # 네트워크 연결 자체가 안 될 때
    APITimeoutError,      # 응답이 너무 오래 걸릴 때
    AuthenticationError,  # API 키가 틀렸을 때
    OpenAI,               # OpenAI 클라이언트 본체
    RateLimitError,       # API 호출 한도를 초과했을 때
)

# 로거 설정: 이 모듈에서 발생하는 로그를 기록하는 객체
# 호출한 쪽(예: Streamlit 앱)에서 logging 설정을 하면 자동으로 연결됨
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
#  사용 가능한 모델 목록                                               #
# ------------------------------------------------------------------ #

# OpenAI에서 현재 지원하는 모델 이름 목록
# 초기화 시 이 목록에 없는 모델명을 넣으면 즉시 에러를 발생시켜
# 잘못된 모델명으로 API를 호출하는 상황을 사전에 방지함
SUPPORTED_MODELS = {
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-4o",
    "gpt-4o-mini",
}


# ------------------------------------------------------------------ #
#  응답 데이터 구조                                                    #
# ------------------------------------------------------------------ #

# @dataclass: 데이터를 담는 클래스를 간결하게 선언하는 파이썬 문법
# send_message()가 단순 문자열 대신 이 객체를 반환해서
# 텍스트 응답과 토큰 사용량을 한 번에 전달할 수 있음
@dataclass
class LLMResponse:
    text: str          # AI가 생성한 응답 텍스트
    input_tokens: int  # 입력(질문)에 사용된 토큰 수 → 비용 계산에 활용
    output_tokens: int # 출력(응답)에 사용된 토큰 수 → 비용 계산에 활용

    @property
    def total_tokens(self) -> int:
        # input + output 토큰 합계를 편하게 꺼낼 수 있도록 제공
        # 사용 예: result.total_tokens
        return self.input_tokens + self.output_tokens


# ------------------------------------------------------------------ #
#  메인 클라이언트 클래스                                              #
# ------------------------------------------------------------------ #

class OpenAIClient:
    """
    팀 공용 OpenAI 호출 클라이언트.

    팀원들이 뉴스 요약, 검색어 생성 등 어떤 용도로든
    동일한 방식으로 LLM을 호출할 수 있도록 만든 공용 모듈.

    사용 예:
        client = OpenAIClient()
        result = client.send_message(
            system_prompt="뉴스를 3줄로 요약하는 AI입니다.",
            user_input="오늘 뉴스 내용...",
        )
        print(result.text)
        print(result.total_tokens)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,   # 직접 넘겨도 되고, 환경변수로 설정해도 됨
        model: Optional[str] = None,      # 모델 미지정 시 환경변수 또는 기본값 사용
        timeout: float = 20.0,            # OpenAI 응답 대기 최대 시간 (초 단위)
    ):
        # API 키 설정: 직접 전달 → 환경변수 순으로 확인
        # 둘 다 없으면 즉시 에러 발생 (키 없이 API 호출 불가)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

        # 모델 설정: 직접 전달 → 환경변수 → 기본값(gpt-4.1) 순으로 확인
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4.1")

        # 지원하지 않는 모델명이면 API 호출 전에 즉시 에러 발생
        # API를 실제로 호출한 뒤 에러를 받는 것보다 훨씬 빠르게 문제를 잡을 수 있음
        if self.model not in SUPPORTED_MODELS:
            raise ValueError(
                f"지원하지 않는 모델: '{self.model}'. "
                f"사용 가능한 모델: {sorted(SUPPORTED_MODELS)}"
            )

        # OpenAI 클라이언트 생성: 이후 모든 API 호출은 이 객체를 통해 이루어짐
        self.client = OpenAI(api_key=self.api_key, timeout=timeout)

        logger.info(f"[OpenAIClient] 초기화 완료 | model={self.model}")

    # ------------------------------------------------------------------ #
    #  내부 유틸 메서드 (외부에서 직접 호출하지 않음)                     #
    # ------------------------------------------------------------------ #

    def _validate_system_prompt(self, system_prompt: str) -> None:
        """
        system_prompt가 유효한 문자열인지 검사.
        빈 문자열이나 공백만 있는 경우 에러 발생.
        메서드 이름 앞의 _ 는 내부 전용임을 나타내는 파이썬 관례.
        """
        if not isinstance(system_prompt, str) or not system_prompt.strip():
            raise ValueError("system_prompt는 비어 있지 않은 문자열이어야 합니다.")

    def _build_input(
        self,
        history: Optional[List[Dict[str, str]]],  # 이전 대화 내역
        user_input: str,                           # 이번에 보낼 사용자 메시지
    ) -> List[Dict]:
        """
        OpenAI Responses API가 요구하는 input 배열 형식으로 변환.

        history(이전 대화) + user_input(현재 질문)을 합쳐서
        API가 이해할 수 있는 구조로 만들어 반환.

        반환 예시:
        [
            {"role": "user",      "content": [{"type": "input_text",  "text": "안녕"}]},
            {"role": "assistant", "content": [{"type": "output_text", "text": "안녕하세요"}]},
            {"role": "user",      "content": [{"type": "input_text",  "text": "오늘 날씨는?"}]},
        ]
        """
        if not isinstance(user_input, str) or not user_input.strip():
            raise ValueError("user_input은 비어 있지 않은 문자열이어야 합니다.")

        history = history or []

        # 최근 대화 20개(10쌍)만 유지: 너무 오래된 대화는 잘라냄
        # 토큰 낭비 방지 + API 입력 길이 제한 대응
        recent = history[-20:]

        # user/assistant 가 반드시 쌍을 이루어야 API가 정상 동작함
        # 홀수 개이면 가장 오래된 메시지 1개를 제거해서 짝수로 맞춤
        if len(recent) % 2 != 0:
            recent = recent[1:]

        input_items = []

        for msg in recent:
            role = msg.get("role")
            content = msg.get("content", "")

            # user / assistant 외의 role은 지원하지 않음
            if role not in ("user", "assistant"):
                raise ValueError(f"지원하지 않는 role입니다: '{role}'")

            if not isinstance(content, str) or not content.strip():
                raise ValueError("history의 content는 비어 있지 않은 문자열이어야 합니다.")

            # Responses API 규칙:
            # user 메시지   → content type: "input_text"
            # assistant 메시지 → content type: "output_text"
            content_type = "input_text" if role == "user" else "output_text"
            input_items.append(
                {"role": role, "content": [{"type": content_type, "text": content}]}
            )

        # 현재 사용자 입력을 맨 마지막에 추가
        input_items.append(
            {"role": "user", "content": [{"type": "input_text", "text": user_input}]}
        )

        return input_items

    def _handle_exception(self, e: Exception, attempt: int) -> None:
        """
        에러 종류에 따라 다르게 처리.

        - RateLimitError   : 잠깐 기다렸다가 재시도 (기다리는 시간은 시도할수록 늘어남)
        - AuthenticationError : API 키 문제이므로 재시도해도 소용없음 → 즉시 중단
        - APITimeoutError  : 타임아웃 경고 후 재시도
        - APIConnectionError : 연결 오류 경고 후 재시도
        - 그 외           : 예상치 못한 에러이므로 즉시 중단
        """
        if isinstance(e, RateLimitError):
            # Exponential backoff: 1회 실패 → 2초, 2회 실패 → 4초, 3회 실패 → 8초 대기
            # API 호출이 몰릴 때 서버 부하를 줄이는 표준적인 재시도 전략
            wait = 2 ** attempt
            logger.warning(
                f"[OpenAIClient] Rate limit 초과. {wait}초 후 재시도 (attempt={attempt})"
            )
            time.sleep(wait)
        elif isinstance(e, AuthenticationError):
            # API 키 오류는 재시도해도 해결되지 않으므로 바로 종료
            raise ValueError("API 키가 유효하지 않습니다. OPENAI_API_KEY를 확인하세요.") from e
        elif isinstance(e, APITimeoutError):
            logger.warning(f"[OpenAIClient] 응답 시간 초과 (attempt={attempt})")
        elif isinstance(e, APIConnectionError):
            logger.warning(f"[OpenAIClient] 연결 오류 (attempt={attempt}): {e}")
        else:
            # 위 케이스에 해당하지 않는 예외는 재시도 없이 즉시 올림
            raise RuntimeError(f"OpenAI 호출 실패: {e}") from e

    # ------------------------------------------------------------------ #
    #  외부 공개 메서드 (프론트 담당자가 호출하는 부분)                   #
    # ------------------------------------------------------------------ #

    def send_message(
        self,
        system_prompt: str,                              # AI의 역할/행동 지침
        user_input: str,                                 # 사용자가 입력한 메시지
        history: Optional[List[Dict[str, str]]] = None, # 이전 대화 내역 (없으면 빈 리스트)
        max_output_tokens: int = 800,                    # 응답 최대 토큰 수 (길이 제한)
        max_retries: int = 3,                            # 실패 시 최대 재시도 횟수
    ) -> LLMResponse:
        """
        OpenAI에 메시지를 보내고 응답을 받는 메인 메서드.
        응답 텍스트와 토큰 사용량을 LLMResponse 객체로 반환.

        프론트 담당자 사용 예:
            result = client.send_message(
                system_prompt="뉴스를 3줄로 요약하는 AI입니다.",
                user_input=user_input,
                history=st.session_state.history,
            )
            st.write(result.text)
            st.caption(f"토큰: {result.total_tokens}")
        """
        self._validate_system_prompt(system_prompt)
        input_items = self._build_input(history, user_input)

        logger.info(
            f"[OpenAIClient] send_message 시작 | model={self.model}, "
            f"max_output_tokens={max_output_tokens}, history={len(history or [])}개"
        )

        last_exc: Optional[Exception] = None

        # 실패 시 max_retries 횟수만큼 재시도
        for attempt in range(max_retries):
            try:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=system_prompt,  # system 역할은 instructions 파라미터로 전달
                    input=input_items,
                    max_output_tokens=max_output_tokens,
                )

                # 응답 텍스트 추출 및 공백 제거
                text = (response.output_text or "").strip()
                if not text:
                    raise RuntimeError("응답은 성공했지만 output_text가 비어 있습니다.")

                # 토큰 사용량 추출 (usage가 없는 경우 0으로 처리)
                usage = response.usage
                result = LLMResponse(
                    text=text,
                    input_tokens=usage.input_tokens if usage else 0,
                    output_tokens=usage.output_tokens if usage else 0,
                )

                logger.info(
                    f"[OpenAIClient] 완료 | "
                    f"input_tokens={result.input_tokens}, "
                    f"output_tokens={result.output_tokens}"
                )
                return result

            except Exception as e:
                last_exc = e
                # 에러 종류 판단: 재시도 가능한 에러면 기다렸다가 루프 계속
                # 재시도 불가 에러(AuthenticationError 등)면 즉시 예외 발생
                self._handle_exception(e, attempt)

        # max_retries 횟수를 모두 소진했을 때
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
        """
        응답을 스트리밍(조각 단위)으로 받는 메서드.
        응답이 생성되는 즉시 조각씩 yield해서 타이핑 효과를 낼 수 있음.

        send_message()와 차이:
            send_message()   → 응답 전체가 완성된 뒤 한 번에 반환
            stream_message() → 응답이 생성되는 즉시 조각씩 반환 (UX 개선)

        프론트 담당자 사용 예 (Streamlit):
            st.write_stream(
                client.stream_message(
                    system_prompt="뉴스를 3줄로 요약하는 AI입니다.",
                    user_input=user_input,
                )
            )
        """
        self._validate_system_prompt(system_prompt)
        input_items = self._build_input(history, user_input)

        logger.info(f"[OpenAIClient] stream_message 시작 | model={self.model}")

        try:
            # responses.stream: 응답을 이벤트 단위로 수신하는 스트리밍 모드
            with self.client.responses.stream(
                model=self.model,
                instructions=system_prompt,
                input=input_items,
                max_output_tokens=max_output_tokens,
            ) as stream:
                for event in stream:
                    # 각 이벤트에서 텍스트 조각(delta)을 꺼내 yield
                    # delta가 없는 이벤트(연결 확인용 등)는 건너뜀
                    delta = getattr(event, "delta", None)
                    if delta:
                        yield delta
        except Exception as e:
            raise RuntimeError(f"스트리밍 호출 실패: {e}") from e