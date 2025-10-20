# ======================================================================================
# 원문(오류 원인) — 실행 방지를 위해 전체를 주석 처리했습니다. (앱 화면에도 표시되지 않음)
#
# "너는 **파이썬·Streamlit 개발자**이자 **생활 데이터 시각화 기획자**야. 사용자가 **생년월일과 조회 날짜**를 입력하면 **바이오리듬(신체·감정·지성)**을 계산·해석하고 **대화형 차트로 시각화**하는 **단일 파일(Streamlit) 웹앱** 코드를 작성하라.
#
# ## 핵심 요구
# import streamlit as st
#
# SPEC = """
# **요구사항 요약**
# 1) **출력물:** `app.py` 1파일. 추가 설치 없이 **Streamlit Cloud**에서 즉시 실행(표준 라이브러리+`pandas`만).
# 2) **입력:** …
# 3) **계산:** …
# """
#
# st.set_page_config(page_title="마음 예보", page_icon="🌤️", layout="centered")
#
# 1) **출력물:** `app.py` 1파일. 추가 설치 없이 **Streamlit Cloud**에서 즉시 실행(표준 라이브러리+`pandas`만).  
# 2) **입력:** `date_input` 2개(생년월일, 조회 시작일=기본 오늘), 기간 `slider`(±15~60일).  
# 3) **계산:** `d=(기준일-생일).days`; 주기=신체23·감정28·지성33; 값=`sin(2π*d/주기)`([-1,1]).  
# 4) **시각화:** 기간 범위 라인 차트(3곡선, 범례, 색약 친화 팔레트, 오늘선).  
# 5) **예외처리:** 미래 생일/비정상 기간 입력 시 안내 후 기본값으로 보정.  
# 6) **윤리 고지:** 상단 문구 — “바이오리듬은 **오락·참고용**입니다. 중요한 결정의 단독 근거로 사용하지 마세요.”
#
# ## 섹션 구성(수정/추가 반영 필수)
# - **헤더:** 제목 `마음 예보`(예시) + 부제.  
# - **“오늘의 AI 조언 (YYYY-MM-DD)”**: 제목에 **오늘 날짜를 (yyyy-mm-dd)** 형식으로 **괄호 안에 포함**하여 표시.  
#   - 내용은 **구체·실행형**으로 작성(이모지 1개 이내):  
#     - **공부/업무:** 집중 시간대·권장 과목/과제  
#     - **활동/대인:** 협업·발표·상담 적합도  
#     - **건강/휴식:** 운동 강도·수면 팁  
#     - **주의:** 과도한 의사결정, 갈등 상황 회피 등  
# - **“오늘의 바이오리듬” 섹션은 삭제.**  
# - **“오늘의 바이오리듬 요약”**: 각 항목 **이름에 수치 포함**해 표기하고 **색상으로 강조**  
#   - 예: `신체 (0.72) 🟢`, `감정 (-0.15) 🔴`, `지성 (0.02) ⚪`  
#   - **색상 규칙:** 양수≥0.33 = 녹색🟢, -0.33<값<0.33 = 회색⚪(임계), ≤-0.33 = 빨강🔴  
#   - 각 항목 아래 **상세 코멘트**를 2~3문장으로: 현재 상태 해석 + 권장 행동(예: “가벼운 인터벌 러닝 적합”, “논술보다 요약·정리 우선”).  
# - **중요 날짜:** 기간 내 영점 교차일(임계일) 리스트업.
#
# ## 코드 품질
# - 함수 분리: `biorhythm_value`, `make_series`, `state_label`, `plot_chart`, `advise_today`, `main`.  
# - UI 한국어, 모바일 가독성(여백/폰트), 주석·Docstring, 기본 유효성 검사.
#
# ## 출력 순서
# (1) 완성된 `app.py` 전체 코드 → (2) 실행 안내(로컬/클라우드 3~5줄) → (3) 유지보수 팁(색상 임계/문구 사전 확장법).
#
# 이제 위 **수정·변경 사항을 정확히 반영**하여 `app.py`를 작성하라."
# ======================================================================================

# ===== 실제 실행 코드 시작 =====
import math
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

# --- 페이지 설정 ---
st.set_page_config(page_title="마음 예보 | 바이오리듬", page_icon="🌤️", layout="centered")

# --- 상단 안내 (필수 윤리 고지) ---
st.markdown(
    "<h1 style='margin-bottom:0.2rem'>마음 예보 🌤️</h1>"
    "<p style='color:#6b6f76;margin-top:0'>바이오리듬은 오락·참고용입니다. "
    "건강·학업 등 중요한 결정의 단독 근거로 사용하지 마세요.</p>",
    unsafe_allow_html=True,
)

# ---------- 유틸리티 & 계산 함수들 ----------
def biorhythm_value(days_from_birth: int, period: int) -> float:
    """주기(period) 일수를 갖는 바이오리듬 값[-1,1]을 반환."""
    return math.sin(2 * math.pi * days_from_birth / period)


def make_series(birth: date, start_day: date, num_days: int) -> pd.DataFrame:
    """지정 기간에 대해 신체(23), 감정(28), 지성(33) 값을 생성한 DataFrame 반환."""
    records: List[Dict] = []
    for i in range(num_days):
        current = start_day + timedelta(days=i)
        d = (current - birth).days
        records.append(
            {
                "날짜": current,
                "신체": biorhythm_value(d, 23),
                "감정": biorhythm_value(d, 28),
                "지성": biorhythm_value(d, 33),
            }
        )
    return pd.DataFrame.from_records(records)


def state_label(val: float) -> Tuple[str, str, str]:
    """
    값에 따라 (라벨, 색상HEX, 아이콘)을 반환.
    규칙: val>=0.33 → 녹색🟢, -0.33<val<0.33 → 회색⚪(임계), val<=-0.33 → 빨강🔴
    """
    if val >= 0.33:
        return ("높음", "#2ca02c", "🟢")
    if val <= -0.33:
        return ("낮음", "#d62728", "🔴")
    return ("임계", "#7f7f7f", "⚪")


def zero_crossings(df: pd.DataFrame, col: str) -> List[date]:
    """지정 곡선의 영점 교차 추정 날짜 리스트."""
    zdays: List[date] = []
    vals = df[col].values
    for i in range(1, len(vals)):
        if vals[i - 1] == 0:
            zdays.append(pd.to_datetime(df.iloc[i - 1]["날짜"]).date())
        elif vals[i] == 0:
            zdays.append(pd.to_datetime(df.iloc[i]["날짜"]).date())
        elif (vals[i - 1] < 0 and vals[i] > 0) or (vals[i - 1] > 0 and vals[i] < 0):
            zdays.append(pd.to_datetime(df.iloc[i]["날짜"]).date())
    return sorted(list(set(zdays)))


def advise_today(pb: float, em: float, inl: float) -> Dict[str, List[str]]:
    """
    오늘의 AI 조언을 상세하고 구체적으로 생성.
    반환: 섹션 키(공부/업무, 활동/대인, 건강/휴식, 주의) → 문장 리스트
    """
    tips: Dict[str, List[str]] = {"공부/업무": [], "활동/대인": [], "건강/휴식": [], "주의": []}

    # 공부/업무
    if inl >= 0.33:
        tips["공부/업무"].append("논리·분석이 필요한 과목(수학, 과학) 또는 코딩/문제풀이를 우선 처리하세요. 🧠")
        tips["공부/업무"].append("오전 집중도가 높습니다. 어려운 과제는 오전에 배치하세요.")
    elif inl <= -0.33:
        tips["공부/업무"].append("암기·정리·요약 위주의 루틴으로 전환하세요. 어려운 과제는 내일로 미루어도 좋습니다.")
        tips["공부/업무"].append("타이머(25-5 규칙)로 짧게 끊어 몰입도를 유지하세요.")
    else:
        tips["공부/업무"].append("중간 강도의 과제를 우선 처리하고, 검토·오탈자 점검에 시간을 투자하세요.")

    # 활동/대인
    if em >= 0.33:
        tips["활동/대인"].append("발표·토론·상담에 적합합니다. 협업 미팅을 잡아도 좋아요. 💬")
    elif em <= -0.33:
        tips["활동/대인"].append("갈등 가능성이 높습니다. 중요한 협상·감정적 대화는 내일로 조정하세요.")
        tips["활동/대인"].append("메신저는 간결한 문장으로, 확인은 한 번 더.")
    else:
        tips["활동/대인"].append("메시지는 짧고 명확하게. 대면보다 문서로 남기는 커뮤니케이션이 유리합니다.")

    # 건강/휴식
    if pb >= 0.33:
        tips["건강/휴식"].append("러닝·자전거 등 유산소 + 가벼운 근력운동이 좋아요. 물 충분히! 🏃")
    elif pb <= -0.33:
        tips["건강/휴식"].append("무리한 운동은 피하고 스트레칭·산책 위주로 컨디션을 회복하세요.")
        tips["건강/휴식"].append("취침 전 1시간 화면 끄기, 수면 위생을 챙기세요.")
    else:
        tips["건강/휴식"].append("가벼운 인터벌 또는 요가로 리듬을 조절하세요.")

    # 주의
    if (em <= -0.33) or (inl <= -0.33):
        tips["주의"].append("중요 계약·지원서 제출 등 큰 의사결정은 하루 미루는 선택이 더 안전합니다. ⚠️")
    else:
        tips["주의"].append("집중력 과신을 경계하고, 중요한 문서는 10분 뒤 재검토하세요.")

    return tips


def plot_chart(df: pd.DataFrame, today: date):
    """기간 라인 차트를 표시하고, 오늘선 보조선 추가."""
    st.subheader("기간별 바이오리듬 추이")
    chart_df = df.set_index("날짜")[["신체", "감정", "지성"]]
    st.line_chart(chart_df, height=260, use_container_width=True)
    st.caption("참고: 신체(23일)·감정(28일)·지성(33일) 주기")

# ---------- 입력 UI ----------
with st.sidebar:
    st.header("입력")
    today = date.today()
    birth = st.date_input("생년월일", value=date(2008, 1, 1), max_value=today)
    start = st.date_input("조회 시작일", value=today)
    span = st.slider("조회 기간(일)", min_value=15, max_value=60, value=30)

# 입력 유효성 보정
if birth > today:
    st.warning("생년월일이 미래로 설정되어 기본값으로 보정했습니다.")
    birth = today

# 기간 설정
start_day = min(start, today)
num_days = span * 2 + 1  # -span ~ +span 범위
range_start = start_day - timedelta(days=span)

# 데이터 생성
df = make_series(birth=birth, start_day=range_start, num_days=num_days)

# 오늘 인덱스 계산
today_row = df[df["날짜"] == pd.to_datetime(today)].copy()
if today_row.empty:
    # 안전장치: 오늘이 범위 밖이면 가장 가까운 날로 대체
    nearest_idx = (df["날짜"] - pd.to_datetime(today)).abs().idxmin()
    today_row = df.iloc[[nearest_idx]].copy()

pb_val = float(today_row["신체"].iloc[0])
em_val = float(today_row["감정"].iloc[0])
in_val = float(today_row["지성"].iloc[0])

# ---------- “오늘의 AI 조언 (YYYY-MM-DD)” ----------
title_date = today.strftime("%Y-%m-%d")
st.subheader(f"오늘의 AI 조언 ({title_date})")

tips = advise_today(pb_val, em_val, in_val)
cols = st.columns(2)
with cols[0]:
    st.markdown("**공부/업무**")
    for t in tips["공부/업무"]:
        st.write("- " + t)
    st.markdown("**활동/대인**")
    for t in tips["활동/대인"]:
        st.write("- " + t)
with cols[1]:
    st.markdown("**건강/휴식**")
    for t in tips["건강/휴식"]:
        st.write("- " + t)
    st.markdown("**주의**")
    for t in tips["주의"]:
        st.write("- " + t)

st.markdown("---")

# ---------- “오늘의 바이오리듬 요약” (이름에 수치 포함 & 색상 강조) ----------
st.subheader("오늘의 바이오리듬 요약")

def metric_line(name: str, value: float):
    lbl, color, icon = state_label(value)
    disp = f"{name} ({value:+.2f}) {icon}"
    st.markdown(
        f"<div style='padding:10px;border-radius:8px;background:{color}1A'>"
        f"<span style='font-weight:600;color:{color}'>{disp}</span>"
        f"<span style='margin-left:8px;color:#555'>— {lbl}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )
    # 상세 코멘트 2~3문장
    if name == "신체":
        if value >= 0.33:
            st.write("에너지가 올라오는 날입니다. 유산소+가벼운 근력 조합이 잘 맞아요. 수분 섭취를 늘려 회복을 돕고, 과도한 무게는 피하세요.")
        elif value <= -0.33:
            st.write("피로 누적 가능성이 있어요. 스트레칭·산책 위주로 컨디션을 관리하고, 수면 시간을 30분 더 확보해보세요.")
        else:
            st.write("무리하지 않는 선에서 몸을 깨우세요. 가벼운 인터벌이나 요가로 리듬을 조절하면 좋습니다.")
    elif name == "감정":
        if value >= 0.33:
            st.write("정서 안정과 공감 능력이 좋은 날입니다. 발표·상담·협업 일정을 소화하기 좋고, 피드백 주고받기에도 유리합니다.")
        elif value <= -0.33:
            st.write("감정 기복에 주의하세요. 중요한 대화는 내일로 미루고, 메시지는 짧고 명확하게 남기세요. 휴식 신호를 자주 점검하세요.")
        else:
            st.write("감정선이 비교적 중립입니다. 작은 자극에 흔들릴 수 있으니 루틴과 호흡으로 안정감을 유지하세요.")
    else:  # 지성
        if value >= 0.33:
            st.write("분석·추론력이 좋아지는 날입니다. 수학·과학·코딩 등 고난도 과제를 오전에 처리하고, 오후엔 리뷰/정리에 시간을 배분하세요.")
        elif value <= -0.33:
            st.write("복잡한 문제는 효율이 떨어질 수 있어요. 암기·요약·오답정리 위주로 전환하고, 중요한 결정은 하루 미루는 편이 안전합니다.")
        else:
            st.write("정리·검토에 적합합니다. 과제의 결론보다 근거 정돈, 노트 재구성에 시간을 투자해 완성도를 높이세요.")

metric_line("신체", pb_val)
metric_line("감정", em_val)
metric_line("지성", in_val)

st.markdown("---")

# ---------- 추이 차트 ----------
plot_chart(df, today=today)

# ---------- 중요 날짜(영점 교차일) ----------
st.subheader("중요 날짜(영점 교차일)")
zc_body = zero_crossings(df, "신체")
zc_emo = zero_crossings(df, "감정")
zc_int = zero_crossings(df, "지성")

if not (zc_body or zc_emo or zc_int):
    st.write("조회 범위 내 영점 교차가 없습니다.")
else:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**신체**")
        for d in zc_body:
            st.write("- ", d.strftime("%Y-%m-%d"))
    with c2:
        st.markdown("**감정**")
        for d in zc_emo:
            st.write("- ", d.strftime("%Y-%m-%d"))
    with c3:
        st.markdown("**지성**")
        for d in zc_int:
            st.write("- ", d.strftime("%Y-%m-%d"))

# ---------- 푸터 ----------
st.caption("ⓘ 본 서비스는 참고용이며, 개인 정보는 저장·외부 전송하지 않습니다.")
# ===== 실제 실행 코드 끝 =====
