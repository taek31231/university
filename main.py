import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="2028 내신 종합 분석 계산기",
    page_icon="🎓",
    layout="wide"
)

# --- 1. 등급 산정 및 대학 데이터베이스 정의 ---
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

st.title("🎓 2028 개편 내신 종합 분석 계산기")
st.markdown("### 2022 개정 교육과정 최적화")
st.write("---")

if 'subjects_data' not in st.session_state:
    st.session_state.subjects_data = [
        {"category": "수학", "name": "대수", "type": "일반(공통)", "rank": 5, "total": 200, "achievement": "A", "hours": 4},
        {"category": "수학", "name": "기하", "type": "진로선택", "rank": 1, "total": 200, "achievement": "A", "hours": 3},
        {"category": "국어", "name": "독서와 작문", "type": "일반(공통)", "rank": 14, "total": 200, "achievement": "A", "hours": 4},
        {"category": "과학", "name": "물리학Ⅱ", "type": "진로선택", "rank": 1, "total": 200, "achievement": "B", "hours": 3}
    ]

col_left, col_right = st.columns([5, 4])

# --- 왼쪽: 성적 입력 창 ---
with col_left:
    st.markdown("### 📝 학생 성적 상세 기록 패널")
    c1, c2, _ = st.columns([1, 1.2, 3])
    with c1:
        if st.button("➕ 과목 추가"):
            st.session_state.subjects_data.append({"category": "수학", "name": "새 과목", "type": "일반(공통)", "rank": 10, "total": 200, "achievement": "A", "hours": 3})
            st.rerun()
    with c2:
        if st.button("🗑️ 마지막 과목 삭제") and len(st.session_state.subjects_data) > 1:
            st.session_state.subjects_data.pop()
            st.rerun()

    updated_list = []
    for i, sub in enumerate(st.session_state.subjects_data):
        sub_type = sub.get('type', '일반(공통)')
        sub_achievement = sub.get('achievement', 'A')
        sub_rank = sub.get('rank', 1)
        sub_total = sub.get('total', 200)

        with st.container():
            st.markdown(f"##### **과목 #{i+1}**")
            cc1, cc2 = st.columns([2, 3])
            with cc1:
                cat = cc1.selectbox("교과", ["국어", "수학", "영어", "사회", "과학", "기타/예체능"], index=["국어", "수학", "영어", "사회", "과학", "기타/예체능"].index(sub['category']), key=f"cat_{i}")
                stype = cc1.selectbox("과목유형", ["일반(공통)", "진로선택"], index=["일반(공통)", "진로선택"].index(sub_type), key=f"type_{i}")
            with cc2:
                name = cc2.text_input("과목명", value=sub['name'], key=f"name_{i}")
                hours = cc2.number_input("이수시수", min_value=1, max_value=10, value=sub['hours'], key=f"hours_{i}")
            
            # 💡 2015개정용 'A비율(%)' 입력을 완벽하게 제거하여 UI 최적화
            cc3, cc4, cc5 = st.columns([3, 3, 3])
            with cc3: rank = cc3.number_input("석차(등)", min_value=1, value=sub_rank, key=f"rank_{i}")
            with cc4: total = cc4.number_input("수강자(명)", min_value=1, value=sub_total, key=f"total_{i}")
            with cc5: ach = cc5.selectbox("성취도", ["A", "B", "C"], index=["A", "B", "C"].index(sub_achievement), key=f"ach_{i}")
            
            pct = (rank / total) * 100 if total > 0 else 100.0
            
            # --- 고정 등급 및 백분위 매핑 엔진 (2022 개정 표준 적용) ---
            if stype == "일반(공통)":
                g9 = calculate_9grade(pct)
                g5 = calculate_5grade_by_rules(rank, total)
            else:
                # 사용자가 석차를 기입했다면 석차 기반 계산, 아니라면 성취도별 고정 등급 매핑
                if rank > 1 or total != 200:
                    g9 = calculate_9grade(pct)
                    g5 = calculate_5grade_by_rules(rank, total)
                else:
                    if ach == "A": g5, g9 = 1.0, 1.0
                    elif ach == "B": g5, g9 = 3.0, 4.0
                    else: g5, g9 = 5.0, 9.0

            updated_list.append({"category": cat, "name": name, "type": stype, "rank": rank, "total": total, "achievement": ach, "hours": hours, "pct": pct, "grade9": g9, "grade5": g5})
            st.write("---")
            
    st.session_state.subjects_data = updated_list

# --- 오른쪽: 계산 대시보드 및 결과 리포트 ---
with col_right:
    st.markdown("### 📊 최종 대시보드 결과 리포트")
    df = pd.DataFrame(st.session_state.subjects_data)
    
    if not df.empty:
        reg_only = df[(df["type"] == "일반(공통)") | (df["rank"] > 1) | (df["total"] != 200)]
        if reg_only.empty: reg_only = df
            
        total_h = reg_only["hours"].sum()
        avg_g9 = (reg_only["grade9"] * reg_only["hours"]).sum() / total_h if total_h > 0 else 1.0
        avg_g5 = (reg_only["grade5"] * reg_only["hours"]).sum() / total_h if total_h > 0 else 1.0
        
        m_c1, m_c2 = st.columns(2)
        with m_c1: st.metric(label="📊 주요 석차산출 과목 9등급제 평균", value=f"{avg_g9:.2f} 등급")
        with m_c2: st.metric(label="✨ 주요 석차산출 과목 5등급제 평균", value=f"{avg_g5:.2f} 등급")
            
        st.write("---")
        
        st.markdown("#### 🎯 단일 과목별 성적 정밀 분석")
        analysis_df = pd.DataFrame({
            "과목명": df["name"],
            "유형": df["type"],
            "이수시수": df["hours"].astype(str) + "단위",
            "석차/수강자": df["rank"].astype(str) + " / " + df["total"].astype(str),
            "상위 백분위": df["pct"].map(lambda x: f"{x:.2f}%" if x > 0 else "-"),
            "9등급제 결과": df["grade9"].map(lambda x: f"{x}등급"),
            "5등급제 결과": df["grade5"].map(lambda x: f"{x}등급")
        })
        st.dataframe(analysis_df, use_container_width=True)
