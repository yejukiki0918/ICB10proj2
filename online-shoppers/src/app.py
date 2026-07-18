"""
이 파일은 Online Shoppers Purchasing Intention 데이터셋을 분석하는 Streamlit 대시보드입니다.
수치형 및 범주형 변수의 EDA 탐색 분석과 사용자 행동 퍼널 분석(Funnel Analysis)을 제공합니다.
"""
import streamlit as st
import pandas as pd
import zipfile
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(page_title="Online Shoppers Intention EDA & Funnel", layout="wide")

@st.cache_data
def load_data():
    # 현재 파일 기준 부모 디렉토리의 data 폴더 경로 탐색
    zip_path = os.path.join(os.path.dirname(__file__), "..", "data", "online+shoppers+purchasing+intention+dataset.zip")
    with zipfile.ZipFile(zip_path, 'r') as z:
        file_list = z.namelist()
        with z.open(file_list[0]) as f:
            df = pd.read_csv(f)
    return df

st.title("Online Shoppers Purchasing Intention - EDA & 퍼널 대시보드")
st.markdown("사용자의 웹사이트 행동 특징을 탐색하고 구매 전환 퍼널을 분석합니다.")

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 로드 실패: {e}")
    st.stop()

# 탭 메뉴 정의
tab_eda, tab_funnel = st.tabs(["🔍 기본 EDA", "🎯 퍼널 분석"])

with tab_eda:
    # 1. KPI (기본 통계)
    st.header("1. 주요 지표 (KPI)")
    col1, col2, col3 = st.columns(3)
    col1.metric("총 세션 수", f"{len(df):,}")
    col2.metric("구매 (Revenue=True) 비율", f"{df['Revenue'].mean():.2%}")
    col3.metric("주말 방문 비율", f"{df['Weekend'].mean():.2%}")

    # 2. 변수 구분
    # 숫자형태로 인코딩되어 있지만 의미상 범주형인 변수들을 지정
    cat_cols_explicit = ['Month', 'VisitorType', 'Weekend', 'OperatingSystems', 'Browser', 'Region', 'TrafficType']
    num_cols = [c for c in df.columns if c not in cat_cols_explicit and c != 'Revenue']

    st.header("2. 수치형 변수 탐색")
    st.markdown("각 수치형 변수에 대해 **박스플롯(상단)** 과 **히스토그램(하단)** 을 하나의 세로 서브플롯으로 시각화하고, 하단에 기술 통계량을 출력합니다.")

    for col in num_cols:
        st.subheader(f"{col}")
        
        # 세로로 배치된 2행 1열 서브플롯 생성
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True, 
            row_heights=[0.3, 0.7],
            vertical_spacing=0.08,
            subplot_titles=("박스플롯 분포", "히스토그램 분포")
        )
        
        df_true = df[df['Revenue'] == True][col]
        df_false = df[df['Revenue'] == False][col]
        
        # 1. 상단 박스플롯 (가로 방향 orientation='h' 으로 설정하여 x축 공유)
        fig.add_trace(go.Box(x=df_false, name='False (미구매)', marker_color='#EF553B', orientation='h', legendgroup='False'), row=1, col=1)
        fig.add_trace(go.Box(x=df_true, name='True (구매)', marker_color='#00CC96', orientation='h', legendgroup='True'), row=1, col=1)
        
        # 2. 하단 히스토그램
        fig.add_trace(go.Histogram(x=df_false, name='False (미구매)', opacity=0.7, marker_color='#EF553B', showlegend=False, legendgroup='False'), row=2, col=1)
        fig.add_trace(go.Histogram(x=df_true, name='True (구매)', opacity=0.7, marker_color='#00CC96', showlegend=False, legendgroup='True'), row=2, col=1)
        
        fig.update_layout(
            barmode='overlay', 
            height=600, 
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 기술통계 테이블
        desc_df = df.groupby('Revenue')[col].describe()
        st.markdown("**그룹별 기술 통계 요약**")
        st.dataframe(desc_df.style.format("{:.2f}"))
        st.divider()

    st.header("3. 범주형 변수 탐색")
    st.markdown("각 범주형 변수의 범주별로 **빈도(상단)** 와 **Revenue 비율(하단: 100% 누적 막대)** 을 세로 서브플롯으로 비교하고, 하단에 **빈도 교차표**를 확인합니다.")

    for col in cat_cols_explicit:
        st.subheader(f"{col}")
        
        # 세로로 배치된 2행 1열 서브플롯 생성
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True,
            row_heights=[0.5, 0.5],
            vertical_spacing=0.1,
            subplot_titles=("빈도 막대그래프", "비율 막대그래프 (100% 누적)")
        )
        
        # 1. 빈도 데이터
        count_df = df.groupby([col, 'Revenue']).size().reset_index(name='Count')
        count_df[col] = count_df[col].astype(str)
        
        # 2. 비율 데이터
        total_counts = count_df.groupby(col)['Count'].transform('sum')
        count_df['Percentage'] = (count_df['Count'] / total_counts) * 100
        
        df_false = count_df[count_df['Revenue'] == False]
        df_true = count_df[count_df['Revenue'] == True]
        
        # 1. 상단 빈도 막대그래프
        fig.add_trace(go.Bar(x=df_false[col], y=df_false['Count'], name='False (미구매)', marker_color='#EF553B', legendgroup='False'), row=1, col=1)
        fig.add_trace(go.Bar(x=df_true[col], y=df_true['Count'], name='True (구매)', marker_color='#00CC96', legendgroup='True'), row=1, col=1)
        
        # 2. 하단 100% 누적 비율 막대그래프
        fig.add_trace(go.Bar(
            x=df_false[col], y=df_false['Percentage'], name='False (미구매)', 
            marker_color='#EF553B', showlegend=False, legendgroup='False', 
            text=df_false['Percentage'].apply(lambda x: f'{x:.1f}%'), textposition='inside'
        ), row=2, col=1)
        fig.add_trace(go.Bar(
            x=df_true[col], y=df_true['Percentage'], name='True (구매)', 
            marker_color='#00CC96', showlegend=False, legendgroup='True', 
            text=df_true['Percentage'].apply(lambda x: f'{x:.1f}%'), textposition='inside'
        ), row=2, col=1)
        
        fig.update_layout(
            barmode='stack', 
            height=800, 
            legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 교차표
        st.markdown("**빈도 및 비율 교차표**")
        crosstab = pd.crosstab(df[col], df['Revenue'], margins=True, margins_name="Total")
        crosstab_perc = pd.crosstab(df[col], df['Revenue'], normalize='index').rename(columns={False: 'False_Ratio', True: 'True_Ratio'}) * 100
        
        merged_tab = pd.concat([crosstab, crosstab_perc], axis=1)
        
        st.dataframe(merged_tab.style.format(formatter={
            'False_Ratio': "{:.1f}%", 
            'True_Ratio': "{:.1f}%"
        }, na_rep="-"))
        st.divider()

with tab_funnel:
    st.header("🎯 사용자 행동 퍼널 분석")
    st.markdown("쇼핑몰 방문자들의 행동 깊이 및 의도에 따른 전환 흐름을 비교 분석합니다.")
    
    # 2가지 유형의 퍼널 데이터 계산
    # 1. 마일스톤 기반 퍼널 (Milestone-based)
    m_all = len(df)
    m_prod = len(df[df['ProductRelated'] > 0])
    m_admin = len(df[df['Administrative'] > 0])
    m_intent = len(df[df['PageValues'] > 0])
    m_purchase = len(df[df['Revenue'] == True])
    
    # 2. 순차 필터링 기반 퍼널 (Sequential-filtered)
    s_all = len(df)
    s_prod = len(df[df['ProductRelated'] > 0])
    s_admin = len(df[(df['ProductRelated'] > 0) & (df['Administrative'] > 0)])
    s_intent = len(df[(df['ProductRelated'] > 0) & (df['Administrative'] > 0) & (df['PageValues'] > 0)])
    s_purchase = len(df[(df['ProductRelated'] > 0) & (df['Administrative'] > 0) & (df['PageValues'] > 0) & (df['Revenue'] == True)])
    
    funnel_option = st.radio(
        "퍼널 모델 유형 선택",
        ["마일스톤 기반 퍼널 (Milestone-based)", "순차 필터링 기반 퍼널 (Sequential-filtered)"],
        help="마일스톤 기반: 각 단계를 독립적으로 도달한 유저 수 집계\n순차 필터링 기반: 이전 단계를 반드시 통과한 유저만 집계"
    )
    
    stages = [
        "1. 전체 세션 방문 (All Sessions)",
        "2. 상품 상세 페이지 조회 (Product Related View)",
        "3. 관리/계정 페이지 방문 (Administrative View)",
        "4. 높은 구매 의향 보유 (PageValues > 0)",
        "5. 최종 구매 완료 (Purchase)"
    ]
    
    if funnel_option == "마일스톤 기반 퍼널 (Milestone-based)":
        counts = [m_all, m_prod, m_admin, m_intent, m_purchase]
        description_text = """
        ### 📌 마일스톤 기반 퍼널 모델 설명
        이 퍼널 모델은 **각 전환 단계를 한 번이라도 경험한 사용자를 독립적으로 집계**합니다.
        쇼핑몰의 핵심 기능(상품 상세 조회, 마이페이지/계정 영역 방문, 가치 있는 페이지 조회)에 각각 도달한 세션의 크기를 나타냅니다.
        
        *   **1. 전체 세션 방문**: 웹사이트 유입 전체 세션입니다. (100.0%)
        *   **2. 상품 상세 페이지 조회**: 상품 상세 내용(`ProductRelated > 0`)을 탐색하여 구매 검토 단계로 진입한 세션입니다.
        *   **3. 관리/계정 페이지 방문**: 로그인, 장바구니 관리, 마이페이지 등 계정/행정 영역(`Administrative > 0`)을 확인하여 구매 전/후 프로세스를 거친 세션입니다.
        *   **4. 높은 구매 의향 보유**: 사용자가 거래 완료 시점 이전에 **실제 가치가 기여된 유효 페이지(`PageValues > 0`)**를 방문한 세션으로, 매우 강한 구매 의사를 보여줍니다.
        *   **5. 최종 구매 완료**: 실제 결제가 완료된 세션(`Revenue == True`)입니다.
        """
    else:
        counts = [s_all, s_prod, s_admin, s_intent, s_purchase]
        description_text = """
        ### 📌 순차 필터링 기반 퍼널 모델 설명
        이 퍼널 모델은 **이전 단계를 만족하면서 다음 단계 조건까지 모두 충족한 유저만 필터링하여 순차적으로 추적**합니다.
        가장 엄격한 사용자 경로(상품 상세 조회 -> 계정 영역 방문 -> 구매의도 페이지 도달 -> 최종 구매)를 보여줍니다.
        
        *   **1. 전체 세션 방문**: 웹사이트 유입 전체 세션입니다. (100.0%)
        *   **2. 상품 상세 페이지 조회**: 전체 세션 중 상품 페이지를 조회한 세션입니다.
        *   **3. 관리/계정 페이지 방문**: 상품 페이지를 조회한 사람들 중 마이페이지/계정 영역까지 방문한 사용자입니다.
        *   **4. 높은 구매 의향 보유**: 상품 페이지와 계정 영역을 방문했고, 동시에 거래 기여도가 있는 페이지(`PageValues > 0`)를 조회한 세션입니다.
        *   **5. 최종 구매 완료**: 위 모든 조건을 순서대로 혹은 함께 거쳐 최종 결제까지 완료된 세션입니다.
        """
        
    # 퍼널 차트 시각화
    fig = go.Figure(go.Funnel(
        y=stages,
        x=counts,
        textinfo="value+percent initial+percent previous",
        marker=dict(color=["#3366CC", "#DC3912", "#FF9900", "#109618", "#990099"]),
        connector={"fillcolor": "lightgrey"}
    ))
    
    fig.update_layout(
        title=dict(text=f"쇼핑몰 구매 전환 퍼널 ({funnel_option})", font=dict(size=18)),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 퍼널 통계 테이블
    st.subheader("📊 퍼널 통계 요약")
    
    funnel_data = {
        "전환 단계": stages,
        "세션 수": [f"{c:,} 건" for c in counts],
        "전체 대비 비율 (초기 전환율)": [f"{(c/counts[0])*100:.2%}" for c in counts],
        "이전 단계 대비 비율 (단계 전환율)": ["100.0%"] + [f"{(counts[i]/counts[i-1])*100:.2%}" for i in range(1, len(counts))]
    }
    
    st.dataframe(pd.DataFrame(funnel_data), use_container_width=True)
    
    # 퍼널 해석 설명 영역
    st.markdown(description_text)
