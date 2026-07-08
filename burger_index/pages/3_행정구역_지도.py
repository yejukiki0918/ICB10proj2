"""
제공된 GeoJSON을 활용해 행정구역(시군구)별 버거지수를 코로플레스(Choropleth) 지도로 시각화하는 페이지입니다.
작성일: 2026-07-04
"""
import os
import streamlit as st
import pandas as pd
import numpy as np
import folium
import requests
from streamlit_folium import st_folium

st.set_page_config(page_title="행정구역 지도", page_icon="🗺️", layout="wide")
st.title("🗺️ 행정구역별 버거지수 지도 (Choropleth)")

# 시도 코드 매핑 (행정표준코드 기준)
SIDO_MAPPING = {
    '11': '서울특별시',
    '21': '부산광역시',
    '22': '대구광역시',
    '23': '인천광역시',
    '24': '광주광역시',
    '25': '대전광역시',
    '26': '울산광역시',
    '29': '세종특별자치시',
    '31': '경기도',
    '32': '강원도',
    '33': '충청북도',
    '34': '충청남도',
    '35': '전라북도',
    '36': '전라남도',
    '37': '경상북도',
    '38': '경상남도',
    '39': '제주특별자치도'
}

@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_municipalities_geo_simple.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

@st.cache_data
def load_data(filter_threshold):
    data_path = os.path.join("burger_index", "data", "region_brand_crosstab.csv")
    df = pd.read_csv(data_path, encoding='utf-8-sig')
    
    # 필터링 적용
    if filter_threshold > 0:
        df = df[df['총합'] >= filter_threshold]
        
    # inf 처리
    max_finite = df.loc[df['버거지수'] != np.inf, '버거지수'].max()
    df['버거지수_시각화용'] = df['버거지수'].replace(np.inf, max_finite + 1.0)
    
    # 공백을 제거한 매핑용 이름 생성 (예: "서울특별시 중구" -> "서울특별시중구")
    df['매핑용_이름'] = df['시도시군구명'].str.replace(' ', '')
    
    return df

st.sidebar.header("설정")
filter_option = st.sidebar.selectbox("데이터 필터링 (최소 매장 수)", ["총합 5개 이상 (권장)", "총합 3개 이상", "필터링 없음 (전체 데이터)"])

threshold = 0
if "5개" in filter_option:
    threshold = 5
elif "3개" in filter_option:
    threshold = 3

df = load_data(threshold)
geojson_data = load_geojson()

if not geojson_data:
    st.error("GeoJSON 데이터를 불러오는데 실패했습니다.")
else:
    # GeoJSON 피처에 매핑용 이름 속성 추가
    for feature in geojson_data['features']:
        code = feature['properties']['code']
        name = feature['properties']['name']
        sido_code = code[:2]
        sido_name = SIDO_MAPPING.get(sido_code, '')
        
        # SIDO + 이름에서 공백 제거하여 매핑 키 생성
        match_name = (sido_name + name).replace(' ', '')
        feature['properties']['match_name'] = match_name

    # Folium 지도 생성
    m = folium.Map(location=[36.5, 127.5], zoom_start=7, tiles='CartoDB positron')

    # Choropleth 추가
    folium.Choropleth(
        geo_data=geojson_data,
        name='choropleth',
        data=df,
        columns=['매핑용_이름', '버거지수_시각화용'],
        key_on='feature.properties.match_name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Burger Index',
        nan_fill_color='white'
    ).add_to(m)
    
    # 툴팁을 위한 GeoJson 오버레이
    # 매핑된 데이터를 GeoJSON properties에 병합
    df_dict = df.set_index('매핑용_이름')[['버거지수', '총합']].to_dict('index')
    
    for feature in geojson_data['features']:
        m_name = feature['properties']['match_name']
        if m_name in df_dict:
            feature['properties']['burger_index'] = round(df_dict[m_name]['버거지수'], 2)
            feature['properties']['total_cnt'] = df_dict[m_name]['총합']
        else:
            feature['properties']['burger_index'] = '데이터 없음'
            feature['properties']['total_cnt'] = '데이터 없음'

    folium.GeoJson(
        geojson_data,
        style_function=lambda x: {'fillColor': '#ffffff', 'color': 'transparent', 'fillOpacity': 0.01},
        tooltip=folium.features.GeoJsonTooltip(
            fields=['name', 'burger_index', 'total_cnt'],
            aliases=['지역명:', '버거지수:', '총 매장 수:'],
            localize=True
        )
    ).add_to(m)

    st_folium(m, width=1200, height=700)
