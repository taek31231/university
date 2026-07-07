import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="대학 입학처 표준 내신 환산 시뮬레이터",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 대입 입학처 공식 연산 알고리즘 탑재 시뮬레이터")
st.markdown("### 일반선택(석차등급)과 진로선택(성취도별 분포비율) 및 대학별 이수 과목 제한 규칙을 적용합니다.")
st.write("---")

# 1. 초기 샘플 데이터 정의 (일반과목과 진로선택과목 분리 구조)
if 'regular_subjects' not in st.session_state:
    st.session_state.regular_subjects = [
        {"category": "수학", "name": "대수", "grade": 1, "hours": 4},
        {"category": "국어", "name": "독서와 작문", "grade": 2, "hours": 4},
        {"category": "영어", "name": "영어 회화", "grade": 2, "hours": 4},
        {"category": "과학", "name": "물리학Ⅰ", "grade": 3, "hours": 3},
    ]

if 'career_subjects' not in st.session_state:
    st.session_state.career_subjects = [
        {"category": "수학", "name": "기하", "achievement": "A", "a_ratio": 35.0, "b_ratio": 45.0, "c_ratio": 20.0, "hours": 3},
        {"category": "과학", "name": "물리학Ⅱ", "achievement": "A", "a_ratio": 25.0, "b_ratio": 50.0, "c_ratio": 25.0, "hours": 3}
    ]

col_input, col_output = st.columns([5, 4])

# --- 왼쪽 입력 파트 ---
with col_input:
    st.subheader("📝 1. 일반 / 공통 선택 과목 (석차등급 산출)")
    if st.button("➕ 일반과목 추가"):
        st.session_state.regular_subjects.append({"category": "수학", "name": "새 일반과목", "grade": 3, "hours": 3})
        st.rerun()

    updated_reg = []
    for idx, sub in enumerate(st.session_state.regular_subjects):
        with st.container():
            rc1, rc2, rc3, rc4, rc5 = st.columns([2, 3, 2, 2, 1])
            with rc1:
                cat = rc1.selectbox("교과", ["국어", "수학", "영어", "사회", "과학", "기타"], index=["국어", "수학", "영어", "사회", "과학", "기타"].index(sub['category']), key=f"reg_cat_{idx}")
            with rc2:
                name = rc2.text_input("과목명", value=sub['name'], key=f"reg_name_{idx}")
            with rc3:
                grade = rc3.number_input("등급", min_value=1, max_value=9, value=sub['grade'], key=f"reg_grd_{idx}")
            with rc4:
                hours = rc4.number_input("시수", min_value=1, max_value=10, value=sub['hours'], key=f"reg_hrs_{idx}")
            with rc5:
                if rc5.button("🗑️", key=f"reg_del_{idx}"):
                    st.session_state.regular_subjects.pop(idx)
                    st.rerun()
            updated_reg.append({"category": cat, "name": name, "grade": grade, "hours": hours})
    st.session_state.regular_subjects = updated_reg

    st.write("---")
    st.subheader("📐 2. 진로 선택 과목 (성취도 및 비율)")
    if st.button("➕ 진로과목 추가"):
        st.session_state.career_subjects.append({"category": "수학", "name": "새 진로과목", "achievement": "A", "a_ratio": 30.0, "b_ratio": 50.0, "c_ratio": 20.0, "hours": 3})
        st.rerun()

    updated_car = []
    for idx, sub in enumerate(st.session_state.career_subjects):
        with st.container():
            cc1, cc2, cc3, cc4, cc5, cc6 = st.columns([2, 2, 1.5, 3, 1.5, 1])
            with cc1:
                cat = cc1.selectbox("교과", ["국어", "수학", "영어", "사회", "과학", "기타"], index=["국어", "수학", "영어", "사회", "과학", "기타"].index(sub['category']), key=f"car_cat_{idx}")
            with cc2:
                name = cc2.text_input("과목명", value=sub['name'], key=f"car_name_{idx}")
            with cc3:
                ach = cc3.selectbox("성취도", ["A", "B", "C"], index=["A", "B", "C"].index(sub['achievement']), key=f"car_ach_{idx}")
            with cc4:
                st.write("분포 비율(%)")
                ca = st.number_input("A", min_value=0.0, max_value=100.0, value=sub['a_ratio'], step=0.1, key=f"car_a_{idx}")
                cb = st.number_input("B", min_value=0.0, max_value=100.0, value=sub['b_ratio'], step=0.1, key=f"car_b_{idx}")
                cc = 100.0 - ca - cb
                st.caption(f"C비율자동계산: {cc:.1f}%")
            with cc5:
                hours = cc5.number_input("시수", min_value=1, max_value=10, value=sub['hours'], key=f"car_hrs_{idx}")
            with cc6:
                if cc6.button("🗑️", key=f"car_del_{idx}"):
                    st.session_state.career_subjects.pop(idx)
                    st.rerun()
            updated_car.append({"category": cat, "name": name, "achievement": ach, "a_ratio": ca, "b_ratio": cb, "c_ratio": cc, "hours": hours})
    st.session_state.career_subjects = updated_car


# --- 오른쪽 계산 파트 ---
with col_output:
    st.subheader("📊 대학 입학처 연산 엔진 결과")
    
    reg_df = pd.DataFrame(st.session_state.regular_subjects)
    car_df = pd.DataFrame(st.session_state.career_subjects)
    
    if reg_df.empty:
        st.warning("먼저 일반 과목을 한 개 이상 등록해 주세요.")
    else:
        # --- [규칙 1: 고려대학교식 변환석차등급 알고리즘] ---
        # A인 경우: 1 + (A비율/100)
        # B인 경우: 5 + (A비율 + B비율)/100
        # C인 경우: 9 (또는 내부식 매핑)
        def get_korea_univ_grade(row):
            if row['achievement'] == 'A':
                return 1.0 + (row['a_ratio'] / 100.0)
            elif row['achievement'] == 'B':
                return 5.0 + ((row['a_ratio'] + row['b_ratio']) / 100.0)
            else:
                return 9.0

        if not car_df.empty:
            car_df['ku_converted_grade'] = car_df.apply(get_korea_univ_grade, axis=1)
        
        # 1. 고려대학교 산출 계산 (소수점 아래 5자리 계산 규칙 반영)
        ku_total_weighted_grade = (reg_df['grade'] * reg_df['hours']).sum()
        ku_total_hours = reg_df['hours'].sum()
        
        if not car_df.empty:
            ku_total_weighted_grade += (car_df['ku_converted_grade'] * car_df['hours']).sum()
            ku_total_hours += car_df['hours'].sum()
            
        ku_final_grade = ku_total_weighted_grade / ku_total_hours
        # 소수점 5자리 이하 절사/반올림 처리 (입학처 표준 소수점 5자리 고정)
        ku_final_grade_fixed = np.round(ku_final_grade, 5)
        
        # 2. 동국대학교식 산출 계산 (상위 10과목 제한 예외 규칙)
        # 일반 선택과목 중 석차등급이 가장 좋은 상위 10과목만 추려서 평균 냄
        sorted_reg = reg_df.sort_values(by="grade", ascending=True)
        top_10_reg = sorted_reg.head(10)
        dg_final_grade = (top_10_reg['grade'] * top_10_reg['hours']).sum() / top_10_reg['hours'].sum()
        dg_final_grade_fixed = np.round(dg_final_grade, 5)

        # 3. 서강대학교 성취도 기반 비율 환산점수 계산 방식
        # 진로선택과목 A등급에 100점 만점 부여 후, 비율에 따라 정밀 감점 계산
        def get_sogang_career_score(row):
            if row['achievement'] == 'A':
                return 100.0 - (row['a_ratio'] * 0.1) # 학교 부풀리기 방지 역산 감점
            elif row['achievement'] == 'B':
                return 80.0 - (row['b_ratio'] * 0.1)
            else:
                return 50.0

        if not car_df.empty:
            car_df['sogang_score'] = car_df.apply(get_sogang_career_score, axis=1)
            sg_career_avg = (car_df['sogang_score'] * car_df['hours']).sum() / car_df['hours'].sum()
        else:
            sg_career_avg = 100.0
            
        # 대시보드 출력
        st.info("💡 **고려대학교 교과 산출 (성취도별 분포비율 반영)**")
        st.metric(label="고려대식 변환 최종 내신 등급", value=f"{ku_final_grade_fixed:.5f} 등급")
        st.caption("※ 진로선택과목의 성취도와 해당 학교의 등급별 취득 학생 비율을 역산하여 내신 등급 부풀리기를 방지하는 공식이 작동했습니다.")
        
        st.write("---")
        st.info("💡 **동국대학교형 산출 (이수 과목 제한 규칙 반영)**")
        st.metric(label="동국대식 상위 과목 반영 평균 내신", value=f"{dg_final_grade_fixed:.5f} 등급")
        st.caption(f"※ 전체 {len(reg_df)}개 제출 과목 중 가장 성적이 좋은 상위 10개(이하) 과목만 정제 추출하여 계산한 결과입니다.")
        
        if not car_df.empty:
            st.write("---")
            st.markdown("#### 🔍 진로선택과목 대학별 변환 매핑 테이블 데이터")
            st.dataframe(car_df[['name', 'achievement', 'ku_converted_grade', 'hours']], hide_index=True)
