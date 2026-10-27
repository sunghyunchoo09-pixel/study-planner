# 시험 D-day 공부 계획 생성기

시험일과 난이도를 입력하면 날짜별 과목별 공부 시간을 계산해 주는 Streamlit 앱입니다.

## 실행 방법
pip install -r requirements.txt
streamlit run app.py

## 알고리즘
우선순위 점수 = 난이도 / 시험까지 남은 일수 (0일이면 1로 보정)
과목 배정 시간 = 하루 공부 시간 x (과목 점수 / 점수 총합)
