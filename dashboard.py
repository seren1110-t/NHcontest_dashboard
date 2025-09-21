import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import openpyxl # .xlsx 파일을 읽기 위해 필요합니다. pip install openpyxl

# ======================================================================================
# 페이지 기본 설정
# ======================================================================================
st.set_page_config(
    page_title="NH 농업 리스크 진단서",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================================================
# 라이트/다크 모드 스타일 적용
# ======================================================================================
st.markdown("""
<style>
/* ... (CSS 스타일은 이전과 동일하게 유지) ... */
</style>
""", unsafe_allow_html=True)


# ======================================================================================
# 데이터 로딩
# ======================================================================================
@st.cache_data
def load_data(filepath, engine=None):
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith('.xlsx'):
            df = pd.read_excel(filepath, engine=engine)
        return df
    except FileNotFoundError:
        st.error(f"오류: '{filepath}' 파일을 찾을 수 없습니다. dashboard.py와 같은 폴더에 있는지 확인해주세요.")
        return None

# 기본 리스크 데이터와 소득회복지수 데이터를 각각 로드
df = load_data("농업_리스크관리유형_최종분석_보고서_v2.csv")
income_df = load_data("소득회복지수.xlsx", engine='openpyxl')


# ======================================================================================
# 대시보드 UI 구성
# ======================================================================================
st.title("📄 NH 농업 리스크 진단서")
st.markdown("귀하의 농장/기업이 가진 고유의 강점과 약점을 데이터로 분석하여, 지속가능한 성장을 위한 방향을 제시합니다.")

if df is None or income_df is None:
    st.stop()

# --------------------------------------------------------------------------------------
# 사이드바: 사용자 입력
# --------------------------------------------------------------------------------------
st.sidebar.header("🔍 진단 대상 정보 입력")
unique_regions = sorted(df['지역명'].unique())
selected_region = st.sidebar.selectbox("1. 지역을 선택하세요.", unique_regions)
available_items = sorted(df[df['지역명'] == selected_region]['품목명'].unique())
selected_item = st.sidebar.selectbox("2. 주력 품목을 선택하세요.", available_items)

# --------------------------------------------------------------------------------------
# 메인 화면: 분석 결과
# --------------------------------------------------------------------------------------
st.header(f"'{selected_region} - {selected_item}' 종합 진단 결과")
user_data = df[(df['지역명'] == selected_region) & (df['품목명'] == selected_item)]

if user_data.empty:
    st.warning("선택하신 조합에 대한 분석 데이터가 없습니다.")
else:
    user_row = user_data.iloc[0]
    included_seasons = ", ".join(user_data['기후계절_유형'].unique())
    
    st.info(f"**분석 기간**: 이 결과는 **{included_seasons}**을 포함한 1년 전체 데이터를 종합하여 도출된 **연간 종합 진단**입니다.")
    
    # --- 진단 요약 ---
    # ... (진단 요약 부분은 이전과 동일하게 유지) ...
    st.subheader("진단 요약: 귀하의 리스크 관리 유형")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**주요 리스크 환경**")
        st.markdown(f"### {user_row['대분류_유형']}")
    with col2:
        st.markdown("**추천 관리 전략**")
        st.markdown(f"### {user_row['리스크관리_유형']}")
    
    with st.expander("› 유형별 상세 설명 및 추천 전략 보기"):
        risk_type_description = {
            # ... (유형별 설명 내용은 이전과 동일하게 유지) ...
        }
        st.write(risk_type_description.get(user_row['리스크관리_유형'], "설명이 준비되지 않았습니다."))

    st.divider()

    # --- 세부 지표 분석 ---
    # ... (세부 지표 분석 부분은 이전과 동일하게 유지) ...
    st.subheader("세부 지표 분석: 우리 농장의 강점과 약점")
    
    col_climate, col_market = st.columns(2)
    with col_climate:
        st.markdown("#### 🌱 **기후 & 환경 대응력**")
        # ...
    with col_market:
        st.markdown("#### 📈 **시장 & 수익성 분석**")
        # ...

    with st.expander("💡 각 지표별 금융 연계 활용 전략 보기"):
        # ... (금융 연계 전략 설명은 이전과 동일하게 유지) ...
        st.markdown(""" ... """)

    st.divider()

    # --- [신규 기능 추가] 품목별 유통 및 소득 안정성 분석 ---
    st.subheader(f"참고: '{selected_item}' 품목의 일반적인 유통 및 소득 안정성")
    
    # 소득회복지수 데이터프레임에서 선택된 품목 정보 찾기
    item_income_data = income_df[income_df['품목'] == selected_item]
    
    if item_income_data.empty:
        st.warning(f"'{selected_item}' 품목에 대한 유통 및 소득 안정성 정보가 없습니다.")
    else:
        item_income_row = item_income_data.iloc[0]
        
        # 1. 농가 수취율 비교 (Bar Chart)
        st.markdown("##### **농가 수취율 비교**")
        st.caption("소비자 가격 중 농가에게 돌아오는 몫의 비율입니다. 직거래 수취율이 높을수록 유통 구조 개선의 잠재력이 큽니다.")
        
        income_chart_df = pd.DataFrame({
            '유통 방식': ['일반 유통', '직거래'],
            '농가 수취율(%)': [item_income_row['일반 수취율(%)'], item_income_row['직거래 수취율(%)']],
            '유통 비용률(%)': [item_income_row['일반 유통비용률(%)'], item_income_row['직거래 유통비용률(%)']]
        })
        
        fig_income = go.Figure()
        fig_income.add_trace(go.Bar(
            x=income_chart_df['유통 방식'],
            y=income_chart_df['농가 수취율(%)'],
            name='농가 수취율',
            marker_color='royalblue',
            text=income_chart_df['농가 수취율(%)'].apply(lambda x: f'{x}%'),
            textposition='auto'
        ))
        fig_income.add_trace(go.Bar(
            x=income_chart_df['유통 방식'],
            y=income_chart_df['유통 비용률(%)'],
            name='유통 비용',
            marker_color='lightgray',
            text=income_chart_df['유통 비용률(%)'].apply(lambda x: f'{x}%'),
            textposition='auto'
        ))
        fig_income.update_layout(barmode='stack', yaxis_title="비율(%)", height=300, 
                                 margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)",
                                 font_color="gray", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_income, use_container_width=True)

        # 2. 소득회복력 지수 (Metric)
        st.metric("소득회복력 지수", f"{item_income_row['소득회복력 지수(%)']:.2f} %",
                  help="가격이 폭락했을 때, 다음 해에 얼마나 빨리 소득을 회복하는지를 나타내는 지표입니다. 높을수록 소득 안정성이 높습니다.")
        
    st.divider()

    # --- 핵심 지표 시각화 ---
    st.subheader("핵심 지표 현황")
    # ... (게이지 차트 부분은 이전과 동일하게 유지) ...
    def create_gauge_chart(value, title, color):
        # ...
        return fig
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.plotly_chart(create_gauge_chart(user_row['기후회복력점수'], "기후 대응 능력", "green"), use_container_width=True)
    with g_col2:
        st.plotly_chart(create_gauge_chart(user_row['출하최적기지수'], "현재 판매 적합도", "blue"), use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.info("**향후 업데이트 예정**: AI 금융 컨설턴트가 진단 결과에 맞는 최적의 금융 상품(대출/보험)을 추천해 드립니다.")
