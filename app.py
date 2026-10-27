import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config(page_title="공부 계획 생성기", page_icon="📚")
st.title("📚 시험 D-day 공부 계획 생성기")
st.write("과목, 시험일, 난이도를 입력하면 날짜별 공부 시간을 자동으로 계산해 줍니다.")

# 1. 과목 목록 저장소 (새로고침 전까지 유지)
if "subjects" not in st.session_state:
    st.session_state.subjects = []


# 2. 과목 추가 함수 (입력 검증 포함)
def add_subject(name, exam_date, difficulty):
    name = name.strip()
    if name == "":
        return False, "과목명을 입력하세요."
    if exam_date < date.today():
        return False, "이미 지난 날짜입니다."
    for s in st.session_state.subjects:
        if s["name"] == name:
            return False, "이미 추가된 과목입니다."
    st.session_state.subjects.append(
        {"name": name, "exam_date": exam_date, "difficulty": difficulty}
    )
    return True, f"'{name}' 과목을 추가했습니다."


# 3. 핵심 알고리즘: 날짜별 과목별 공부 시간 계산
def make_plan(subjects, daily_hours, start_day):
    rows = []
    last_day = max(s["exam_date"] for s in subjects)  # 마지막 시험일
    day = start_day
    while day <= last_day:
        # 그날 아직 시험이 안 끝난 과목만 선택
        active = [s for s in subjects if s["exam_date"] >= day]
        scores = {}
        for s in active:
            remain = max((s["exam_date"] - day).days, 1)  # 0일이면 1로 보정
            scores[s["name"]] = s["difficulty"] / remain   # 우선순위 점수
        total = sum(scores.values())
        for name, score in scores.items():
            hours = daily_hours * score / total            # 점수 비율대로 배분
            rows.append({"날짜": day, "과목": name, "공부시간": round(hours, 2)})
        day += timedelta(days=1)
    return pd.DataFrame(rows, columns=["날짜", "과목", "공부시간"])


# 4. 입력 화면
st.subheader("1. 과목 추가")
col1, col2, col3 = st.columns(3)
with col1:
    name = st.text_input("과목명")
with col2:
    exam_date = st.date_input("시험일", value=date.today() + timedelta(days=7))
with col3:
    difficulty = st.slider("난이도 (1~5)", 1, 5, 3)

if st.button("과목 추가"):
    ok, msg = add_subject(name, exam_date, difficulty)
    if ok:
        st.success(msg)
    else:
        st.warning(msg)

# 5. 현재 과목 목록 + 삭제/초기화
if st.session_state.subjects:
    st.subheader("2. 입력한 과목")
    df_sub = pd.DataFrame(st.session_state.subjects)
    df_sub.columns = ["과목", "시험일", "난이도"]
    st.table(df_sub)

    c1, c2 = st.columns(2)
    with c1:
        target = st.selectbox("삭제할 과목", [s["name"] for s in st.session_state.subjects])
        if st.button("선택 과목 삭제"):
            st.session_state.subjects = [
                s for s in st.session_state.subjects if s["name"] != target
            ]
            st.rerun()
    with c2:
        st.write("")
        st.write("")
        if st.button("전체 초기화"):
            st.session_state.subjects = []
            st.rerun()

# 6. 계획 생성
st.subheader("3. 계획 생성")
daily_hours = st.number_input("하루 공부 가능 시간 (시간)", value=3.0, step=0.5)

if st.button("계획 만들기"):
    try:
        if len(st.session_state.subjects) == 0:
            st.warning("과목을 먼저 추가하세요.")
        elif daily_hours <= 0:
            st.warning("공부 시간은 0보다 커야 합니다.")
        else:
            plan = make_plan(st.session_state.subjects, daily_hours, date.today())
            st.success("계획이 만들어졌습니다!")

            st.write("**날짜별 과목별 공부 시간**")
            st.dataframe(plan, use_container_width=True)

            st.write("**날짜별 공부 시간 차트**")
            pivot = plan.pivot_table(
                index="날짜", columns="과목", values="공부시간", aggfunc="sum"
            ).fillna(0)
            st.bar_chart(pivot)

            csv = plan.to_csv(index=False).encode("utf-8-sig")
            st.download_button("CSV로 다운로드", csv, "study_plan.csv", "text/csv")
    except Exception as e:
        st.error(f"예상치 못한 오류가 발생했습니다: {e}")
