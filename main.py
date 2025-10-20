import streamlit as st
from datetime import date, datetime, timedelta
import math
import io
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="마음 예보", page_icon="🌤️", layout="centered")

# ==========================
# 유틸 함수
# ==========================
CYCLES = {
    "신체": 23,   # Physical
    "감정": 28,   # Emotional
    "지성": 33,   # Intellectual
}
EMOJI = {
    "신체": "💪",
    "감정": "💖",
    "지성": "🧠",
    "전체": "🌈",
}

@st.cache_data(show_spinner=False)
def days_between(b: date, t: date) -> int:
    return (t - b).days

def cycle_value(days: int, period: int) -> float:
    # 전통적 바이오리듬: sin(2π * days / period)
    return math.sin(2 * math.pi * (days / period))


def phase_and_tip(kind: str, val: float, is_critical: bool) -> tuple[str, str]:
    # 상태 라벨과 실천 팁 반환
    if is_critical:
        return (
            "⚠️ 크리티컬(전환기)",
            {
                "신체": "격한 운동은 피하고, 가벼운 스트레칭·수면 위주로 컨디션 관리",
                "감정": "중요 대화는 미루고, 감정 기록(저널링)·호흡 4-7-8 연습",
                "지성": "시험/발표 전이라면 체크리스트로 이중 점검, 실수 방지 루틴",
            }[kind],
        )

    if val >= 0.6:
        return (
            "⬆️ 상승·호조",
            {
                "신체": "인터벌/근력 같이 도전 강도 ↑, 수분·단백질 보충으로 회복 최적화",
                "감정": "친구와 협업·봉사·발표 등 대인 활동에 도전",
                "지성": "심화 문제·모의고사·프로젝트 설계처럼 고난도 과제 배치",
            }[kind],
        )
    if val >= 0.2:
        return (
            "🙂 안정",
            {
                "신체": "지속 가능한 루틴(30분 유산소+가벼운 코어) 유지",
                "감정": "감사 3가지 적기·산책 20분으로 정서 안정",
                "지성": "암기+이해 균형, 오답노트 정리·개념 간 연결 지도 만들기",
            }[kind],
        )
    if val > -0.2:
        return (
            "〰️ 중립",
            {
                "신체": "컨디션 탐색일: 가벼운 활동으로 몸 상태 점검",
                "감정": "미디어 사용 시간 줄이고, 수면 위생(블루라이트 차단) 챙기기",
                "지성": "집중 25분(포모도로)×3세트로 가볍게 스타트",
            }[kind],
        )
    if val > -0.6:
        return (
            "⬇️ 하강·주의",
            {
                "신체": "과부하 금지, 스트레칭·폼롤러로 회복",
                "감정": "셀프케어 우선: 음악·취미·가벼운 대화로 안정",
                "지성": "핵심 개념 복습·기출 회독, 실수 체크리스트 작성",
            }[kind],
        )
    return (
        "🔻 저조·관리 필요",
        {
            "신체": "휴식 1순위, 단 음료 대신 물·전자해질, 7–8시간 숙면",
            "감정": "감정 이름 붙이기(‘지금 나는 …’), 신뢰 인물과 짧은 대화",
            "지성": "쉬운 과제부터 처리, 중요한 의사결정은 연기·재검토",
        }[kind],
    )


def is_critical_day(prev_val: float, curr_val: float) -> bool:
    # 0 교차(부호 변화) 시 크리티컬로 봄
    return (prev_val <= 0 < curr_val) or (prev_val >= 0 > curr_val)


def mini_bar(val: float, width: int = 20) -> str:
    # -1~1 값을 좌우 막대로 표현
    clamped = max(-1.0, min(1.0, val))
    mid = width // 2
    if clamped >= 0:
        filled = int(round(clamped * mid))
        return "▁" * mid + "|" + "█" * filled + "·" * (mid - filled)
    else:
        filled = int(round(abs(clamped) * mid))
        return "·" * (mid - filled) + "█" * filled + "|" + "▁" * mid

# ==========================
# UI
# ==========================
st.title("마음 예보 🌤️")
st.caption("생년월일과 조회 날짜를 바탕으로 신체·감정·지성 리듬을 간단히 확인하고, 오늘의 실천 팁을 받아보세요.")

with st.sidebar:
    st.header("설정 ⚙️")
    today = date.today()
    bday = st.date_input("생년월일", value=date(2008, 1, 1), min_value=date(1950, 1, 1), max_value=today)
    target = st.date_input("조회 날짜", value=today, min_value=bday, max_value=date(2100, 12, 31))
    horizon = st.slider("예보 기간(일)", 7, 30, 14)
    st.markdown("""
    **해석 팁**
    - 값은 -1.00 ~ +1.00 범위이며, 0 부근은 **전환기(크리티컬)** 일 수 있어요.
    - 추천은 참고용입니다. 몸과 마음의 **실제 신호**를 더 신뢰하세요.
    """)

# 오늘 값 계산
D = days_between(bday, target)
rows = []
for kind, period in CYCLES.items():
    prev_val = cycle_value(D - 1, period)
    curr_val = cycle_value(D, period)
    crit = is_critical_day(prev_val, curr_val) or abs(curr_val) < 0.05
    label, tip = phase_and_tip(kind, curr_val, crit)
    rows.append({
        "항목": kind,
        "이모지": EMOJI[kind],
        "값": round(curr_val, 3),
        "상태": label,
        "바": mini_bar(curr_val),
        "오늘의 실천": tip,
    })

# 전체 컨디션(평균)
avg = sum(r["값"] for r in rows) / len(rows)
avg_label = (
    "맑음 ☀️" if avg >= 0.6 else
    "갬 ⛅" if avg >= 0.2 else
    "보통 🌥️" if avg > -0.2 else
    "주의 🌧️" if avg > -0.6 else
    "회복권장 ⛈️"
)

# --- Copy & Paste: 오늘의 조언 전체 문자열 구성 ---
advice_lines = [
    f"[마음 예보] {target.strftime('%Y-%m-%d')} · 전체 컨디션: {avg_label}",
    "— 오늘의 조언 —",
]
for r in rows:
    advice_lines.append(
        f"{EMOJI[r['항목']]} {r['항목']} (" 
        f"{r['상태']}, 값 {r['값']:+.3f}) : {r['오늘의 실천']}"
    )
advice_text = "
".join(advice_lines)

# 미리보기 + 복사 버튼
with st.container():
    cols = st.columns([1,1])
    with cols[0]:
        st.markdown("### 📋 오늘의 조언 복사")
        st.caption("버튼 클릭 시 아래 내용이 클립보드에 복사됩니다.")
    with cols[1]:
        components.html(
            f"""
            <div style='display:flex;justify-content:flex-end;align-items:center;height:100%'>
              <button id='copyBtn' style='padding:8px 14px;border-radius:10px;border:1px solid #ddd;cursor:pointer;'>📄 Copy</button>
            </div>
            <script>
              const txt = {json.dumps(advice_text)};
              const btn = document.getElementById('copyBtn');
              btn.onclick = async () => {{
                try {{
                  await navigator.clipboard.writeText(txt);
                  btn.textContent = '✅ Copied!';
                }} catch (e) {{
                  btn.textContent = '❌ Copy failed';
                }}
                setTimeout(() => btn.textContent = '📄 Copy', 1500);
              }};
            </script>
            """,
            height=46,
        )

with st.expander("복사될 내용 미리보기"):
    st.text_area("copy_preview", advice_text, height=140, label_visibility="collapsed")

st.subheader(f"{target.strftime('%Y-%m-%d')} · 전체 컨디션 {EMOJI['전체']} : {avg_label}")
for r in rows:
    with st.container(border=True):
        st.markdown(f"### {EMOJI[r['항목']]} {r['항목']} — {r['상태']}")
        st.write(f"**값:** {r['값']:+.3f}")
        st.markdown(f"`{r['바']}`")
        st.write(f"**오늘의 실천:** {r['오늘의 실천']}")

# 예보 표 & 크리티컬 데이
st.divider()
st.markdown("### 앞으로의 예보 📅")

forecast = []
critical_days = []
for i in range(horizon):
    dt = target + timedelta(days=i)
    dday = days_between(bday, dt)
    day_entry = {"날짜": dt.strftime("%Y-%m-%d")}
    is_any_critical = False
    for kind, period in CYCLES.items():
        prev_v = cycle_value(dday - 1, period)
        v = cycle_value(dday, period)
        day_entry[f"{kind}"] = round(v, 3)
        if is_critical_day(prev_v, v) or abs(v) < 0.01:
            is_any_critical = True
    forecast.append(day_entry)
    if is_any_critical:
        critical_days.append(day_entry["날짜"])

# 간단 표 출력(내장 렌더러 사용)
st.dataframe(forecast, use_container_width=True)

if critical_days:
    st.info("**크리티컬 가능일(전환기)**: " + ", ".join(critical_days[:10]) + (" …" if len(critical_days) > 10 else ""))

# 리포트 저장
st.divider()
export = {
    "title": "마음 예보",
    "birthdate": bday.isoformat(),
    "target_date": target.isoformat(),
    "today": rows,
    "overall": {"avg": round(avg, 3), "label": avg_label},
    "forecast_days": horizon,
    "forecast": forecast,
    "generated_at": datetime.now().isoformat(timespec="seconds"),
}

buf = io.BytesIO()
buf.write(json.dumps(export, ensure_ascii=False, indent=2).encode("utf-8"))
buf.seek(0)

st.download_button(
    label="💾 예보 리포트(JSON) 저장",
    data=buf,
    file_name=f"mind_forecast_{target.strftime('%Y%m%d')}.json",
    mime="application/json",
    help="현재 화면의 계산 결과를 JSON 파일로 저장합니다.",
)

st.caption("※ 본 도구는 참고용 자기점검 도구입니다. 건강·정서 문제는 보호자·전문가와 상의하세요. 🧑‍⚕️👩‍🏫")
