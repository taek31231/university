import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="2028 내신 5등급제 주요대 환산기",
    page_icon="🎓",
    layout="wide"
)

# 1. 대학별 등급 환산 점수 데이터베이스 (2028 전형 계획 기준 시뮬레이션)
# 5등급제 도입으로 대다수 대학이 1~2등급 간 감점을 최소화하고 3등급부터 감점 폭을 키우는 추세 반영
UNIV_FORMULAS = {
    "연세대학교": {
        "group": "수도권 상위대학",
        "max_score": 100,
        "grade_points": {1: 100, 2: 95, 3: 87.5, 4: 75, 5: 60},
        "desc": "공통/일반선택과목 100점 만점 기준 구조 (과거 Z점수 폐기, 등급별 점수 반영)"
    },
    "고려대학교": {
        "group": "수도권 상위대학",
        "max_score": 100,
        "grade_points": {1: 100, 2: 98, 3: 94, 4: 86, 5: 70},
        "desc": "교과 평균 점수 산출 방식 (전 교과 균등 반영)"
    },
    "서강대학교": {
        "group": "수도권 상위대학",
        "max_score": 100,
        "grade_points": {1: 100, 2: 99, 3: 97, 4: 90, 5: 70},
        "desc": "국·수·영·사·과 전 과목 이수단위 가중평균 반영"
    },
    "성균관대학교": {
        "group": "수도권 상위대학",
        "max_score": 1000,
        "grade_points": {1: 1000, 2: 990, 3: 970, 4: 900, 5: 700},
        "desc": "정량평가 1000점 만점 기준 산출"
    },
    "한양대학교": {
        "group": "수도권 상위대학",
        "max_score": 100,
        "grade_points": {1: 100, 2: 98, 3: 96, 4: 85, 5: 60},
        "desc": "국·수·영·사·과 전 과목 반영 (학생부 종합평가 미포함 정량 전형 기준)"
    },
    "중앙대학교": {
        "group": "수도권 상위대학",
        "max_score": 100,
        "grade_points": {1: 100, 2: 98.5, 3: 96.5, 4: 88, 5: 70},
        "desc": "계열 구분 없이 국수영사과 이수단위 반영"
    },
    "경희대학교": {
        "group": "수도권 상위대학",
        "max_score": 500,
        "grade_points": {1: 500, 2: 490, 3: 475, 4: 430, 5: 300},
        "desc": "교과 성적 500점 만점 정량 산출 공식"
    },
    "아주대학교": {
        "group": "수도권 주요대학",
        "max_score": 100,
        "grade_points": {1: 100, 2: 98, 3: 95, 4: 88, 5: 70},
        "desc": "전 교과 이수단위 가중평균 반영"
    },
    "부산대학교": {
        "group": "지방거점국립대",
        "max_score": 100,
        "grade_points": {1: 100, 2: 98, 3: 96, 4: 92, 5: 80},
        "desc": "지거국 특성상 등급 간 격차가 상위권 사립대와 다름"
    },
    "경북대학교": {
        "group": "지방거점국립대",
        "max_score": 500,
        "grade_points": {1: 500, 2: 492, 3: 480, 4: 460, 5: 400},
        "desc": "교과 정량점수 500점 만점 기준"
    },
    "서울교대": {
        "group": "교대",
        "max_score": 100,
        "grade_points": {1: 100, 2: 98, 3: 95, 4: 85, 5: 50},
        "desc": "초등교육과 특성상 전 과목(예체능 포함)을 균등 가중치로 반영"
    }
}

# 5등급제 환산 기준 컷
GRADE_5_CUTS = [
    ("1등급", 10.0), ("2등급", 34.0), ("3등급", 66.0), ("4등급", 90.0), ("5등급", 100.0)
]

def get_5grade(pct):
    for grade_str, cut in GRADE_5_CUTS:
        if pct <= cut:
            return int(grade_str[0])
    return 5

st.title("🎓 5등급제 주요 대학별 내신 실전 환산 시뮬레이터")
st.markdown("### 과목 세부 분류(대수, 기하 등)를 지정하여 실제 대학별 환산 점수를 자동으로 계산합니다.")
st.write("---")

# 세션 상태로 과목 입력 데이터 관리
if 'subjects_data' not in st.session_state:
    st.session_state.subjects_data = [
        {"category": "수학", "name": "대수", "rank": 3, "total": 150, "hours": 4},
        {"category": "수학", "name": "기하", "rank": 12, "total": 150, "hours": 3},
        {"category": "국어", "name": "독서와 작문", "rank": 8, "total": 150, "hours": 4},
        {"category": "영어", "name": "영어 회화", "rank": 5, "total": 150, "hours": 4},
    ]

col_left, col_right = st.columns([5, 4])

with col_left:
    st.markdown("### 📝 과목별 석차 및 시수 입력")
    
    # 과목 관리 버튼
    c_btn1, c_btn2, _ = st.columns([1, 1, 3])
    with c_btn1:
        if st.button("➕ 과목 추가"):
            st.session_state.subjects_data.append({"category": "수학", "name": "새 과목", "rank": 10, "total": 100, "hours": 3})
            st.rerun()
    with c_btn2:
        if st.button("🗑️ 마지막 과목 삭제") and len(st.session_state.subjects_data) > 1:
            st.session_state.subjects_data.pop()
            st.rerun()

    # 입력 UI 리스트업
    updated_list = []
    for i, sub in enumerate(st.session_state.subjects_data):
        with st.container():
            cc1, cc2, cc3, cc4, cc5 = st.columns([2, 3, 2, 2, 2])
            with cc1:
                cat = cc1.selectbox("교과분류", ["국어", "수학", "영어", "사회", "과학", "기타/예체능"], 
                                    index=["국어", "수학", "영어", "사회", "과학", "기타/예체능"].index(sub['category']), key=f"cat_{i}")
            with cc2:
                name = cc2.text_input("세부과목명 (예: 대수/기하)", value=sub['name'], key=f"name_{i}")
            with cc3:
                rank = cc3.number_input("석차(등)", min_value=1, value=sub['rank'], key=f"rank_{i}")
            with cc4:
                total = cc4.number_input("수강자(명)", min_value=1, value=sub['total'], key=f"total_{i}")
            with cc5:
                hours = cc5.number_input("시수", min_value=1, value=sub['hours'], key=f"hours_{i}")
            
            # 계산 진행
            pct = (rank / total) * 100
            g5 = get_5grade(pct)
            
            updated_list.append({"category": cat, "name": name, "rank": rank, "total": total, "hours": hours, "pct": pct, "grade5": g5})
            st.write("---")
            
    st.session_state.subjects_data = updated_list

with col_right:
    st.markdown("### 📊 대학별 산출 점수 리포트")
    
    # 데이터프레임 시각화
    df = pd.DataFrame(st.session_state.subjects_data)
    
    if not df.empty:
        # 간단 요약 표
        summary_df = df[["category", "name", "hours", "pct", "grade5"]].copy()
        summary_df.columns = ["교과", "과목명", "시수", "백분율", "5등급제 결과"]
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        # 단순 평균 계산
        total_h = df["hours"].sum()
        df["weighted_g5"] = df["grade5"] * df["hours"]
        simple_avg = df["weighted_g5"].sum() / total_h if total_h > 0 else 5.0
        st.subheader(f"🏫 내신 평균 등급: {simple_avg:.2f} 등급")
        st.write("---")
        
        # 대학별 루프 돌며 실제 환산점수 매기기
        st.markdown("#### 🎯 주요 대학별 실제 전형 환산 점수")
        
        calculated_univs = []
        for univ_name, info in UNIV_FORMULAS.items():
            total_weighted_points = 0
            total_hours_count = 0
            
            for index, row in df.iterrows():
                # 대학별로 예체능/기타 과목을 제외할지 여부 결정 규칙
                if info["group"] != "교대" and row["category"] == "기타/예체능":
                    continue # 일반 대학은 국수영사과 위주 정량 산출하므로 패스
                    
                grade = row["grade5"]
                hours = row["hours"]
                
                # 등급에 대응하는 대학별 부여 점수 매핑
                pt = info["grade_points"].get(grade, info["grade_points"][5])
                
                total_weighted_points += pt * hours
                total_hours_count += hours
                
            if total_hours_count > 0:
                final_score = total_weighted_points / total_hours_count
                calculated_univs.append({
                    "대학교": univ_name,
                    "그룹": info["group"],
                    "내 점수": f"{final_score:.2f} 점",
                    "만점 기준": f"{info['max_score']} 점",
                    "전형 특징": info["desc"]
                })
                
        res_df = pd.DataFrame(calculated_univs)
        st.table(res_df)
        
    else:
        st.warning("오른쪽에 성적을 산출할 과목 정보가 없습니다.")
