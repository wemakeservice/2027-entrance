import streamlit as st
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="2027 대입 시행계획 실시간 대시보드", layout="wide")

# 데이터 불러오기
@st.cache_data
def load_data():
    if os.path.exists("university_data.csv"):
        return pd.read_csv("university_data.csv")
    else:
        return pd.DataFrame(columns=["대학명", "지역", "전형유형", "수능최저", "면접", "내신반영", "모집인원"])

df = load_data()

# 사이드바: 필터링 설정
st.sidebar.header("🔍 상세 필터")

# 지역 선택
all_regions = sorted(df["지역"].unique()) if not df.empty else []
selected_region = st.sidebar.multiselect("지역 선택", options=all_regions, default=all_regions[:5] if all_regions else [])

# 전형유형 선택
all_types = sorted(df["전형유형"].unique()) if not df.empty else []
selected_type = st.sidebar.multiselect("전형유형 선택", options=all_types, default=all_types)

# 수능최저 및 면접 필터
has_min_score = st.sidebar.radio("수능최저학력기준", ["전체", "있음", "없음"])
has_interview = st.sidebar.radio("면접 유무", ["전체", "있음", "없음"])

# 데이터 필터링 로직
if not df.empty:
    filtered_df = df.copy()
    if selected_region:
        filtered_df = filtered_df[filtered_df["지역"].isin(selected_region)]
    if selected_type:
        filtered_df = filtered_df[filtered_df["전형유형"].isin(selected_type)]
    if has_min_score != "전체":
        filtered_df = filtered_df[filtered_df["수능최저"] == has_min_score]
    if has_interview != "전체":
        filtered_df = filtered_df[filtered_df["면접"] == has_interview]
else:
    filtered_df = df

# 메인 화면 UI
st.title("🎓 2027학년도 전국 대학 입시 전형 비교")
st.markdown(f"현재 분석 완료된 **{len(df)}개** 대학의 데이터를 바탕으로 실시간 정보를 제공합니다.")

if df.empty:
    st.warning("데이터 파일(university_data.csv)을 찾을 수 없습니다. 데이터 추출을 먼저 진행해 주세요.")
else:
    # 지표 표시
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("검색된 대학 수", f"{len(filtered_df)}개")
    
    # 최저학력기준 적용 비율 계산
    if len(filtered_df) > 0:
        csat_ratio = int((len(filtered_df[filtered_df['수능최저'] == '있음']) / len(filtered_df) * 100))
        interview_ratio = int((len(filtered_df[filtered_df['면접'] == '있음']) / len(filtered_df) * 100))
    else:
        csat_ratio = 0
        interview_ratio = 0
        
    col2.metric("수능최저 적용 비율", f"{csat_ratio}%")
    col3.metric("면접 실시 비율", f"{interview_ratio}%")
    col4.metric("지역 수", f"{len(filtered_df['지역'].unique())}개")

    # 데이터 테이블 출력
    st.subheader("📊 대학별 상세 전형 조건")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    # 대학 비교 섹션
    st.divider()
    st.subheader("⚖️ 대학 간 1:1 조건 비교")
    selected_unis = st.multiselect("비교할 대학들을 선택하세요", options=sorted(df["대학명"].unique()))

    if selected_unis:
        compare_df = df[df["대학명"].isin(selected_unis)].drop_duplicates(subset=["대학명"]).set_index("대학명").T
        st.table(compare_df)
    else:
        st.info("비교하고 싶은 대학 이름을 선택하면 상세 표가 생성됩니다.")

st.sidebar.markdown("---")
st.sidebar.caption("본 데이터는 2027학년도 대입 시행계획 PDF를 AI로 자동 분석한 결과이며, 최종 확인은 반드시 각 대학 입학처 홈페이지를 통해 확인하시기 바랍니다.")
