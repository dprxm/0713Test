import streamlit as st
 
import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="서울-양평 기온 분석", layout="wide")

st.title("🌡️ 서울 vs 양평 도시 열섬현상 분석")
st.write("2025년 시간별 기온 데이터를 바탕으로 두 지역의 기온 차이를 비교합니다.")

# 1. 데이터 로드
@st.cache_data
def load_data():
    df_seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    df_yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    
    # 일시 컬럼을 datetime 형식으로 변환
    for df in [df_seoul, df_yangpyeong]:
        df['일시'] = pd.to_datetime(df['일시'])
    
    return df_seoul, df_yangpyeong

try:
    df_seoul, df_yangpyeong = load_data()
    
    # 데이터 병합 (일시 기준)
    df = pd.merge(df_seoul[['일시', '기온(°C)']], 
                  df_yangpyeong[['일시', '기온(°C)']], 
                  on='일시', suffixes=('_서울', '_양평'))
    
    # 기온 차이 컬럼 생성
    df['기온차'] = df['기온(°C)_서울'] - df['기온(°C)_양평']
    df['시간'] = df['일시'].dt.hour
    df['월'] = df['일시'].dt.month

    # 2. 그래프 시각화
    
    # ① 1년간 기온 변화
    st.subheader("1. 2025년 서울 및 양평 기온 추이")
    st.line_chart(df.set_index('일시')[['기온(°C)_서울', '기온(°C)_양평']])

    col1, col2 = st.columns(2)

    # ② 시각별 평균 기온차
    with col1:
        st.subheader("2. 시간(0-23시)별 평균 기온차")
        hourly_diff = df.groupby('시간')['기온차'].mean()
        st.bar_chart(hourly_diff)
        st.caption("서울 기온이 높을수록 양수(+) 값을 가집니다.")

    # ③ 월별 평균 기온차
    with col2:
        st.subheader("3. 월별 평균 기온차")
        monthly_diff = df.groupby('월')['기온차'].mean()
        st.bar_chart(monthly_diff)

except FileNotFoundError:
    st.error("파일을 찾을 수 없습니다. '서울_기온.csv'와 '양평_기온.csv' 파일이 같은 폴더에 있는지 확인해주세요.")
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
