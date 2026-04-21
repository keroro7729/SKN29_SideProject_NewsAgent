"""하위호환용 shim 모듈.

원래는 이 파일에 CSS 문자열이 하드코딩되어 있었으나,
유지보수성을 위해 `frontend/assets/css/` 아래 파일 단위로 분리되었습니다.

기존 호출부(`from styles.global_css import inject_css`)를 깨지 않기 위해
`loader.inject_css`를 그대로 re-export 합니다.

신규 코드에서는 아래 경로를 사용하는 것을 권장합니다.

    from styles import inject_css
"""

from .loader import inject_css

__all__ = ["inject_css"]
