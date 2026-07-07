import streamlit as st
import pandas as pd
import numpy as np

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
st.markdown("### 2022 개정 교육과정 최적화 및 수시 배치 라인")
st.write("---")

# --- 3. 세션 상태 초기화 (샘플 데이터 포함) ---
if 'subjects_data' not in st.session_state:
    st.session_state.subjects_data = [
        {"category": "수학", "name": "대수", "type": "일반(공통)", "rank": 5, "total": 200, "achievement": "A", "hours": 4},
        {"category": "수학", "name": "기하", "type": "진로선택", "rank": 1, "total": 200, "achievement": "A", "hours": 3},
        {"category": "국어", "name": "독서와 작문", "type": "일반(공통)", "rank": 14, "total": 200, "achievement": "A", "hours": 4},
        {"category": "과학", "name": "물리학Ⅱ", "type": "진로선택", "rank": 1, "total": 200, "achievement": "B", "hours": 3}
    ]

# 화면 레이아웃 분할
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
        
        st.markdown("#### 🔍 실시간 수시 배치 라인 (9등급제 마진 연동)")
        track = st.radio("본인의 계열을 선택하세요:", ["이과(자연계열)", "문과(인문계열)"], horizontal=True)
        
        # 2025학년도 9등급제 기반 대학별 평균 입결 컷 데이터베이스
        raw_univ_data = [
            {"univ": "서울대학교 (종합)", "track": "이과(자연계열)", "dept": "사범대 과학교육계열 / 간호학과", "cut": 1.25, "desc": "일반고 기준 극상위권 라인. 면접 및 최저학력기준 변수 존재."},
            {"univ": "연세대학교 (종합)", "track": "이과(자연계열)", "dept": "천문우주학과 / 대기과학과", "cut": 1.30, "desc": "활동우수형 전형. 서류 및 제시문 면접 역량이 핵심."},
            {"univ": "고려대학교 (종합)", "track": "이과(자연계열)", "dept": "수학과 / 물리학과 / 바이오의공학", "cut": 1.35, "desc": "학업우수형 전형. 강력한 수능 최저(4합8) 학력 기준 요구."},
            {"univ": "성균관대학교 (종합)", "track": "이과(자연계열)", "dept": "자연과학계열 / 공학계열 (광역)", "cut": 1.45, "desc": "대규모 광역 선발로 인해 내신 컷의 유연성 확보 가능."},
            {"univ": "서강대학교 (교과)", "track": "이과(자연계열)", "dept": "컴퓨터공학과 / 전자공학과", "cut": 1.50, "desc": "교과전형이나 수능 최저 및 서류 정성 평가 동시 반영."},
            {"univ": "한양대학교 (교과)", "track": "이과(자연계열)", "dept": "융합전자공학부 / 신소재공학부", "cut": 1.55, "desc": "수능 최저학력기준 신설로 입결 유동성이 커진 구간."},
            {"univ": "중앙대학교 (교과)", "track": "이과(자연계열)", "dept": "AI학과 / 기계공학부 / 화학신소재", "cut": 1.65, "desc": "높은 수능 최저(3합7) 기준으로 인해 실질 경쟁률 하락 효과."},
            {"univ": "경희대학교 (종합)", "track": "이과(자연계열)", "dept": "정보디스플레이학과 / 물리학과", "cut": 1.70, "desc": "네오르네상스 전형. 일반고 합격자가 가장 두터웁게 분포."},
            {"univ": "서울시립대학교 (교과)", "track": "이과(자연계열)", "dept": "전자전기컴퓨터공학부 / 화학공학", "cut": 1.75, "desc": "수능 최저(3합7) 만족 시 안정적인 추가 합격 라인."},
            {"univ": "건국대학교 (교과)", "track": "이과(자연계열)", "dept": "전기전자공학부 / 생명과학특성", "cut": 1.85, "desc": "수능 최저가 없으며, 내신 정량 점수의 영향력이 매우 큼."},
            {"univ": "동국대학교 (교과)", "track": "이과(자연계열)", "dept": "멀티미디어공학 / 융합에너지", "cut": 1.95, "desc": "상위 10과목만 추출 반영하므로 보정 내신 확인 필요."},
            {"univ": "홍익대학교 (교과)", "track": "이과(자연계열)", "dept": "신소재·화학공학부 / 건축학부", "cut": 2.05, "desc": "내신 대비 높은 수능 최저(3합8)가 가장 큰 변수."},

            {"univ": "서울대학교 (종합)", "track": "문과(인문계열)", "dept": "정치외교학부 / 경제학부 / 인문계열", "cut": 1.20, "desc": "일반고 문과 극최상위권 타깃. 수능 최저 및 심층 구술 면접 필요."},
            {"univ": "연세대학교 (종합)", "track": "문과(인문계열)", "dept": "경영학과 / 언론홍보영상학부", "cut": 1.28, "desc": "활동우수형 전형. 학업 역량과 깊이 있는 탐구 성과 입증 필요."},
            {"univ": "고려대학교 (종합)", "track": "문과(인문계열)", "dept": "자유전공학부 / 통계학과 / 미디어학부", "cut": 1.32, "desc": "학업우수형 인문 최저(4합8) 충족 시 실질 합격률 급상승."},
            {"univ": "성균관대학교 (종합)", "track": "문과(인문계열)", "dept": "사회과학계열 / 글로벌경영", "cut": 1.40, "desc": "계열모집 광역 선발의 특성을 활용한 안정적 지원 유효."},
            {"univ": "서강대학교 (교과)", "track": "문과(인문계열)", "dept": "경영학부 / 지식융합미디어학부", "cut": 1.45, "desc": "비교과 서류 반영 비율이 존재하여 문과 상위권 선호도 높음."},
            {"univ": "한양대학교 (교과)", "track": "문과(인문계열)", "dept": "정책학과 / 행정학과 / 미디어커뮤", "cut": 1.50, "desc": "한양대 특유의 수능 최저 기준 충족 여부가 최종 합격 판단 기준."},
            {"univ": "중앙대학교 (교과)", "track": "문과(인문계열)", "dept": "경영학부 / 공공인재학부 / 심리학과", "cut": 1.60, "desc": "인문계열 수능 최저(3합7)가 까다로워 내신 컷 방어에 유리."},
            {"univ": "경희대학교 (교과)", "track": "문과(인문계열)", "dept": "자율전공학부 / 회계세무 / 행정학과", "cut": 1.65, "desc": "교과 70% 정량평가 구조로 내신 경쟁력 확보가 최우선."},
            {"univ": "서울시립대학교 (교과)", "track": "문과(인문계열)", "dept": "세무학과 / 행정학과 / 국제관계학과", "cut": 1.70, "desc": "시립대 간판 인문 학과군을 노려볼 수 있는 적정 기준선."},
            {"univ": "건국대학교 (교과)", "track": "문과(인문계열)", "dept": "경영학과 / 미디어커뮤니케이션", "cut": 1.80, "desc": "수능 최저가 없으나, 정량 내신 점수로 1차적 안정성 확보 가능."},
            {"univ": "동국대학교 (교과)", "track": "문과(인문계열)", "dept": "법학과 / 경찰행정학부 / 국어국문", "cut": 1.90, "desc": "반영 과목 수 산출 특성을 이용한 문과 상위권의 확실한 보험."},
            {"univ": "홍익대학교 (교과)", "track": "문과(인문계열)", "dept": "경영학부 / 영어영문학과 / 법학부", "cut": 2.00, "desc": "높은 수능 최저(3합8) 학력 기준 덕분에 이변이 적은 안정 카드."}
        ]

        # 실시간 계열별 필터링
        filtered_univs = [u for u in raw_univ_data if u["track"] == track]
        categories = {"상향": [], "소신": [], "안정": [], "하향": []}
        
        # 💡 [진짜 등급마진 매핑 알고리즘]
        # 사용자 기준 등급 차이 공식 = (대학 합격 컷) - (내 실시간 내신)
        # 내 성적이 좋아질수록(숫자가 작아질수록) 대학 컷이 내 점수보다 낮아져 하향/안정 구간으로 이동합니다.
        for u in filtered_univs:
            diff = u["cut"] - avg_g9  
            
            if diff <= -0.4:
                categories["상향"].append(u)
            elif -0.4 < diff <= -0.2:
                categories["소신"].append(u)
            elif -0.2 < diff <= 0.2:
                categories["안정"].append(u)
            elif diff > 0.2:
                categories["하향"].append(u)
        
        # 탭 레이아웃 생성 및 마진 기준 명시
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔴 상향 (내 점수 +0.4 이상)", 
            "🟡 소신 (내 점수 +0.2 ~ +0.4)", 
            "🟢 안정 (내 점수 -0.2 ~ +0.2)", 
            "🔵 하향 (내 점수 -0.2 이하)"
        ])
        
        def display_dynamic_tab(target_tab, key_string):
            with target_tab:
                if not categories[key_string]:
                    st.info("현재 계산된 내신 점수 구간에 해당하는 대학이 없습니다. 왼쪽에서 성적을 조정해 보세요.")
                else:
                    for item in categories[key_string]:
                        st.markdown(f"**🏛️ {item['univ']}**")
                        st.markdown(f"📌 **추천 학과 및 입결 평균:** `{item['dept']} [평균 {item['cut']}등급]`")
                        st.write(f"📝 {item['desc']}")
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
