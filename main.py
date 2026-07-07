import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="내신 성적 산출 및 주요대 환산기 (9등급/5등급 겸용)",
    page_icon="🎓",
    layout="wide"
)

# 1. 9등급제 기준 컷
GRADE_9_CUTS = [
    ("1등급", 4.0), ("2등급", 11.0), ("3등급", 23.0), ("4등급", 40.0),
    ("5등급", 60.0), ("6등급", 77.0), ("7등급", 89.0), ("8등급", 96.0), ("9등급", 100.0)
]

# 2. 5등급제 누적 비율 (반올림용)
GRADE_5_RATIOS = [0.10, 0.34, 0.66, 0.90, 1.00]

# 9등급제 계산 함수
def calculate_9grade(pct):
    if pct <= 0: return 1
    for grade_str, cut in GRADE_9_CUTS:
        if pct <= cut:
            return int(grade_str[0])
    return 9

# 5등급제 계산 함수 (반올림 규칙 적용)
def calculate_5grade_by_rules(rank, total_students):
    if total_students <= 0: return 5
    cut_ranks = [int(total_students * ratio + 0.5) for ratio in GRADE_5_RATIOS]
    for grade_idx, cut_rank in enumerate(cut_ranks):
        if rank <= cut_rank:
            return grade_idx + 1
    return 5

# 3. 38개 모든 주요 대학 등급별 환산 점수 데이터베이스 정의
# (기본 스케일: 1등급=100점 만점 기준 구조, 대학별 점수 격차 시뮬레이션)
UNIV_DATABASE = {
    # 수도권 상위대학
    "서울대": {"group": "수도권 상위대학", "grade_points_9": {1:100, 2:98, 3:95, 4:90, 5:80, 6:70, 7:55, 8:40, 9:20}, "grade_points_5": {1:100, 2:97, 3:92, 4:80, 5:50}},
    "연세대": {"group": "수도권 상위대학", "grade_points_9": {1:100, 2:95, 3:87.5, 4:75, 5:60, 6:40, 7:25, 8:10, 9:0}, "grade_points_5": {1:100, 2:95, 3:85, 4:70, 5:50}},
    "고려대": {"group": "수도권 상위대학", "grade_points_9": {1:100, 2:98, 3:94, 4:86, 5:70, 6:50, 7:30, 8:10, 9:0}, "grade_points_5": {1:100, 2:98, 3:93, 4:82, 5:60}},
    "서강대": {"group": "수도권 상위대학", "grade_points_9": {1:100, 2:99, 3:97, 4:90, 5:80, 6:70, 7:50, 8:30, 9:0}, "grade_points_5": {1:100, 2:99, 3:96, 4:85, 5:65}},
    "성균관대": {"group": "수도권 상위대학", "grade_points_9": {1:100, 2:98, 3:95, 4:85, 5:70, 6:50, 7:30, 8:10, 9:0}, "grade_points_5": {1:100, 2:98, 3:94, 4:80, 5:60}},
    "한양대": {"group": "수도권 상위대학", "grade_points_9": {1:100, 2:97, 3:94, 4:88, 5:75, 6:55, 7:35, 8:15, 9:0}, "grade_points_5": {1:100, 2:97, 3:93, 4:84, 5:55}},
    "이화여대": {"group": "수도권 상위대학", "grade_points_9": {1:100, 2:98, 3:96, 4:90, 5:80, 6:60, 7:40, 8:20, 9:0}, "grade_points_5": {1:100, 2:98, 3:95, 4:86, 5:60}},
    "중앙대": {"group": "수도권 상위대학", "grade_points_9": {1:100, 2:98.5, 3:96.5, 4:92, 5:85, 6:70, 7:50, 8:30, 9:0}, "grade_points_5": {1:100, 2:98.5, 3:95.5, 4:88, 5:65}},
    "경희대": {"group": "수도권 상위대학", "grade_points_9": {1:100, 2:98, 3:95, 4:88, 5:75, 6:50, 7:30, 8:10, 9:0}, "grade_points_5": {1:100, 2:98, 3:94, 4:82, 5:55}},
    "한국외대": {"group": "수도권 상위대학", "grade_points_9": {1:100, 2:97.5, 3:94, 4:88, 5:80, 6:65, 7:45, 8:20, 9:0}, "grade_points_5": {1:100, 2:97.5, 3:93, 4:85, 5:60}},
    "서울시립대": {"group": "수도권 상위대학", "grade_points_9": {1:100, 2:98, 3:96, 4:92, 5:84, 6:70, 7:50, 8:30, 9:0}, "grade_points_5": {1:100, 2:98, 3:95, 4:88, 5:65}},
    "건국대": {"group": "수도권 상위대학", "grade_points_9": {1:100, 2:98.5, 3:96.5, 4:93, 5:85, 6:70, 7:40, 8:10, 9:0}, "grade_points_5": {1:100, 2:98.5, 3:95, 4:87, 5:60}},

    # 수도권 주요대학
    "동국대": {"group": "수도권 주요대학", "grade_points_9": {1:100, 2:99, 3:97, 4:94, 5:90, 6:80, 7:60, 8:40, 9:0}, "grade_points_5": {1:100, 2:99, 3:96, 4:90, 5:70}},
    "홍익대": {"group": "수도권 주요대학", "grade_points_9": {1:100, 2:97, 3:93, 4:87, 5:79, 6:69, 7:57, 8:40, 9:0}, "grade_points_5": {1:100, 2:97, 3:92, 4:83, 5:60}},
    "숙명여대": {"group": "수도권 주요대학", "grade_points_9": {1:100, 2:98, 3:95, 4:90, 5:82, 6:70, 7:50, 8:30, 9:0}, "grade_points_5": {1:100, 2:98, 3:94, 4:85, 5:60}},
    "국민대": {"group": "수도권 주요대학", "grade_points_9": {1:100, 2:98.5, 3:97, 4:94, 5:90, 6:83, 7:70, 8:50, 9:0}, "grade_points_5": {1:100, 2:98.5, 3:96, 4:88, 5:65}},
    "숭실대": {"group": "수도권 주요대학", "grade_points_9": {1:100, 2:97, 3:94, 4:89, 5:81, 6:70, 7:50, 8:30, 9:0}, "grade_points_5": {1:100, 2:97, 3:92, 4:83, 5:60}},
    "세종대": {"group": "수도권 주요대학", "grade_points_9": {1:100, 2:98, 3:95, 4:90, 5:82, 6:70, 7:50, 8:30, 9:0}, "grade_points_5": {1:100, 2:98, 3:94, 4:85, 5:60}},
    "단국대": {"group": "수도권 주요대학", "grade_points_9": {1:100, 2:98, 3:95, 4:90, 5:80, 6:65, 7:45, 8:20, 9:0}, "grade_points_5": {1:100, 2:98, 3:93, 4:84, 5:55}},
    "아주대": {"group": "수도권 주요대학", "grade_points_9": {1:100, 2:98, 3:95, 4:89, 5:79, 6:60, 7:40, 8:10, 9:0}, "grade_points_5": {1:100, 2:98, 3:93, 4:83, 5:55}},
    "인하대": {"group": "수도권 주요대학", "grade_points_9": {1:100, 2:97, 3:94, 4:88, 5:77, 6:55, 7:35, 8:10, 9:0}, "grade_points_5": {1:100, 2:97, 3:92, 4:81, 5:50}},

    # 지방거점국립대
    "경북대": {"group": "지방거점국립대", "grade_points_9": {1:100, 2:98, 3:96, 4:93, 5:89, 6:82, 7:70, 8:50, 9:20}, "grade_points_5": {1:100, 2:98, 3:95, 4:89, 5:70}},
    "부산대": {"group": "지방거점국립대", "grade_points_9": {1:100, 2:98, 3:96, 4:93, 5:89, 6:82, 7:70, 8:50, 9:20}, "grade_points_5": {1:100, 2:98, 3:95, 4:89, 5:70}},
    "충남대": {"group": "지방거점국립대", "grade_points_9": {1:100, 2:98, 3:96, 4:93, 5:89, 6:82, 7:70, 8:50, 9:20}, "grade_points_5": {1:100, 2:98, 3:95, 4:89, 5:70}},
    "충북대": {"group": "지방거점국립대", "grade_points_9": {1:100, 2:98, 3:95, 4:91, 5:86, 6:78, 7:65, 8:45, 9:15}, "grade_points_5": {1:100, 2:98, 3:94, 4:87, 5:65}},
    "강원대": {"group": "지방거점국립대", "grade_points_9": {1:100, 2:98, 3:95, 4:91, 5:86, 6:78, 7:65, 8:45, 9:15}, "grade_points_5": {1:100, 2:98, 3:94, 4:87, 5:65}},
    "전북대": {"group": "지방거점국립대", "grade_points_9": {1:100, 2:98, 3:95, 4:91, 5:86, 6:78, 7:65, 8:45, 9:15}, "grade_points_5": {1:100, 2:98, 3:94, 4:87, 5:65}},
    "전남대": {"group": "지방거점국립대", "grade_points_9": {1:100, 2:98, 3:95, 4:91, 5:86, 6:78, 7:65, 8:45, 9:15}, "grade_points_5": {1:100, 2:98, 3:94, 4:87, 5:65}},

    # 교대
    "한국교원대": {"group": "교대", "grade_points_9": {1:100, 2:97, 3:93, 4:85, 5:75, 6:60, 7:40, 8:20, 9:0}, "grade_points_5": {1:100, 2:96, 3:90, 4:78, 5:50}},
    "서울교대": {"group": "교대", "grade_points_9": {1:100, 2:97, 3:93, 4:85, 5:75, 6:60, 7:40, 8:20, 9:0}, "grade_points_5": {1:100, 2:96, 3:90, 4:78, 5:50}},
    "경인교대": {"group": "교대", "grade_points_9": {1:100, 2:97, 3:93, 4:85, 5:75, 6:60, 7:40, 8:20, 9:0}, "grade_points_5": {1:100, 2:96, 3:90, 4:78, 5:50}},
    "춘천교대": {"group": "교대", "grade_points_9": {1:100, 2:96, 3:91, 4:83, 5:70, 6:55, 7:35, 8:15, 9:0}, "grade_points_5": {1:100, 2:95, 3:88, 4:75, 5:45}},
    "청주교대": {"group": "교대", "grade_points_9": {1:100, 2:96, 3:91, 4:83, 5:70, 6:55, 7:35, 8:15, 9:0}, "grade_points_5": {1:100, 2:95, 3:88, 4:75, 5:45}},
    "공주교대": {"group": "교대", "grade_points_9": {1:100, 2:96, 3:91, 4:83, 5:70, 6:55, 7:35, 8:15, 9:0}, "grade_points_5": {1:100, 2:95, 3:88, 4:75, 5:45}},
    "전주교대": {"group": "교대", "grade_points_9": {1:100, 2:96, 3:91, 4:83, 5:70, 6:55, 7:35, 8:15, 9:0}, "grade_points_5": {1:100, 2:95, 3:88, 4:75, 5:45}},
    "광주교대": {"group": "교대", "grade_points_9": {1:100, 2:96, 3:91, 4:83, 5:70, 6:55, 7:35, 8:15, 9:0}, "grade_points_5": {1:100, 2:95, 3:88, 4:75, 5:45}},
    "대구교대": {"group": "교대", "grade_points_9": {1:100, 2:96, 3:91, 4:83, 5:70, 6:55, 7:35, 8:15, 9:0}, "grade_points_5": {1:100, 2:95, 3:88, 4:75, 5:45}},
    "부산교대": {"group": "교대", "grade_points_9": {1:100, 2:96, 3:91, 4:83, 5:70, 6:55, 7:35, 8:15, 9:0}, "grade_points_5": {1:100, 2:95, 3:88, 4:75, 5:45}}
}

st.title("🎓 내신 성적 산출 및 주요 대학별 환산 시뮬레이터")
st.markdown("### 9등급제 기준 수시 예측과 개편 5등급제 성적 분석을 동시에 수행합니다.")
st.write("---")

# 성적 입력을 세션 상태로 관리
if 'subjects_data' not in st.session_state:
    st.session_state.subjects_data = [
        {"category": "수학", "name": "대수", "rank": 5, "total": 200, "hours": 4},
        {"category": "수학", "name": "기하", "rank": 23, "total": 200, "hours": 3},
        {"category": "국어", "name": "독서와 작문", "rank": 9, "total": 200, "hours": 4},
        {"category": "영어", "name": "영어 회화", "rank": 15, "total": 200, "hours": 4},
    ]

col_left, col_right = st.columns([5, 4])

with col_left:
    st.markdown("### 📝 과목별 성적 기록 칸")
    
    c_btn1, c_btn2, _ = st.columns([1, 1.2, 3])
    with c_btn1:
        if st.button("➕ 과목 추가"):
            st.session_state.subjects_data.append({"category": "수학", "name": "새 과목", "rank": 10, "total": 200, "hours": 3})
            st.rerun()
    with c_btn2:
        if st.button("🗑️ 마지막 과목 삭제") and len(st.session_state.subjects_data) > 1:
            st.session_state.subjects_data.pop()
            st.rerun()

    updated_list = []
    for i, sub in enumerate(st.session_state.subjects_data):
        with st.container():
            cc1, cc2, cc3, cc4, cc5 = st.columns([2, 3, 2, 2, 2])
            with cc1:
                cat = cc1.selectbox("교과분류", ["국어", "수학", "영어", "사회", "과학", "기타/예체능"], 
                                    index=["국어", "수학", "영어", "사회", "과학", "기타/예체능"].index(sub['category']), key=f"cat_{i}")
            with cc2:
                name = cc2.text_input("세부과목명", value=sub['name'], key=f"name_{i}")
            with cc3:
                rank = cc3.number_input("석차(등)", min_value=1, value=sub['rank'], key=f"rank_{i}")
            with cc4:
                total = cc4.number_input("수강자(명)", min_value=1, value=sub['total'], key=f"total_{i}")
            with cc5:
                hours = cc5.number_input("시수", min_value=1, value=sub['hours'], key=f"hours_{i}")
            
            # 비율 및 이원화 등급 계산
            pct = (rank / total) * 100
            g9 = calculate_9grade(pct)
            g5 = calculate_5grade_by_rules(rank, total)
            
            updated_list.append({"category": cat, "name": name, "rank": rank, "total": total, "hours": hours, "pct": pct, "grade9": g9, "grade5": g5})
            st.write("---")
            
    st.session_state.subjects_data = updated_list

with col_right:
    st.markdown("### 📊 최종 결과 및 대학별 환산 리포트")
    df = pd.DataFrame(st.session_state.subjects_data)
    
    if not df.empty:
        # 성적 테이블 대시보드 출력
        view_df = df[["category", "name", "hours", "pct", "grade9", "grade5"]].copy()
        view_df.columns = ["교과", "과목명", "시수", "백분율", "9등급제 결과", "5등급제 결과"]
        st.dataframe(view_df, use_container_width=True, hide_index=True)
        
        # 1. 가중평균 평균 등급 산출 (이원화 표시)
        total_hours = df["hours"].sum()
        avg_g9 = (df["grade9"] * df["hours"]).sum() / total_hours if total_hours > 0 else 9.0
        avg_g5 = (df["grade5"] * df["hours"]).sum() / total_hours if total_hours > 0 else 5.0
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(label="📊 [현행 표준] 9등급제 평균", value=f"{avg_g9:.2f} 등급")
        with col_m2:
            st.metric(label="✨ [개편안] 5등급제 평균", value=f"{avg_g5:.2f} 등급")
            
        st.write("---")
        
        # 2. 대학 그룹 인터페이스 (클릭형 필터링 구현)
        st.markdown("#### 🏫 대학 그룹 필터")
        selected_group = st.radio(
            "조회할 대학 그룹을 선택하세요:",
            ["수도권 상위대학", "수도권 주요대학", "지방거점국립대", "교대"],
            horizontal=True
        )
        
        # 선택한 그룹의 대학교 점수 산출
        calculated_univs = []
        for univ_name, info in UNIV_DATABASE.items():
            if info["group"] != selected_group:
                continue
                
            total_w_p9 = 0
            total_w_p5 = 0
            total_hours_count = 0
            
            for _, row in df.iterrows():
                # 교대 그룹이 아니면 예체능 과목 정량 산출에서 제외 처리하는 범용 규칙 유지
                if selected_group != "교대" and row["category"] == "기타/예체능":
                    continue
                    
                hours = row["hours"]
                p9 = info["grade_points_9"].get(row["grade9"], 0)
                p5 = info["grade_points_5"].get(row["grade5"], 0)
                
                total_w_p9 += p9 * hours
                total_w_p5 += p5 * hours
                total_hours_count += hours
                
            if total_hours_count > 0:
                final_score_9 = total_w_p9 / total_hours_count
                final_score_5 = total_w_p5 / total_hours_count
                
                calculated_univs.append({
                    "대학교": univ_name,
                    "9등급제 환산 점수": f"{final_score_9:.2f} / 100.00",
                    "5등급제 환산 점수": f"{final_score_5:.2f} / 100.00"
                })
                
        res_df = pd.DataFrame(calculated_univs)
        st.subheader(f"🎯 {selected_group} 소속 대학 환산 점수표")
        st.table(res_df)
        
    else:
        st.warning("왼쪽 입력 칸에 한 개 이상의 과목 정보를 추가해 주세요.")
