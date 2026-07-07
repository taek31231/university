import streamlit as st
import pandas as pd
import numpy as np
import os

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

@st.cache_data
def load_university_database():
    csv_file = "univ_data.csv"
    if not os.path.exists(csv_file):
        df_built = 체계적_대학데이터_생성()
        df_built.to_csv(csv_file, index=False, encoding="utf-8-sig")
        return df_built
    else:
        try:
            return pd.read_csv(csv_file, encoding="utf-8-sig")
        except Exception as e:
            df_built = 체계적_대학데이터_생성()
            df_built.to_csv(csv_file, index=False, encoding="utf-8-sig")
            return df_built

# --- 2. 메인 타이틀 ---
st.title("🎓 2028 개편 내신 종합 분석 계산기")
st.markdown("### 2022 개정 교육과정 최적화 및 수시 배치 라인")
st.write("---")

# --- 3. 세션 상태 초기화 ---
if 'subjects_data' not in st.session_state:
    st.session_state.subjects_data = [
        {"category": "수학", "name": "대수", "type": "일반(공통)", "rank": 5, "total": 200, "achievement": "A", "hours": 4},
        {"category": "수학", "name": "기하", "type": "진로선택", "rank": 1, "total": 200, "achievement": "A", "hours": 3},
        {"category": "국어", "name": "독서와 작문", "type": "일반(공통)", "rank": 14, "total": 200, "achievement": "A", "hours": 4},
        {"category": "과학", "name": "물리학Ⅱ", "type": "진로선택", "rank": 1, "total": 200, "achievement": "B", "hours": 3}
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

# --- 5. 오른쪽: 계산 대시보드 및 결과 리포트 ---
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
        
        st.markdown("#### 🔍 실시간 수시 배치 라인 (학생 구간별 동적 마진형)")
        track = st.radio("본인의 계열을 선택하세요:", ["이과(자연계열)", "문과(인문계열)"], horizontal=True)
        
        db_df = load_university_database()
        filtered_df = db_df[db_df["track"] == track]
        categories = {"상향": [], "소신": [], "안정": [], "하향": []}
        
        # 💡 [핵심 알고리즘 수정] 학생 등급 구간별 동적 마진 함수 정의
        # 내 성적에 맞는 유의미한 상하 한계선을 설정하여 우주상향/지하하향 필터링
        if avg_g9 <= 1.5:
            # 1등급대 초중반 극상위권 설정
            up_bound, target_up, target_down, down_bound = -0.2, -0.1, 0.0, 0.1
        elif 1.5 < avg_g9 <= 3.0:
            # 1등급 후반 ~ 2등급대 설정
            up_bound, target_up, target_down, down_bound = -0.4, -0.2, 0.0, 0.2
        else:
            # 3등급대 이하 중위권 설정 (터무니없는 의대/서울대 상향 노출 원천 차단)
            up_bound, target_up, target_down, down_bound = -0.6, -0.3, 0.0, 0.3

        for _, row in filtered_df.iterrows():
            diff = row["cut"] - avg_g9 # 대학 컷 - 내 등급 (음수면 대학 컷이 더 높음 = 상향/소신)
            
            item = {"univ": row["univ"], "dept": row["dept"], "cut": row["cut"], "desc": row["desc"]}
            
            # 구간별 마진 대입
            if up_bound <= diff < target_up:
                categories["상향"].append(item)
            elif target_up <= diff < target_down:
                categories["소신"].append(item)
            elif target_down <= diff <= down_bound:
                categories["안정"].append(item)
            elif down_bound < diff <= (down_bound + (0.3 if avg_g9 <= 3.0 else 0.4)):
                # 하향도 무한정 낮은 대학이 나오지 않도록 적정 캡(Cap)을 씌움
                categories["하향"].append(item)
        
        # 탭 배치 안내
        tab1, tab2, tab3, tab4 = st.tabs(["🔴 도전 상향", "🟡 지원 소신", "🟢 적정 안정", "🔵 보험 하향"])
        
        def display_dynamic_tab(target_tab, key_string):
            with target_tab:
                if not categories[key_string]:
                    st.info("현재 내신 점수 대에 매칭되는 유의미한 대학·학과군이 이 탭에는 없습니다.")
                else:
                    st.caption(f"💡 지원 타깃 범위 내 총 {len(categories[key_string])}개 데이터가 정제되었습니다.")
                    for item in categories[key_string]:
                        st.markdown(f"**🏛️ {item['univ']}**")
                        st.markdown(f"📌 **학과군:** `{item['dept']} [평균 {item['cut']:.2f}등급]`")
                        st.write("")

        display_dynamic_tab(tab1, "상향")
        display_dynamic_tab(tab2, "소신")
        display_dynamic_tab(tab3, "안정")
        display_dynamic_tab(tab4, "하향")
        
        st.write("---")
        
        # 단일 과목별 성적 정밀 분석 테이블
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
