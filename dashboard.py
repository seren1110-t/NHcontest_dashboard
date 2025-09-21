import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =_====================================================================================
# 페이지 기본 설정
# ======================================================================================
st.set_page_config(
    page_title="NH 농업 리스크 진단서",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================================================
# 라이트/다크 모드 자동 감지 및 스타일 적용
# ======================================================================================
st.markdown("""
<style>
/* Streamlit의 다크 모드 테마를 타겟으로 스타일을 재정의(override)합니다. */
[data-testid="stAppViewContainer"][class*="dark"] {
    background-color: #0E1117;
    color: #FAFAFA;
}
[data-testid="stAppViewContainer"][class*="dark"] h1,
[data-testid="stAppViewContainer"][class*="dark"] h2,
[data-testid="stAppViewContainer"][class*="dark"] h3 {
    color: #FFFFFF;
}
[data-testid="stAppViewContainer"][class*="dark"] [data-testid="stMetricLabel"] {
    color: #A0A0A0;
}
[data-testid="stAppViewContainer"][class*="dark"] [data-testid="stInfo"] {
    background-color: rgba(0, 104, 255, 0.15);
    border: 1px solid rgba(0, 104, 255, 0.5);
}
/* 라이트 모드일 때의 스타일은 Streamlit 기본값을 따르도록 남겨둡니다. */
</style>
""", unsafe_allow_html=True)


# ======================================================================================
# 데이터 로딩
# ======================================================================================
@st.cache_data
def load_data(filepath):
    try:
        df = pd.read_csv(filepath)
        return df
    except FileNotFoundError:
        st.error(f"오류: '{filepath}' 파일을 찾을 수 없습니다. dashboard.py와 같은 폴더에 있는지 확인해주세요.")
        return None

df = load_data("농업_리스크관리유형_최종분석_보고서_v2.csv")

# ======================================================================================
# 대시보드 UI 구성
# ======================================================================================
st.title("📄 NH 농업 리스크 진단서")
st.markdown("귀하의 농장/기업이 가진 고유의 강점과 약점을 데이터로 분석하여, 지속가능한 성장을 위한 방향을 제시합니다.")

if df is None:
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
    st.subheader("진단 요약: 귀하의 리스크 관리 유형")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**주요 리스크 환경**")
        st.markdown(f"### {user_row['대분류_유형']}")
    with col2:
        st.markdown("**추천 관리 전략**")
        st.markdown(f"### {user_row['리스크관리_유형']}")
    
    with st.expander("› 유형별 상세 설명 및 추천 전략 보기"):
        # [버그 수정] 누락된 '기후변화 고위험군', '특이 패턴형' 설명을 추가
        risk_type_description = {
            "기후변화 고위험군": "계절과 무관하게 급작스러운 기상 변화(한파, 폭염, 호우 등)에 사업이 크게 흔들릴 수 있는 고위험 그룹입니다. 기후 리스크에 대한 직접적인 대비(시설 개선, 재해 보험)가 최우선 과제입니다.",
            "다각화 안정 추구 타입": "여러 품목을 재배하여 특정 품목의 리스크를 분산시키는 안정적인 전략을 취하고 있습니다. 다만 개별 품목의 저항력(기후회복력)은 다소 낮을 수 있어, 전반적인 생산 기반을 강화하는 투자가 효과적입니다.",
            "고효율 집중 성장 타입": "기후 저항력이 강한 소수의 주력 품목에 집중하여 효율을 극대화하는 성장 전략을 사용하고 있습니다. 핵심 자산인 주력 품목을 보호하고, 규모의 경제를 실현하기 위한 투자가 필요합니다.",
            "시장 관망 타입 (출하 조절)": "생산물의 품질은 안정적이나 현재 시장 가격이 낮아 출하를 보류하며 현금 흐름에 어려움을 겪을 수 있는 유형입니다. 단기 운영자금을 확보하여 시장 상황이 유리해질 때까지 기다리는 전략이 유효합니다.",
            "수익 극대화 타입 (출하 적기)": "현재 시장 가격이 매우 유리하여 지금이 판매 최적기인 상태입니다. 수확 및 유통에 필요한 단기 자금을 신속히 투입하여 최대 수익을 실현하는 것이 중요합니다.",
            "특이 패턴형 (전문 컨설팅 필요)": "일반적인 리스크 패턴에서 벗어나 있어 표준화된 전략 적용이 어렵습니다. 재무 상태가 위기일 경우 '경영회생자금' 등을 우선 검토하고, 전문가를 통해 문제의 근본 원인을 진단받는 것이 시급합니다."
        }
        st.write(risk_type_description.get(user_row['리스크관리_유형'], "설명이 준비되지 않았습니다."))

    st.divider()

    # --- 세부 지표 분석 ---
    st.subheader("세부 지표 분석: 우리 농장의 강점과 약점")
    
    # [구조 개선] 5개 지표를 '기후&환경'과 '시장&수익성' 두 그룹으로 재구성
    col_climate, col_market = st.columns(2)

    with col_climate:
        st.markdown("#### 🌱 **기후 & 환경 대응력**")
        st.metric("기후회복력 점수", f"{user_row['기후회복력점수']:.1f} 점")
        st.metric("지역 포트폴리오", f"{user_row['지역기후포트폴리오지수']:.1f} 점")
    
    with col_market:
        st.markdown("#### 📈 **시장 & 수익성 분석**")
        st.metric("가격 변동성", user_row['가격변동성경보'])
        st.metric("현재 판매 적합도", f"{user_row['출하최적기지수']:.1f} 점")
        st.metric("생육 리스크", f"{user_row['생육주기리스크지수']:.2f}")

    # [신규 기능 추가] 지표별 금융 연계 활용 전략 Expander
    with st.expander("💡 각 지표별 금융 연계 활용 전략 보기"):
        st.markdown("""
        - **기후회복력 점수**: 점수가 낮은 농가(고위험군)는 **농작물재해보험** 가입을 우선 고려하고, 기후 완화 **시설(관수, 환기) 자금 대출** 심사 시 긍정적 요소로 활용할 수 있습니다.
        - **가격 변동성**: '경고' 등급 시, **계약재배나 선도거래**와 같은 가격 안정화 금융 상품을 통해 리스크를 관리할 수 있습니다.
        - **생육 리스크**: 지수가 높은(절댓값이 큰) 품목은 미래 소득 불확실성이 크므로, **재해 대비 자금 계획**을 수립하거나 대출 한도 설정 시 리스크 관리 지표로 활용됩니다.
        - **현재 판매 적합도**: 지수가 낮을 때(판매 부적기)는 **'출하 연계 브릿지론'** 등 단기 운영자금을 통해 최적 출하기를 기다릴 수 있고, 지수가 높을 때는 **단기 운전자금 대출(인력/물류비)** 수요를 예측할 수 있습니다.
        - **지역 포트폴리오**: 지수가 높은 지역은 기후 변화에 안정적인 소득 구조를 가질 확률이 높으므로, **신규 귀농/청년농 대출 상품의 전략적 타겟 지역**으로 설정하는 데 활용됩니다.
        """)
    
    st.divider()
    
    # --- 핵심 지표 시각화 ---
    st.subheader("핵심 지표 현황")

    def create_gauge_chart(value, title, color):
        fig = go.Figure(go.Indicator(
            mode = "gauge+number", value = value, title = {'text': f"<b>{title}</b>"},
            gauge = { 'axis': {'range': [None, 100]}, 'bar': {'color': color} }
        ))
        fig.update_layout(height=250, margin=dict(l=30, r=30, t=60, b=30), paper_bgcolor="rgba(0,0,0,0)", font_color="gray")
        return fig

    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.plotly_chart(create_gauge_chart(user_row['기후회복력점수'], "기후 대응 능력", "green"), use_container_width=True)
    with g_col2:
        st.plotly_chart(create_gauge_chart(user_row['출하최적기지수'], "현재 판매 적합도", "blue"), use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.info("**향후 업데이트 예정**: AI 금융 컨설턴트가 진단 결과에 맞는 최적의 금융 상품(대출/보험)을 추천해 드립니다.")
