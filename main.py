import streamlit as st
import pandas as pd
import plotly.express as px

# --- 0. 페이지 기본 설정 ---

st.set_page_config(
    page_title="2028 내신 종합 분석 계산기",
    page_icon="🎓",
    layout="wide"
)

# --- 1. 등급 산정 규칙 및 데이터베이스 정의 ---
GRADE_9_CUTS = [
    ("1등급", 4.0), ("2등급", 11.0), ("3등급", 23.0), ("4등급", 40.0),
    ("5등급", 60.0), ("6등급", 77.0), ("7등급", 89.0), ("8등급", 96.0), ("9등급", 100.0)
]
GRADE_5_RATIOS = [0.10, 0.34, 0.66, 0.90, 1.00]

def calculate_9grade(pct):
    if pct <= 0: return 1
    for grade_str, cut in GRADE_9_CUTS:
        if pct <= cut: return int(grade_str[0])
    return 9

def calculate_5grade_by_rules(rank, total_students):
    if total_students <= 0: return 5
    cut_ranks = [int(total_students * ratio + 0.5) for ratio in GRADE_5_RATIOS]
    for grade_idx, cut_rank in enumerate(cut_ranks):
        if rank <= cut_rank: return grade_idx + 1
    return 5

# --- 2. 메인 타이틀 ---

st.title("🎓 2028 개편 내신 종합 분석 계산기")
st.markdown("### 2022 개정 교육과정 및 수시 최적화")
st.write("---")


# --- 3. 세션 상태 초기화 ---
if 'subjects_data' not in st.session_state:
    st.session_state.subjects_data = [
        {"category": "국어", "name": "공통국어1", "type": "일반(공통)", "rank": 5, "total": 225, "achievement": "A", "hours": 4},
        {"category": "수학", "name": "공통수학1", "type": "일반(공통)", "rank": 1, "total": 225, "achievement": "A", "hours": 4},
        {"category": "영어", "name": "공통영어1", "type": "일반(공통)", "rank": 14, "total": 225, "achievement": "A", "hours": 4},
        {"category": "사회", "name": "통합사회1", "type": "일반(공통)", "rank": 1, "total": 225, "achievement": "A", "hours": 4},
        {"category": "사회", "name": "한국사1", "type": "일반(공통)", "rank": 1, "total": 225, "achievement": "A", "hours": 3},
        {"category": "과학", "name": "통합과학1", "type": "일반(공통)", "rank": 1, "total": 225, "achievement": "A", "hours": 4},
    ]

col_left, col_right = st.columns([5, 4])


# --- 4. 왼쪽: 성적 입력 창 ---
with col_left:
    st.markdown("### 📝 학생 성적 상세 기록 패널")
    c1, c2, _ = st.columns([1, 1.2, 3])
    with c1:
        if st.button("➕ 과목 추가"):
            st.session_state.subjects_data.append({
                "category": "수학", "name": "새 과목", "type": "일반(공통)", 
                "rank": 10, "total": 200, "achievement": "A", "hours": 3
            })
    with c2:
        if st.button("🗑️ 마지막 과목 삭제") and len(st.session_state.subjects_data) > 1:
            st.session_state.subjects_data.pop()
    updated_list = []
    for i, sub in enumerate(st.session_state.subjects_data):
        with st.container():
            st.markdown(f"##### **과목 #{i+1}**")
            cc1, cc2 = st.columns([2, 3])
            with cc1:
                cat = cc1.selectbox("교과", ["국어", "수학", "영어", "사회", "과학", "기타/예체능"], index=["국어", "수학", "영어", "사회", "과학", "기타/예체능"].index(sub['category']), key=f"cat_{i}")
                stype = cc1.selectbox("과목유형", ["일반(공통)", "진로선택"], index=["일반(공통)", "진로선택"].index(sub.get('type', '일반(공통)')), key=f"type_{i}")
            with cc2:
                name = cc2.text_input("과목명", value=sub['name'], key=f"name_{i}")
                hours = cc2.number_input("이수시수", min_value=1, max_value=10, value=sub['hours'], key=f"hours_{i}")
            cc3, cc4, cc5 = st.columns([3, 3, 3])
            with cc3: rank = cc3.number_input("석차(등)", min_value=1, value=sub.get('rank', 1), key=f"rank_{i}")
            with cc4: total = cc4.number_input("수강자(명)", min_value=1, value=sub.get('total', 200), key=f"total_{i}")
            with cc5: ach = cc5.selectbox("성취도", ["A", "B", "C"], index=["A", "B", "C"].index(sub.get('achievement', 'A')), key=f"ach_{i}")
            pct = (rank / total) * 100 if total > 0 else 100.0
            g9 = calculate_9grade(pct)
            g5 = calculate_5grade_by_rules(rank, total)
            updated_list.append({
                "category": cat, "name": name, "type": stype, 
                "rank": rank, "total": total, "achievement": ach, 
                "hours": hours, "pct": pct, "grade9": g9, "grade5": g5
            })
            st.write("---")

    st.session_state.subjects_data = updated_list

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
