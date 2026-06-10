"""
네이버 쇼핑 검색 API를 연동하여
특정 키워드에 대한 상품 리스트를 가져오고 가격 분포 및 카테고리 등을 시각화합니다.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_client import fetch_naver_search_api

st.set_page_config(page_title="쇼핑 검색", page_icon="🛍️", layout="wide")

st.title("🛍️ 쇼핑 검색 분석")

if "client_id" not in st.session_state or "client_secret" not in st.session_state:
    st.warning("왼쪽 사이드바에서 API 인증 정보를 먼저 입력해주세요.")
    st.stop()

query = st.text_input("쇼핑 검색어 입력", "기계식 키보드")
display_count = st.slider("조회 건수", 10, 100, 100, 10)

if st.button("쇼핑 검색 조회"):
    if not query.strip():
        st.error("검색어를 입력해주세요.")
    else:
        with st.spinner("상품 데이터를 수집 중..."):
            client_id = st.session_state["client_id"]
            client_secret = st.session_state["client_secret"]
            
            df, err = fetch_naver_search_api(client_id, client_secret, query, api_type="shop", display=display_count)
            
            if err:
                st.error(f"API 호출 오류: {err}")
            elif df is None or df.empty:
                st.warning("조회된 결과가 없습니다.")
            else:
                st.success("데이터 수집 완료!")
                
                # 데이터 전처리: 가격 숫자로 변환
                df["lprice"] = pd.to_numeric(df["lprice"], errors="coerce")
                
                # HTML 태그 제거 로직
                df["title"] = df["title"].str.replace(r'<[^<>]*>', '', regex=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # 최저가 분포 (히스토그램)
                    fig_price = px.histogram(
                        df, 
                        x="lprice", 
                        nbins=20, 
                        title="최저가 분포",
                        labels={"lprice": "최저가 (원)"}
                    )
                    st.plotly_chart(fig_price, use_container_width=True)
                    
                with col2:
                    # 쇼핑몰별 상품 비중 (파이차트)
                    top_malls = df["mallName"].value_counts().reset_index()
                    top_malls.columns = ["쇼핑몰", "상품 수"]
                    
                    fig_mall = px.pie(
                        top_malls.head(10), 
                        values="상품 수", 
                        names="쇼핑몰", 
                        title="주요 쇼핑몰별 상품 비중 (Top 10)"
                    )
                    st.plotly_chart(fig_mall, use_container_width=True)
                
                st.subheader("상품 목록 데이터")
                st.dataframe(df[["title", "lprice", "mallName", "category1", "category2"]], use_container_width=True)
