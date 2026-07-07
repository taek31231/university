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

# 수도권/지거국/의대/교대 데이터셋 생성기
def 체계적_대학데이터_생성():
    data = []
    
    # 1. 의과대학
    medical_univs = ["서울대", "연세대", "고려대", "가톨릭대", "성균관대", "울산대", "한양대", "경희대", "중앙대", "부산대", "경북대", "전남대", "충남대"]
    for univ in medical_univs:
        data.append({"univ": f"{univ} (의예과/종합·교과)", "track": "이과(자연계열)", "dept": "의예과 / 치의예과", "cut": 1.05 if univ in ["서울대", "연세대", "가톨릭대"] else 1.15, "desc": "전국 최상위 고교 극초상위권 각축지. 수능 최저 완화 여부가 변수."})
        data.append({"univ": f"{univ} (약학과/종합·교과)", "track": "이과(자연계열)", "dept": "약학과 / 수의예과", "cut": 1.25 if univ in ["서울대", "연세대"] else 1.38, "desc": "상위권 자연계열 학생들의 견고한 투표 카드. 전문직 선호 현상 뚜렷."})

    # 2. 전국 주요 교육대학교
    edu_univs = ["서울교대", "경인교대", "공주교대", "대구교대", "부산교대", "광주교대", "춘천교대", "이화여대(초등)", "제주대(초등)"]
    for univ in edu_univs:
        cut_val = 1.45 if "서울" in univ or "경인" in univ or "이화" in univ else 1.75
        data.append({"univ": f"{univ} (교과/종합)", "track": "문과(인문계열)", "dept": "초등교육과", "cut": cut_val, "desc": "면접 비중이 높고 교직 인적성 평가가 당락의 핵심 변수로 작용."})
        data.append({"univ": f"{univ} (교과/종합)", "track": "이과(자연계열)", "dept": "초등교육과(자연선택)", "cut": cut_val + 0.05, "desc": "이과 가산점 매칭 여부 확인 필요. 교직 이념 정성평가 동시 반영."})

    # 3. 수도권 상위권 대학
    seoul_major = {
        "서울대학교": {"이과": [("컴퓨터공학·전기전자군", 1.20), ("화공·생명·기계공학군", 1.28), ("자연과학·지구환경군", 1.38)], "문과": [("경영·경제·정외학부군", 1.15), ("인문학·사회과학·어문학군", 1.35)]},
        "연세대학교": {"이과": [("화공생명·반도체공학부", 1.28), ("신소재·기계·IT융합군", 1.40), ("건축·천문·대기과학군", 1.52)], "문과": [("경영·경제·언론홍보학군", 1.32), ("행정·사회학·문헌정보군", 1.48)]},
        "고려대학교": {"이과": [("스마트보안·데이터과학", 1.32), ("전기전자·바이오의공학", 1.42), ("보건환경·간호·지구환경", 1.58)], "문과": [("자유전공학부·경영대학", 1.34), ("통계·미디어·행정학부", 1.45), ("역사·문학·철학어문군", 1.62)]},
        "서강대학교": {"이과": [("컴퓨터공학·전자공학군", 1.45), ("화학·생명과학·수학군", 1.65)], "문과": [("경영학부·경제학부", 1.42), ("인문학부·사회과학부", 1.55)]},
        "성균관대학교": {"이과": [("반도체·소프트웨어학", 1.35), ("공학계열·자연과학광역", 1.58), ("전자전기·건설환경", 1.68)], "문과": [("글로벌경영·글로벌경제", 1.38), ("사회과학계열·교육학", 1.55), ("인문과학계열·한문학", 1.68)]},
        "한양대학교": {"이과": [("융합전자·컴퓨터소프트", 1.35), ("기계공학·신소재공학", 1.52), ("자연과학·자원환경공", 1.70)], "문과": [("정책학과·행정학과", 1.42), ("경영학부·미디어커뮤", 1.48), ("국어국문·역사·철학", 1.65)]},
        "중앙대학교": {"이과": [("AI학과·융합공학부", 1.52), ("기계공학·화학공학군", 1.68), ("수학·물리·간호학과", 1.82)], "문과": [("경영학부·공공인재학", 1.50), ("심리학과·사회복지학", 1.62), ("문헌정보·역사어문군", 1.75)]},
        "경희대학교": {"이과": [("정보디스플레이학과", 1.58), ("전자공학·생명공학군", 1.75), ("응용물리·지리학과", 1.95)], "문과": [("자율전공학부·빅데이터", 1.55), ("회계세무·행정학과", 1.68), ("외국어문학·관광학군", 1.88)]},
        "서울시립대학교": {"이과": [("전자전기컴퓨터공학", 1.62), ("화학공학·기계정보공", 1.72), ("도시공학·환경공학부", 1.92)], "문과": [("세무학과·행정학과", 1.58), ("국제관계학·도시사회", 1.68), ("국어국문·국사학과군", 1.82)]},
        "건국대학교": {"이과": [("스마트운행체·줄기세포", 1.70), ("전기전자공학·화학공", 1.82), ("산림조경·생물공학군", 2.05)], "문과": [("경영학과·미디어커뮤", 1.68), ("정치외교·경제학과", 1.78), ("문화콘텐츠·철학어문", 1.92)]},
        "동국대학교": {"이과": [("AI소프트웨어융합학", 1.78), ("멀티미디어·전자공학", 1.88), ("바이오환경·통계학과", 2.15)], "문과": [("경찰행정학부·법학과", 1.65), ("경영학부·국제통상학", 1.78), ("국어국문창작·역사학", 1.95)]},
        "홍익대학교": {"이과": [("건축학부·도시공학과", 1.85), ("신소재화학공·정보컴", 1.98), ("기계시스템·기초과학", 2.20)], "문과": [("경영학부·경제학부", 1.82), ("법학부·영어영문학과", 1.92), ("국어국문·독어독문학", 2.10)]}
    }

    for univ, tracks in seoul_major.items():
        for dept_name, cut_v in tracks["이과"]:
            data.append({"univ": f"{univ} (교과/종합)", "track": "이과(자연계열)", "dept": dept_name, "cut": cut_v, "desc": f"{univ} 기술/과학 분야 핵심 학과군."})
        for dept_name, cut_v in tracks["문과"]:
            data.append({"univ": f"{univ} (교과/종합)", "track": "문과(인문계열)", "dept": dept_name, "cut": cut_v, "desc": f"{univ} 경영/인문 핵심 학과군."})

    # 4. 지방 거점 국립대학교
    jigeorug = ["부산대학교", "경북대학교", "충남대학교", "전남대학교", "충북대학교", "전북대학교", "강원대학교", "제주대학교"]
    for univ in jigeorug:
        base_cut = 1.95 if univ in ["부산대학교", "경북대학교"] else (2.25 if univ in ["충남대학교", "전남대학교"] else 2.65)
        
        data.append({"univ": f"{univ}", "track": "이과(자연계열)", "dept": "기계공학부 / 전기전자공학부 / 반도체", "cut": base_cut, "desc": "지방 거점 국립대 간판 공학부."})
        data.append({"univ": f"{univ}", "track": "이과(자연계열)", "dept": "화학공학과 / 컴퓨터공학 / 신소재", "cut": base_cut + 0.25, "desc": "적정 취업 연계 학과군."})
        data.append({"univ": f"{univ}", "track": "이과(자연계열)", "dept": "생명과학 / 수학 / 지구물리 / 간호", "cut": base_cut + 0.55, "desc": "자연과학 및 보건계열 하위 학과군."})
        
        data.append({"univ": f"{univ}", "track": "문과(인문계열)", "dept": "경영학부 / 경제학과 / 행정학과", "cut": base_cut + 0.10, "desc": "문과 최선호 전공군."})
        data.append({"univ": f"{univ}", "track": "문과(인문계열)", "dept": "정치외교 / 미디어커뮤니케이션 / 심리", "cut": base_cut + 0.35, "desc": "사회과학계열 중위 학과군."})
        data.append({"univ": f"{univ}", "track": "문과(인문계열)", "dept": "국어국문 / 사학과 / 철학 / 외국어문학", "cut": base_cut + 0.65, "desc": "인문학/어문학 학과군."})

    return pd.DataFrame(data)

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
