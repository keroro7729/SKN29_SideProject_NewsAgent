"""frontend.styles 패키지.

전역 CSS 주입 API를 제공합니다.
외부에서는 다음처럼 사용하세요:

    from styles import inject_css
    inject_css()
"""

from .loader import inject_css

__all__ = ["inject_css"]
