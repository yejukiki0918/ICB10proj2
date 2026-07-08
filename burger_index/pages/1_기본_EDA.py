"""
기본적인 탐색적 데이터 분석(EDA) 결과를 보여주는 페이지입니다.
작성일: 2026-07-04
"""
import os
import streamlit as st
from PIL import Image

st.set_page_config(page_title="기본 EDA", page_icon="📊", layout="wide")
st.title("📊 기본 EDA 시각화 결과")

def load_image(filename):
    path = os.path.join("burger_index", "report", filename)
    if os.path.exists(path):
        return Image.open(path)
    return None

st.markdown("### 1. 브랜드별 매장 수 (막대그래프)")
img_bar = load_image("brand_total_counts.png")
if img_bar:
    st.image(img_bar, use_container_width=True)
else:
    st.warning("이미지를 찾을 수 없습니다.")

st.markdown("### 2. 브랜드 간 상관관계 히트맵")
img_heat = load_image("brand_corr_heatmap.png")
if img_heat:
    st.image(img_heat, use_container_width=True)
else:
    st.warning("이미지를 찾을 수 없습니다.")

st.markdown("### 3. 지역별 매장 수 분포 플롯")
img_dist = load_image("brand_dist_plots.png")
if img_dist:
    st.image(img_dist, use_container_width=True)
else:
    st.warning("이미지를 찾을 수 없습니다.")

st.markdown("### 4. 상관관계 및 회귀선 페어플롯")
img_pair = load_image("brand_pairplot_advanced.png")
if img_pair:
    st.image(img_pair, use_container_width=True)
else:
    st.warning("이미지를 찾을 수 없습니다.")
