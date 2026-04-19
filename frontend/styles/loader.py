"""CSS 로더.

`frontend/assets/css/` 아래의 분리된 .css 파일들을 읽어
하나의 <style> 블록으로 합쳐 Streamlit 페이지에 주입합니다.

로드 순서 (CSS cascade 제어):
    1) 루트의 00_base.css, 10_layout.css, 20_widgets.css  (숫자 프리픽스 오름차순)
    2) components/ 폴더의 모든 .css                       (알파벳 오름차순)

components 는 widgets 뒤에 로드되므로, 필요 시 위젯 오버라이드보다
더 구체적인 셀렉터로 추가 커스텀을 걸 수 있습니다.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

# frontend/styles/loader.py → frontend/assets/css
_CSS_DIR: Path = Path(__file__).resolve().parent.parent / "assets" / "css"


def _read(path: Path) -> str:
    """파일 경로에 섹션 헤더를 붙여 읽어옵니다 (디버깅 가독성)."""
    rel = path.relative_to(_CSS_DIR)
    return f"\n/* ===== {rel.as_posix()} ===== */\n{path.read_text(encoding='utf-8')}"


@st.cache_data(show_spinner=False)
def _load_all_css() -> str:
    """분리된 모든 CSS 파일을 정해진 순서대로 읽어 하나의 문자열로 합칩니다."""
    if not _CSS_DIR.exists():
        raise FileNotFoundError(f"CSS 디렉토리를 찾을 수 없습니다: {_CSS_DIR}")

    parts: list[str] = []

    # 1) 루트 레벨: 숫자 프리픽스 기준 정렬 → base → layout → widgets
    root_css_files = sorted(
        p for p in _CSS_DIR.glob("*.css") if p.is_file()
    )
    for p in root_css_files:
        parts.append(_read(p))

    # 2) components/ : 알파벳 순서
    components_dir = _CSS_DIR / "components"
    if components_dir.exists():
        for p in sorted(components_dir.glob("*.css")):
            parts.append(_read(p))

    return "\n".join(parts)


def inject_css() -> None:
    """분리된 전역 CSS를 Streamlit 페이지에 주입합니다.

    `st.cache_data` 덕분에 실제 파일 I/O 는 세션당 최초 1회만 발생합니다.
    """
    css = _load_all_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
