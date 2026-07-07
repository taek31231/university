import streamlit as st
import pandas as pd
import plotly.express as px

# --- 0. 페이지 기본 설정 ---
st.set_page_config(page_title="2028 정밀 입시 포트폴리오", layout="wide")

# --- 1. 등급 산정 규칙 ---
GRADE_9_CUTS = [("1등급", 4.0), ("2등급", 11.0), ("3등급", 23.0), ("4등급", 40.0),
                ("5등급", 60.0), ("6등급", 77.0), ("7등급", 89.0), ("8등급", 96.0), ("9등급", 100.0)]
GRADE_5_RATIOS = [0.10, 0.34, 0.66, 0.90, 1.00]

def calculate_9grade(pct):
    for grade_str, cut in GRADE_9_CUTS:
        if pct <= cut: return int(grade_str[0])
    return 9

def calculate_5grade(rank, total):
    pct = (rank / total) * 100
    for i, ratio in enumerate(GRADE_5_RATIOS):
        if pct <= (ratio * 100): return i + 1
    return 5

# --- 2. 세션 상태 초기화 ---
if 'subjects_data' not in st.session_state:
    st.session_state.subjects_data = []

st.title("🎓 2028 정밀 입시 포트폴리오")
st.markdown("성적 관리, 추이 시각화, 대학별 가중치 환산을 한 번에 해결합니다.")
st.write("---")

col_left, col_right = st.columns([1, 1])

# --- 3. 왼쪽: 성적 입력 창 ---
with col_left:
    st.markdown("### 📝 성적 입력")
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        semester = col1.selectbox("학기", ["1-1", "1-2", "2-1", "2-2", "3-1"])
        subject = col2.text_input("과목명")
        
        col3, col4, col5 = st.columns(3)
        cat = col3.selectbox("교과", ["국어", "수학", "영어", "과학", "사회"])
        rank = col4.number_input("석차", 1, 1000, 1)
        total = col5.number_input("수강자수", 1, 1000, 200)
        
        hours = st.number_input("단위수", 1, 10, 3)
        
        if st.form_submit_button("추가하기"):
            g9 = calculate_9grade((rank/total)*100)
            g5 = calculate_5grade(rank, total)
            st.session_state.subjects_data.append({
                "학기": semester, "과목": subject, "교과": cat, "단위수": hours,
                "석차": rank, "수강자": total, "9등급": g9, "5등급": g5, "점수": (rank/total)*100
            })

    if st.button("전체 데이터 삭제"):
        st.session_state.subjects_data = []
        st.rerun()

# --- 4. 오른쪽: 분석 및 시각화 ---
with col_right:
    if st.session_state.subjects_data:
        df = pd.DataFrame(st.session_state.subjects_data)
        
        st.markdown("### 📊 학기별 성적 추이 (시각화)")
        trend_df = df.groupby("학기")["점수"].mean().reset_index()
        fig = px.line(trend_df, x="학기", y="점수", markers=True, title="학기별 내신 백분위 변화 (낮을수록 우수)")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 🧮 대학별 가중치 환산")
        col_w1, col_w2, col_w3, col_w4 = st.columns(4)
        w_kor = col_w1.number_input("국어%", 0, 100, 25)
        w_mat = col_w2.number_input("수학%", 0, 100, 25)
        w_eng = col_w3.number_input("영어%", 0, 100, 25)
        w_sci = col_w4.number_input("과학%", 0, 100, 25)
        
        if (w_kor + w_mat + w_eng + w_sci) == 100:
            df['가중치'] = df['교과'].map({'국어': w_kor, '수학': w_mat, '영어': w_eng, '과학': w_sci})
            weighted_score = (df['점수'] * df['가중치'] / 100).sum() / (df['가중치'] / 100).sum()
            st.metric("가중치 적용 환산 백분위", f"{weighted_score:.2f} %")
        else:
            st.warning("가중치 합계가 100%가 되어야 계산됩니다.")
            
    else:
        st.info("성적을 입력하면 그래프와 환산 결과가 표시됩니다.")

# --- 5. 상세 데이터 테이블 ---
st.write("---")
st.markdown("### 📋 상세 성적 기록")
if st.session_state.subjects_data:
    st.dataframe(pd.DataFrame(st.session_state.subjects_data), use_container_width=True)
