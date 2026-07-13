import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="서울-양평 분석", layout="wide")

st.title("🌡️ 도시 열섬현상 및 전력수요 분석")

# 1. 데이터 로드 함수 (오류 방지 로직 포함)
@st.cache_data
def load_data():
    def read_csv_file(file_name):
        # cp949로 먼저 시도하고 안되면 utf-8 시도
        try:
            df = pd.read_csv(file_name, encoding="cp949")
        except:
            df = pd.read_csv(file_name, encoding="utf-8")
        
        # 컬럼 이름 앞뒤 공백 제거
        df.columns = df.columns.str.strip()
        return df

    df_seoul = read_csv_file("서울_기온.csv")
    df_yang = read_csv_file("양평_기온.csv")
    df_power = read_csv_file("전력수요.csv")

    # 일시 데이터 변환
    df_seoul['일시'] = pd.to_datetime(df_seoul['일시'])
    df_yang['일시'] = pd.to_datetime(df_yang['일시'])
    df_power['일시'] = pd.to_datetime(df_power['일시'])

    return df_seoul, df_yang, df_power

try:
    df_s, df_y, df_p = load_data()

    # 탭 생성
    tab1, tab2 = st.tabs(["🔥 열섬 분석", "⚡ 전력 연결"])

    # 탭 1: 열섬 분석
    with tab1:
        st.header("서울 vs 양평 기온 비교")
        df_uhi = pd.merge(df_s[['일시', '기온(°C)']], df_y[['일시', '기온(°C)']], on='일시', suffixes=('_서울', '_양평'))
        df_uhi['기온차'] = df_uhi['기온(°C)_서울'] - df_uhi['기온(°C)_양평']
        
        st.subheader("1. 1년간 두 지역 기온 변화")
        st.line_chart(df_uhi.set_index('일시')[['기온(°C)_서울', '기온(°C)_양평']])
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("2. 시각별 평균 기온차")
            df_uhi['hour'] = df_uhi['일시'].dt.hour
            st.bar_chart(df_uhi.groupby('hour')['기온차'].mean())
        with col2:
            st.subheader("3. 월별 평균 기온차")
            df_uhi['month'] = df_uhi['일시'].dt.month
            st.bar_chart(df_uhi.groupby('month')['기온차'].mean())

    # 탭 2: 전력 연결
    with tab2:
        st.header("기온과 전력수요 관계")
        df_ep = pd.merge(df_s[['일시', '기온(°C)']], df_p[['일시', '전력수요(MWh)']], on='일시')
        
        st.subheader("1. 기온 vs 전력수요 산점도")
        st.scatter_chart(df_ep, x='기온(°C)', y='전력수요(MWh)')
        
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("2. 기온 구간별 평균 전력수요")
            df_ep['temp_bin'] = (df_ep['기온(°C)'] // 5 * 5)
            st.bar_chart(df_ep.groupby('temp_bin')['전력수요(MWh)'].mean())
        with col4:
            st.subheader("3. 월별 평균 전력수요")
            df_ep['month'] = df_ep['일시'].dt.month
            st.bar_chart(df_ep.groupby('month')['전력수요(MWh)'].mean())

except Exception as e:
    st.error(f"오류 발생: {e}")
    st.write("파일이 같은 폴더에 있는지, 파일명(서울_기온.csv 등)이 정확한지 확인해 주세요.")
