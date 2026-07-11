"""
서울 생활인구 데이터(2026년 06월) 탐색적 데이터 분석(EDA) 대시보드 (SQLite 최적화 버전)
작성자: Antigravity
주요 기능: 
- SQLite DB(사전 집계)에서 데이터를 캐싱하여 로드 (속도 최적화)
- 시간대별, 연령/성별, 지역별 인구수 시각화 및 필터링
- Folium 기반 코로플리스 맵 지도 시각화
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import folium
from streamlit_folium import st_folium
import json
import sqlite3

# --- Page Config ---
st.set_page_config(page_title="서울 생활인구 대시보드", page_icon="🏙️", layout="wide")

# --- Constants & Paths ---
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DATA_DIR, "dashboard.db")
GU_GEO_PATH = os.path.join(DATA_DIR, "seoul_gu.geojson")
DONG_GEO_PATH = os.path.join(DATA_DIR, "seoul_dong.geojson")

# --- Data Loading (Cached) ---
@st.cache_data(show_spinner="SQLite DB에서 데이터를 로딩 중입니다...")
def load_data():
    conn = sqlite3.connect(DB_PATH)
    # 구 단위 마스터 집계 (필터 적용용)
    df_gu = pd.read_sql("SELECT * FROM agg_gu", conn)
    # 동 단위 지도 전용 집계 (연령/성별 제외됨)
    df_dong = pd.read_sql("SELECT * FROM agg_dong", conn)
    # 데이터 미리보기용 샘플 원본
    df_raw = pd.read_sql("SELECT * FROM sample_raw", conn)
    conn.close()
    
    # 숫자형 변환 (필요시)
    df_gu['기준일ID'] = df_gu['기준일ID'].astype(str)
    df_dong['기준일ID'] = df_dong['기준일ID'].astype(str)
    return df_gu, df_dong, df_raw

try:
    df_gu, df_dong, df_raw = load_data()
except Exception as e:
    st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("🔍 데이터 필터링")

# 일자 필터
dates = sorted(df_gu['기준일ID'].unique())
selected_dates = st.sidebar.multiselect("기준일 선택", options=dates, default=dates[:3] if len(dates)>3 else dates)

# 자치구(시군구) 필터
gu_list = sorted([str(x) for x in df_gu['시군구명'].unique() if str(x) != '알수없음'])
selected_gu = st.sidebar.multiselect("자치구 선택", options=gu_list, default=[])

# 연령대 필터
age_list = sorted([str(x) for x in df_gu['연령대'].unique()])
selected_age = st.sidebar.multiselect("연령대 선택", options=age_list, default=age_list)

# 데이터 필터링 적용
df_filtered_gu = df_gu.copy()
df_filtered_dong = df_dong.copy()

if selected_dates:
    df_filtered_gu = df_filtered_gu[df_filtered_gu['기준일ID'].isin(selected_dates)]
    df_filtered_dong = df_filtered_dong[df_filtered_dong['기준일ID'].isin(selected_dates)]
if selected_gu:
    df_filtered_gu = df_filtered_gu[df_filtered_gu['시군구명'].isin(selected_gu)]
    df_filtered_dong = df_filtered_dong[df_filtered_dong['시군구명'].isin(selected_gu)]
if selected_age:
    df_filtered_gu = df_filtered_gu[df_filtered_gu['연령대'].isin(selected_age)]
    # 동 단위 테이블에는 연령대 컬럼이 없으므로 필터 제외 (알림 메시지 처리 가능)

# --- Main Dashboard ---
st.title("🏙️ 서울 생활인구 데이터 탐색 대시보드")
st.markdown("`SQLite 사전 집계(Pre-aggregation)`를 활용하여 최적화된 대시보드입니다.")

# --- KPIs ---
st.subheader("💡 핵심 지표 (KPI)")
col1, col2, col3, col4 = st.columns(4)

total_pop = df_filtered_gu['인구수'].sum()
# 평균 인구수는 기준일/시간대 기준
avg_pop = df_filtered_gu.groupby(['기준일ID', '시간대구분'])['인구수'].sum().mean() if not df_filtered_gu.empty else 0

# 가장 인구가 많은 시간대
time_pop = df_filtered_gu.groupby('시간대구분')['인구수'].sum().reset_index()
max_time = time_pop.loc[time_pop['인구수'].idxmax(), '시간대구분'] if not time_pop.empty else "-"

# 가장 인구가 많은 행정동 (동 단위 테이블 활용)
dong_pop = df_filtered_dong.groupby(['시군구명', '행정동명'])['인구수'].sum().reset_index()
max_dong_row = dong_pop.loc[dong_pop['인구수'].idxmax()] if not dong_pop.empty else None
max_dong = f"{max_dong_row['시군구명']} {max_dong_row['행정동명']}" if max_dong_row is not None else "-"

col1.metric("총 누적 생활인구수", f"{total_pop:,.0f} 명")
col2.metric("일/시간 평균 생활인구", f"{avg_pop:,.0f} 명")
col3.metric("최대 밀집 시간대", f"{max_time}시")
col4.metric("최대 밀집 지역", max_dong)

st.markdown("---")

# --- Tabs for EDA ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🕒 시간대별 추이", "👥 인구 구조 (성/연령)", "📍 지역별 분석", "📋 원본 데이터", "🗺️ 지도 시각화"])

with tab1:
    st.subheader("시간대별 생활인구 추이")
    df_time = df_filtered_gu.groupby(['기준일ID', '시간대구분'])['인구수'].sum().reset_index()
    
    fig_time = px.line(
        df_time, x='시간대구분', y='인구수', color='기준일ID',
        markers=True, title="일자별/시간대별 생활인구 변화량",
        labels={"시간대구분": "시간(시)", "인구수": "생활인구수"}
    )
    fig_time.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
    st.plotly_chart(fig_time, use_container_width=True)

with tab2:
    st.subheader("성별 및 연령대별 인구 구조")
    c1, c2 = st.columns(2)
    
    with c1:
        df_sex = df_filtered_gu.groupby('성별')['인구수'].sum().reset_index()
        fig_sex = px.pie(df_sex, values='인구수', names='성별', title="성별 인구 비중", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_sex.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_sex, use_container_width=True)
        
    with c2:
        df_age = df_filtered_gu.groupby('연령대')['인구수'].sum().reset_index()
        df_age = df_age.sort_values(by='연령대')
        fig_age = px.bar(df_age, x='연령대', y='인구수', title="연령대별 인구수", text_auto='.2s', color='인구수', color_continuous_scale='Blues')
        st.plotly_chart(fig_age, use_container_width=True)

with tab3:
    st.subheader("행정동별 생활인구 밀집도")
    top_dong = dong_pop.sort_values(by='인구수', ascending=False).head(20)
    top_dong['지역명'] = top_dong['시군구명'] + " " + top_dong['행정동명']
    
    fig_dong = px.bar(
        top_dong, x='인구수', y='지역명', orientation='h',
        title="상위 20개 행정동 생활인구", color='인구수', color_continuous_scale='Magma'
    )
    fig_dong.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_dong, use_container_width=True)

with tab4:
    st.subheader("데이터 미리보기 및 요약 통계 (원본 샘플)")
    st.dataframe(df_raw, use_container_width=True)

with tab5:
    st.subheader("서울시 생활인구 코로플리스 맵")
    
    col_map1, col_map2 = st.columns([1, 3])
    with col_map1:
        map_level = st.radio("지도 표시 단위", ["구별", "동별"])
        selected_time = st.slider("시간대 선택 (시)", min_value=0, max_value=23, value=12, step=1)
        st.caption("좌측의 '일자', '자치구' 필터가 반영됩니다. (동별 지도에는 연령 필터가 적용되지 않습니다)")
        
    with col_map2:
        m = folium.Map(location=[37.5665, 126.9780], zoom_start=11, tiles="cartodbpositron")
        
        if map_level == "구별":
            df_map_filtered = df_filtered_gu[df_filtered_gu['시간대구분'] == selected_time]
            if not df_map_filtered.empty:
                map_data = df_map_filtered.groupby('시군구명')['인구수'].sum().reset_index()
                pop_dict = dict(zip(map_data['시군구명'], map_data['인구수']))
                
                with open(GU_GEO_PATH, encoding='utf-8') as f:
                    geo_data = json.load(f)
                
                for feature in geo_data['features']:
                    feature_name = feature['properties']['name']
                    feature['properties']['pop'] = f"{int(pop_dict.get(feature_name, 0)):,} 명"
                    
                choropleth = folium.Choropleth(
                    geo_data=geo_data,
                    data=map_data,
                    columns=['시군구명', '인구수'],
                    key_on='feature.properties.name',
                    fill_color='YlOrRd',
                    fill_opacity=0.7,
                    line_opacity=0.2,
                    legend_name=f'시간대({selected_time}시) 구별 생활인구수'
                )
                choropleth.add_to(m)
                
                choropleth.geojson.add_child(
                    folium.features.GeoJsonTooltip(
                        fields=['name', 'pop'],
                        aliases=['구명:', '생활인구수:'],
                        labels=True
                    )
                )
        else:
            df_map_filtered = df_filtered_dong[df_filtered_dong['시간대구분'] == selected_time]
            if not df_map_filtered.empty:
                map_data = df_map_filtered.groupby('행정동명')['인구수'].sum().reset_index()
                pop_dict = dict(zip(map_data['행정동명'], map_data['인구수']))
                
                with open(DONG_GEO_PATH, encoding='utf-8') as f:
                    geo_data = json.load(f)
                
                for feature in geo_data['features']:
                    feature_name = feature['properties']['name']
                    feature['properties']['pop'] = f"{int(pop_dict.get(feature_name, 0)):,} 명"
                    
                choropleth = folium.Choropleth(
                    geo_data=geo_data,
                    data=map_data,
                    columns=['행정동명', '인구수'],
                    key_on='feature.properties.name',
                    fill_color='YlOrRd',
                    fill_opacity=0.7,
                    line_opacity=0.2,
                    legend_name=f'시간대({selected_time}시) 동별 생활인구수'
                )
                choropleth.add_to(m)
                
                choropleth.geojson.add_child(
                    folium.features.GeoJsonTooltip(
                        fields=['name', 'pop'],
                        aliases=['동명:', '생활인구수:'],
                        labels=True
                    )
                )
                
        st_folium(m, width=800, height=500, returned_objects=[])
