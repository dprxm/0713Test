import streamlit as st
 
import streamlit as st
import pandas as pd

# 페이지 기본 설정
st.set_page_config(page_title="서울-양평 열섬 및 전력 분석", layout="wide")

st.title("🌡️ 도시 열섬현상 및 전력수요 상관관계 분석")
st.markdown("2025년 서울과 양평의 기온 데이터를 통해 도시화에 따른 기온 차이와 전력 소비 패턴을 분석합니다.")

# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_all_data():
    # 1. 서울/양평 기온 데이터 로드
    df_seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    df_yang = pd.read_csv("양평_기온.csv", encoding="cp949")
    # 2. 전력 수요 데이터 로드
    df_power = pd.read_csv("전력수요.csv", encoding="cp949")
    
    # 일시 컬럼 datetime 변환
    for df in [df_seoul, df_yang, df_power]:
        df['일시'] = pd.to_datetime(df['일시'])
        
    return df_seoul, df_yang, df_power

try:
    df_seoul, df_yang, df_power = load_all_data()

    # 탭 생성
    tab1, tab2 = st.tabs(["🔥 탭1: 열섬 분석", "⚡ 탭2: 전력 연결"])

    # --- 탭 1: 열섬 분석 ---
    with tab1:
        st.header("도시와 농촌의 기온 차이 분석 (서울 vs 양평)")
        
        # 데이터 병합 (서울 & 양평 기온)
        df_uhi = pd.merge(df_seoul[['일시', '기온(°C)']], 
                         df_yang[['일시', '기온(°C)']], 
                         on='일시', suffixes=('_서울', '_양평'))
        
        df_uhi['기온차'] = df_uhi['기온(°C)_서울'] - df_uhi['기온(°C)_양평']
        df_uhi['hour'] = df_uhi['일시'].dt.hour
        df_uhi['month'] = df_uhi['일시'].dt.month

        # ① 1년간 기온 변화 (선그래프)
        st.subheader("1. 연간 기온 변화 추이")
        st.line_chart(df_uhi.set_index('일시')[['기온(°C)_서울', '기온(°C)_양평']])

        col1, col2 = st.columns(2)
        # ② 시각별 평균 기온차 (막대그래프)
        with col1:
            st.subheader("2. 시각별 평균 기온차 (서울-양평)")
            hourly_diff = df_uhi.groupby('hour')['기온차'].mean()
            st.bar_chart(hourly_diff)
            st.caption("주로 야간에 도시 열섬현상이 뚜렷하게 나타납니다.")

        # ③ 월별 평균 기온차 (막대그래프)
        with col2:
            st.subheader("3. 월별 평균 기온차 (서울-양평)")
            monthly_diff = df_uhi.groupby('month')['기온차'].mean()
            st.bar_chart(monthly_diff)

    # --- 탭 2: 전력 연결 ---
    with tab2:
        st.header("기온 변화에 따른 전력 수요 변동 분석")
        
        # 데이터 병합 (서울 기온 & 전력수요)
        df_energy = pd.merge(df_seoul[['일시', '기온(°C)']], 
                            df_power[['일시', '전력수요(MWh)']], 
                            on='일시')
        
        df_energy['month'] = df_energy['일시'].dt.month
        # 기온 구간 생성 (5도 단위)
        df_energy['temp_bin'] = (df_energy['기온(°C)'] // 5 * 5).astype(int)

        # ① 기온과 전력수요의 산점도
        st.subheader("1. 기온 vs 전력수요 상관관계")
        st.scatter_chart(data=df_energy, x='기온(°C)', y='전력수요(MWh)')
        st.info("기온이 매우 낮거나 매우 높을 때 전력 수요가 급증하는 'U'자형 곡선을 보입니다.")

        col3, col4 = st.columns(2)
        # ② 기온 구간별 평균 전력수요
        with col3:
            st.subheader("2. 기온 구간별 평균 전력수요")
            temp_bin_power = df_energy.groupby('temp_bin')['전력수요(MWh)'].mean()
            st.bar_chart(temp_bin_power)

        # ③ 월별 평균 전력수요
        with col4:
            st.subheader("3. 월별 평균 전력수요")
            monthly_power = df_energy.groupby('month')['전력수요(MWh)'].mean()
            st.bar_chart(monthly_power)

except FileNotFoundError:
    st.error("데이터 파일을 찾을 수 없습니다. CSV 파일 3개가 같은 폴더에 있는지 확인해주세요.")
