import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="2028 내신 종합 분석 및 38개대 실전 환산기",
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

UNIV_DATABASE = {
    "서울대": {"group": "수도권 상위대학", "points_9": {1:100, 2:98, 3:95, 4:90, 5:80, 6:70, 7:55, 8:40, 9:20}, "points_5": {1:100, 2:97, 3:92, 4:80, 5:50}},
    "연세대": {"group": "수도권 상위대학", "points_9": {1:100, 2:95, 3:87.5, 4:75, 5:60, 6:40, 7:25, 8:10, 9:0}, "points_5": {1:100, 2:95, 3:85, 4:70, 5:50}},
    "고려대": {"group": "수도권 상위대학", "points_9": {1:100, 2:98, 3:94, 4:86, 5:70, 6:50, 7:30, 8:10, 9:0}, "points_5": {1:100, 2:98, 3:93, 4:82, 5:60}},
    "서강대": {"group": "수도권 상위대학", "points_9": {1:100, 2:99, 3:97, 4:90, 5:80, 6:70, 7:50, 8:30, 9:0}, "points_5": {1:100, 2:99, 3:96, 4:85, 5:65}},
    "성균관대": {"group": "수도권 상위대학", "points_9": {1:100, 2:98, 3:95, 4:85, 5:70, 6:50, 7:30, 8:10, 9:0}, "points_5": {1:100, 2:98, 3:94, 4:80, 5:60}},
    "한양대": {"group": "수도권 상위대학", "points_9": {1:100, 2:97, 3:94, 4:88, 5:75, 6:55, 7:35, 8:15, 9:0}, "points_5": {1:100, 2:97, 3:93, 4:84, 5:55}},
    "이화여대": {"group": "수도권 상위대학", "points_9": {1:100, 2:98, 3:96, 4:90, 5:80, 6:60, 7:40, 8:20, 9:0}, "points_5": {1:100, 2:98, 3:95, 4:86, 5:60}},
    "중앙대": {"group": "수도권 상위대학", "points_9": {1:100, 2:98.5, 3:96.5, 4:92, 5:85, 6:70, 7:50, 8:30, 9:0}, "points_5": {1:100, 2:98.5, 3:95.5, 4:88, 5:65}},
    "경희대": {"group": "수도권 상위대학", "points_9": {1:100, 2:96, 3:89, 4:77, 5:60, 6:40, 7:23, 8:11, 9:0}, "points_5": {1:100, 2:98, 3:94, 4:82, 5:55}},
    "한국외대": {"group": "수도권 상위대학", "points_9": {1:100, 2:97.5, 3:94, 4:88, 5:80, 6:65, 7:45, 8:20, 9:0}, "points_5": {1:100, 2:97.5, 3:93, 4:85, 5:60}},
    "서울시립대": {"group": "수도권 상위대학", "points_9": {1:100, 2:98, 3:96, 4:92, 5:84, 6:70, 7:50, 8:30, 9:0}, "points_5": {1:100, 2:98, 3:95, 4:88, 5:65}},
    "건국대": {"group": "수도권 상위대학", "points_9": {1:100, 2:98.5, 3:96.5, 4:93, 5:85, 6:70, 7:40, 8:10, 9:0}, "points_5": {1:100, 2:98.5, 3:95, 4:87, 5:60}},

    "동국대": {"group": "수도권 주요대학", "points_9": {1:100, 2:99, 3:97, 4:94, 5:90, 6:80, 7:60, 8:40, 9:0}, "points_5": {1:100, 2:99, 3:96, 4:90, 5:70}},
    "홍익대": {"group": "수도권 주요대학", "points_9": {1:100, 2:97, 3:93, 4:87, 5:79, 6:69, 7:57, 8:40, 9:0}, "points_5": {1:100, 2:97, 3:92, 4:83, 5:60}},
    "숙명여대": {"group": "수도권 주요대학", "points_9": {1:100, 2:98, 3:95, 4:90, 5:82, 6:70, 7:50, 8:30, 9:0}, "points_5": {1:100, 2:98, 3:94, 4:85, 5:60}},
    "국민대": {"group": "수도권 주요대학", "points_9": {1:100, 2:98.5, 3:97, 4:94, 5:90, 6:83, 7:70, 8:50, 9:0}, "points_5": {1:100, 2:98.5, 3:96, 4:88, 5:65}},
    "숭실대": {"group": "수도권 주요대학", "points_9": {1:100, 2:97, 3:94, 4:89, 5:81, 6:70, 7:50, 8:30, 9:0}, "points_5": {1:100, 2:97, 3:92, 4:83, 5:60}},
    "세종대": {"group": "수도권 주요대학", "points_9": {1:100, 2:98, 3:95, 4:90, 5:82, 6:70, 7:50, 8:30, 9:0}, "points_5": {1:100, 2:98, 3:94, 4:85, 5:60}},
    "단국대": {"group": "수도권 주요대학", "points_9": {1:100, 2:98, 3:95, 4:90, 5:80, 6:65, 7:45, 8:20, 9:0}, "points_5": {1:100, 2:98, 3:93, 4:84, 5:55}},
    "아주대": {"group": "수도권 주요대학", "points_9": {1:100, 2:98, 3:95, 4:89, 5:79, 6:60, 7:40, 8:10, 9:0}, "points_5": {1:100, 2:98, 3:93, 4:83, 5:55}},
    "인하대": {"group": "수도권 주요대학", "points_9": {1:100, 2:97, 3:94, 4:88, 5:77, 6:55, 7:35, 8:10, 9:0}, "points_5": {1:100, 2:97, 3:92, 4:81, 5:50}},

    "충남대": {"group": "지방거점국립대", "points_9": {1:100, 2:98, 3:96, 4:93, 5:89, 6:82, 7:70, 8:50, 9:20}, "points_5": {1:100, 2:98, 3:95, 4:89, 5:70}},
    "충북대": {"group": "지방거점국립대", "points_9": {1:100, 2:98, 3:95, 4:91, 5:86, 6:78, 7:65, 8:45, 9:15}, "points_5": {1:100, 2:98, 3:94, 4:87, 5:65}},
    "강원대": {"group": "지방거점국립대", "points_9": {1:100, 2:98, 3:95, 4:91, 5:86, 6:78, 7:65, 8:45, 9:15}, "points_5": {1:100, 2:98, 3:94, 4:87, 5:65}},
    "경북대": {"group": "지방거점국립대", "points_9": {1:100, 2:98, 3:96, 4:93, 5:89, 6:82, 7:70, 8:50, 9:20}, "points_5": {1:100, 2:98, 3:95, 4:89, 5:70}},
    "부산대": {"group": "지방거점국립대", "points_9": {1:100, 2:98, 3:96, 4:93, 5:89, 6:82, 7:70, 8:50, 9:20}, "points_5": {1:100, 2:98, 3:95, 4:89, 5:70}},
    "전북대": {"group": "지방거점국립대", "points_9": {1:100, 2:98, 3:95, 4:91, 5:86, 6:78, 7:65, 8:45, 9:15}, "points_5": {1:100, 2:98, 3:94, 4:87, 5:65}},
    "전남대": {"group": "지방거점국립대", "points_9": {1:100, 2:98, 3:95, 4:91, 5:86, 6:78, 7:65, 8:45, 9:15}, "points_5": {1:100, 2:98, 3:94, 4:87, 5:65}},

    "한국교원대": {"group": "교대", "points_9": {1:100, 2:97, 3:93, 4:85, 5:75, 6:60, 7:40, 8:20, 9:0}, "points_5": {1:100, 2:96, 3:90, 4:78, 5:50}},
    "서울교대": {"group": "교대", "points_9": {1:100, 2:97, 3:93, 4:85, 5:75, 6:60, 7:40, 8:20, 9:0}, "points_5": {1:100, 2:96, 3:90, 4:78, 5:50}},
    "경인교대": {"group": "교대", "points_9": {1:100, 2:97, 3:93, 4:85, 5:75, 6:60, 7:40, 8:20, 9:0}, "points_5": {1:100, 2:96, 3:90, 4:78, 5:50}},
    "춘천교대": {"group": "교대", "points_9": {1:100, 2:96, 3:91, 4:83, 5:70, 6:55, 7:35, 8:15, 9:0}, "points_5": {1:100, 2:95, 3:88, 4:75, 5:45}},
    "청주교대": {"group": "교대", "points_9": {1:100, 2:96, 3:91, 4:83, 5:70, 6:55, 7:35, 8:15, 9:0}, "points_5": {1:100, 2:95, 3:88, 4:75, 5:45}},
    "공주교대": {"group": "교대", "points_9": {1:100, 2:96, 3:91, 4:83, 5:70, 6:55, 7:35, 8:15, 9:0}, "points_5": {1:100, 2:95, 3:88, 4:75, 5:45}},
    "전주교대": {"group": "교대", "points_9": {1:100, 2:96, 3:91, 4:83, 5:70, 6:55, 7:35, 8:15, 9:0}, "points_5": {1:100, 2:95, 3:88, 4:75, 5:45}},
    "광주교대": {"group": "교대", "points_9": {1:100, 2:96, 3:91, 4:83, 5:70, 6:55, 7:35, 8:15, 9:0}, "points_5": {1:100, 2:95, 3:88, 4:75, 5:45}},
    "대구교대": {"group": "교대", "points_9": {1:100, 2:96, 3:91, 4:83, 5:70, 6:55, 7:35, 8:15, 9:0}, "points_5": {1:100, 2:95, 3:88, 4:75, 5:45}},
    "부산교대": {"group": "교대", "points_9": {1:100, 2:96, 3:91, 4:83, 5:70, 6:55, 7:35, 8:15, 9:0}, "points_5": {1:100, 2:95, 3:88, 4:75, 5:45}}
}

st.title("🎓 2028 개편 내신 종합 분석 및 38개대 실전 환산기")
st.markdown("### 2022 개정 교육과정 최적화 버전 (불필요한 옛 산출식 제거)")
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
        
        st.write("---")
        st.markdown("#### 🏫 대학 그룹 선택 필터")
        selected_group = st.radio(
            "조회할 대학 그룹 라인을 선택해 주세요:",
            ["수도권 상위대학", "수도권 주요대학", "지방거점국립대", "교대"], horizontal=True
        )
        
        calculated_results = []
        for univ_name, info in UNIV_DATABASE.items():
            if info["group"] != selected_group: continue
            
            # 1. 동국대학교식 상위 10과목 제한 엔진
            if univ_name == "동국대":
                dg_target = df.sort_values(by="grade9").head(10)
                if not dg_target.empty:
                    score_9 = (dg_target['grade9'].map(info['points_9']) * dg_target['hours']).sum() / dg_target['hours'].sum()
                    score_5 = (dg_target['grade5'].map(info['points_5']) * dg_target['hours']).sum() / dg_target['hours'].sum()
                else: score_9, score_5 = 0, 0
            
            # 2. 경희대학교식 반영 엔진 (일반 80% + 진로상위3개 20%)
            elif univ_name == "경희대":
                khu_reg = df[df["type"] == "일반(공통)"]
                if khu_reg.empty: khu_reg = df
                
                reg_w9 = sum([info["points_9"].get(int(np.clip(np.round(row["grade9"]), 1, 9)), 0) * row["hours"] for _, row in khu_reg.iterrows()])
                reg_w5 = sum([info["points_5"].get(int(np.clip(np.round(row["grade5"]), 1, 5)), 0) * row["hours"] for _, row in khu_reg.iterrows()])
                reg_score_9 = reg_w9 / khu_reg["hours"].sum()
                reg_score_5 = reg_w5 / khu_reg["hours"].sum()
                
                career_only = df[df["type"] == "진로선택"].copy()
                if not career_only.empty:
                    score_map = {"A": 100.0, "B": 80.0, "C": 60.0}
                    career_only["khu_score"] = career_only["achievement"].map(score_map)
                    top_3_career = career_only.sort_values(by="khu_score", ascending=False).head(3)
                    career_score = top_3_career["khu_score"].mean()
                else:
                    career_score = 100.0
                
                score_9 = (reg_score_9 * 0.8) + (career_score * 0.2)
                score_5 = (reg_score_5 * 0.8) + (career_score * 0.2)
            
            # 3. 보편적인 대학별 전체 평균 연산 엔진
            else:
                total_w9, total_w5, hours_sum = 0, 0, 0
                for _, row in df.iterrows():
                    if selected_group != "교대" and row["category"] == "기타/예체능": continue
                    
                    h = row["hours"]
                    g9_idx = int(np.clip(np.round(row["grade9"]), 1, 9))
                    g5_idx = int(np.clip(np.round(row["grade5"]), 1, 5))
                    
                    total_w9 += info["points_9"].get(g9_idx, 0) * h
                    total_w5 += info["points_5"].get(g5_idx, 0) * h
                    hours_sum += h
                
                score_9 = total_w9 / hours_sum if hours_sum > 0 else 0
                score_5 = total_w5 / hours_sum if hours_sum > 0 else 0
                
            calculated_results.append({
                "대학교": univ_name,
                "9등급제 환산 점수": f"{np.round(score_9, 5):.5f} / 100.00",
                "5등급제 환산 점수": f"{np.round(score_5, 5):.5f} / 100.00"
            })
            
        st.subheader(f"🎯 {selected_group} 입학처 공식 기반 환산 테이블")
        st.table(pd.DataFrame(calculated_results))
