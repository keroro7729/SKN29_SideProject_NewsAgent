import random
import plotly.graph_objects as go
import plotly.express as px


# ── 공통 색상 팔레트 ─────────────────────────────────────────────────────────
PALETTE = {
    "bg":      "rgba(0,0,0,0)",   # 투명 배경 (앱 배경색과 통일)
    "pos":     "#2d6a4f",          # 긍정 – 딥 그린
    "neg":     "#c1440e",          # 부정 – 번트 오렌지
    "neu":     "#b0a898",          # 중립 – 워럼 그레이
    "line":    "#111111",          # 트렌드 라인
    "fill":    "rgba(17,17,17,.06)",
    "amber":   "#e8a020",          # 포인트 컬러
    "grid":    "#ece9e3",          # 그리드 라인
}

FONT_FAMILY = "IBM Plex Sans"
SERIF_FAMILY = "Playfair Display"


# ── 감성 분석 도넛 차트 ───────────────────────────────────────────────────────
def sentiment_donut(pos: int, neg: int, neu: int) -> go.Figure:
    """
    긍정/부정/중립 비율을 도넛 차트로 시각화합니다.

    Parameters
    ----------
    pos, neg, neu : int   각 감성 비율 (합 = 100)

    Returns
    -------
    go.Figure  Streamlit st.plotly_chart() 에 바로 전달 가능
    """
    labels = ["긍정", "부정", "중립"]
    values = [pos, neg, neu]
    colors = [PALETTE["pos"], PALETTE["neg"], PALETTE["neu"]]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(colors=colors, line=dict(color="#f5f3ef", width=3)),
        textinfo="label+percent",
        textfont=dict(family=FONT_FAMILY, size=12, color="#111"),
        direction="clockwise",
        sort=False,
    )])

    # 도넛 중앙 텍스트: 긍정 비율 강조
    dominant = max(zip(values, labels), key=lambda x: x[0])
    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor=PALETTE["bg"],
        plot_bgcolor=PALETTE["bg"],
        annotations=[dict(
            text=f"<b>{dominant[0]}%</b><br><span style='font-size:11px'>{dominant[1]}</span>",
            x=0.5, y=0.5,
            font=dict(family=SERIF_FAMILY, size=20, color="#111"),
            showarrow=False,
        )],
    )
    return fig


# ── 주간 트렌드 라인 차트 ────────────────────────────────────────────────────
def weekly_trend(query: str, values: list[int] | None = None) -> go.Figure:
    """
    검색어의 주간 언급량 트렌드를 라인 차트로 시각화합니다.

    Parameters
    ----------
    query  : str           검색어 (차트 제목에 사용)
    values : list[int]     7개 값 (월~일). None이면 랜덤 생성.

    Returns
    -------
    go.Figure
    """
    days = ["월", "화", "수", "목", "금", "토", "일"]
    if values is None or len(values) != 7:
        values = [random.randint(15, 95) for _ in days]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=days,
        y=values,
        mode="lines+markers",
        line=dict(color=PALETTE["line"], width=2.5),
        marker=dict(color=PALETTE["amber"], size=9, symbol="circle",
                    line=dict(color="#111", width=1.5)),
        fill="tozeroy",
        fillcolor=PALETTE["fill"],
        hovertemplate="%{x}: %{y}건<extra></extra>",
    ))

    peak_idx = values.index(max(values))
    fig.add_annotation(
        x=days[peak_idx], y=values[peak_idx],
        text=f"최고 {values[peak_idx]}건",
        showarrow=True, arrowhead=2, arrowcolor=PALETTE["amber"],
        font=dict(family=FONT_FAMILY, size=11, color="#111"),
        bgcolor="white", bordercolor=PALETTE["amber"], borderwidth=1.5,
        ay=-36,
    )

    fig.update_layout(
        title=dict(
            text=f"「{query}」 주간 언급량",
            font=dict(family=SERIF_FAMILY, size=17, color="#111"),
            x=0,
        ),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(family=FONT_FAMILY, size=12),
            linecolor="#111", linewidth=1.5,
        ),
        yaxis=dict(
            showgrid=True, gridcolor=PALETTE["grid"],
            tickfont=dict(family=FONT_FAMILY, size=11),
            ticksuffix="건",
            zeroline=False,
        ),
        paper_bgcolor=PALETTE["bg"],
        plot_bgcolor=PALETTE["bg"],
        margin=dict(t=50, b=40, l=50, r=20),
        hovermode="x unified",
    )
    return fig


# ── 카테고리별 뉴스 건수 바 차트 ────────────────────────────────────────────
def category_bar(counts: dict[str, int]) -> go.Figure:
    """
    카테고리별 기사 수를 수평 바 차트로 시각화합니다.

    Parameters
    ----------
    counts : dict  {"사회": 12, "경제": 8, ...}

    Returns
    -------
    go.Figure
    """
    cats   = list(counts.keys())
    values = list(counts.values())
    colors = [PALETTE["amber"] if v == max(values) else "#ddd9d2" for v in values]

    fig = go.Figure(go.Bar(
        x=values, y=cats,
        orientation="h",
        marker=dict(color=colors, line=dict(color="#111", width=1)),
        text=values,
        textposition="outside",
        textfont=dict(family=FONT_FAMILY, size=12),
        hovertemplate="%{y}: %{x}건<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor=PALETTE["bg"],
        plot_bgcolor=PALETTE["bg"],
        margin=dict(t=10, b=10, l=80, r=40),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(
            tickfont=dict(family=FONT_FAMILY, size=13),
            categoryorder="total ascending",
        ),
        showlegend=False,
        height=220,
    )
    return fig


# ── 감성 히스토리 라인 (더미) ────────────────────────────────────────────────
def sentiment_history(query: str) -> go.Figure:
    """
    최근 7일간 긍정·부정 언급 추이를 멀티라인 차트로 시각화합니다.
    (더미 데이터: 실제 API 연결 시 데이터 교체)
    """
    days = ["월", "화", "수", "목", "금", "토", "일"]
    pos_vals = [random.randint(30, 65) for _ in days]
    neg_vals = [random.randint(10, 40) for _ in days]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=days, y=pos_vals, name="긍정",
        mode="lines+markers",
        line=dict(color=PALETTE["pos"], width=2),
        marker=dict(size=7),
    ))
    fig.add_trace(go.Scatter(
        x=days, y=neg_vals, name="부정",
        mode="lines+markers",
        line=dict(color=PALETTE["neg"], width=2, dash="dot"),
        marker=dict(size=7),
    ))

    fig.update_layout(
        title=dict(
            text=f"「{query}」 감성 추이 (7일)",
            font=dict(family=SERIF_FAMILY, size=16, color="#111"),
            x=0,
        ),
        legend=dict(
            font=dict(family=FONT_FAMILY, size=12),
            bgcolor="rgba(0,0,0,0)",
            orientation="h", x=0, y=1.15,
        ),
        xaxis=dict(showgrid=False, tickfont=dict(family=FONT_FAMILY, size=12)),
        yaxis=dict(
            showgrid=True, gridcolor=PALETTE["grid"],
            tickfont=dict(family=FONT_FAMILY, size=11),
            ticksuffix="%",
        ),
        paper_bgcolor=PALETTE["bg"],
        plot_bgcolor=PALETTE["bg"],
        margin=dict(t=50, b=30, l=50, r=20),
    )
    return fig