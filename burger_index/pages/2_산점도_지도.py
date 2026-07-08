"""
위경도 정보를 활용해 지역별 버거지수를 시각화하는 Folium 산점도 지도 페이지입니다.
작성일: 2026-07-04
"""
import os
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import branca.colormap as cm

st.set_page_config(page_title="산점도 지도", page_icon="🌍", layout="wide")
st.title("🌍 위경도 기반 버거지수 산점도")

@st.cache_data
def load_data(filter_threshold):
    data_path = os.path.join("burger_index", "data", "region_brand_crosstab.csv")
    df = pd.read_csv(data_path, encoding='utf-8-sig')
    df = df.dropna(subset=['중앙_위도', '중앙_경도', '버거지수'])
    
    # 필터링 적용
    if filter_threshold > 0:
        df = df[df['총합'] >= filter_threshold]
        
    # inf 처리
    max_finite = df.loc[df['버거지수'] != np.inf, '버거지수'].max()
    df['버거지수_시각화용'] = df['버거지수'].replace(np.inf, max_finite + 1.0)
    
    return df

st.sidebar.header("설정")
filter_option = st.sidebar.selectbox("데이터 필터링 (최소 매장 수)", ["총합 5개 이상 (권장)", "총합 3개 이상", "필터링 없음 (전체 데이터)"])

threshold = 0
if "5개" in filter_option:
    threshold = 5
elif "3개" in filter_option:
    threshold = 3

df = load_data(threshold)

# Folium 지도 생성
# 대한민국의 중심점
m = folium.Map(location=[36.5, 127.5], zoom_start=7, tiles='CartoDB positron')

# 컬러맵 생성
colormap = cm.LinearColormap(colors=['yellow', 'orange', 'red', 'darkred'], 
                             vmin=df['버거지수_시각화용'].min(), 
                             vmax=df['버거지수_시각화용'].max())
colormap.caption = 'Burger Index'
m.add_child(colormap)

for idx, row in df.iterrows():
    popup_text = f"<b>{row['시도시군구명']}</b><br>" \
                 f"버거지수: {row['버거지수']:.2f}<br>" \
                 f"총 매장 수: {row['총합']}<br>" \
                 f"KFC: {row['KFC']} | 롯데리아: {row['롯데리아']}<br>" \
                 f"맥도날드: {row['맥도날드']} | 버거킹: {row['버거킹']}"
                 
    # 버거지수가 클수록 원의 반지름을 크게 설정
    radius = max(3, min(row['버거지수_시각화용'] * 3, 15)) 
    
    folium.CircleMarker(
        location=[row['중앙_위도'], row['중앙_경도']],
        radius=radius,
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=row['시도시군구명'],
        color=colormap(row['버거지수_시각화용']),
        fill=True,
        fill_color=colormap(row['버거지수_시각화용']),
        fill_opacity=0.7
    ).add_to(m)

st_folium(m, width=1200, height=700)
