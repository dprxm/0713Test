import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="서울-양평 분석 앱", layout="wide")

st.title("🌡️ 도시 열섬현상 및 전력수요 분석")

@st.cache_data
def load_data():
    # 데이터를 읽고 컬럼명 공백 제거
    def clean_csv(file_path):
        df = pd.read_csv(file_path, encoding="cp949")
        df.columns = df.columns.str.strip()  # 컬럼명 앞뒤 공백 제거
        return df

    df_seoul = clean_csv("서울_기온.csv")
    df_yang = clean_csv("양평_기온.csv")
    df_power = clean_csv("전력수요.csv")

    # 일시 형식 통일
    for df in [df_seoul, df_yang, df_power]:
        df['일시'] = pd.to_datetime(df['일시'])
        
    return df_seoul, df_yang, df_power

try:
    df_s, df_y, df_p = load_data()

    tab1, tab2 = st.tabs(["🔥 열섬 분석", "⚡ 전력 연결"])

    # 탭1: 열섬 분석
    with tab1:
        st.header("서울 vs 양평 기온 비교")
        # 데이터 병합
        df_uhi = pd.merge(df_s[['일시', '기온(°C)']], df_y[['일시', '기온(°C)']], on='일시', suffixes=('_서울', '_양평'))
        df_uhi['기온차'] = df_uhi['기온(°C)_서울'] - df_uhi['기온(°C)_양평']
        
        st.subheader("① 1년간 두 지역 기온 변화")
        st.line_chart(df_uhi.set_index('일시')[['기온(°C)_서울', '기온(°C)_양평']])
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("② 시각별 기온차")
            df_uhi['시간'] = df_uhi['일시'].dt.hour
            st.bar_chart(df_uhi.groupby('시간')['기온차'].mean())
        with col2:
            st.subheader("③ 월별 기온차")
            df_uhi['월'] = df_uhi['일시'].dt.month
            st.bar_chart(df_uhi.groupby('월')['기온차'].mean())

    # 탭2: 전력 연결
    with tab2:
        st.header("서울 기온과 전력수요 관계")
        df_ep = pd.merge(df_s[['일시', '기온(°C)']], df_p[['일시', '전력수요(MWh)']], on='일시')
        
        st.subheader("① 기온 vs 전력수요 산점도")
        st.scatter_chart(df_ep, x='기온(°C)', y='전력수요(MWh)')
        
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("② 기온 구간별 평균 전력수요")
            df_ep['구간'] = (df_ep['기온(°C)'] // 5 * 5)
            st.bar_chart(df_ep.groupby('구간')['전력수요(MWh)'].mean())
        with col4:
            st.subheader("③ 월별 평균 전력수요")
            df_ep['월'] = df_ep['일시'].dt.month
            st.bar_chart(df_ep.groupby('월')['전력수요(MWh)'].mean())

except Exception as e:
    st.error(f"데이터 로드 또는 처리 중 오류 발생: {e}")
    st.write("파일 이름(공백 없는지), 경로, 컬럼명이 '일시', '기온(°C)', '전력수요(MWh)'가 맞는지 확인해 주세요.")
