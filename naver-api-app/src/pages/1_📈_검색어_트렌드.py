"""
네이버 데이터랩 검색어 트렌드 API를 연동하여
사용자가 입력한 검색어들의 기간별 검색 트렌드를 시각화하는 페이지입니다.
"""

import streamlit as st
import datetime
import plotly.express as px
import sys
import os

# 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_client import fetch_datalab_search_trend

st.set_page_config(page_title="검색어 트렌드", page_icon="📈", layout="wide")

st.title("📈 검색어 트렌드 분석")

if "client_id" not in st.session_state or "client_secret" not in st.session_state:
    st.warning("왼쪽 사이드바에서 API 인증 정보를 먼저 입력해주세요.")
    st.stop()

st.markdown("네이버 데이터랩(DataLab) API를 통해 검색어들의 트렌드를 분석합니다.")

col1, col2 = st.columns([2, 1])

with col1:
    keywords_input = st.text_input("검색어 입력 (콤마로 구분하여 최대 5개)", "파이썬,자바,자바스크립트")

with col2:
    start_date = st.date_input("시작일", datetime.date.today() - datetime.timedelta(days=30))
    end_date = st.date_input("종료일", datetime.date.today())

if st.button("트렌드 조회"):
    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
    
    if not keywords:
        st.error("최소 1개 이상의 검색어를 입력해주세요.")
    elif len(keywords) > 5:
        st.error("검색어는 최대 5개까지만 입력 가능합니다.")
    elif start_date >= end_date:
        st.error("종료일은 시작일보다 이후여야 합니다.")
    else:
        with st.spinner("데이터를 가져오는 중..."):
            client_id = st.session_state["client_id"]
            client_secret = st.session_state["client_secret"]
            
            df, err = fetch_datalab_search_trend(client_id, client_secret, keywords, start_date, end_date)
            
            if err:
                st.error(f"API 호출 오류: {err}")
            elif df is None or df.empty:
                st.warning("조회된 데이터가 없습니다.")
            else:
                st.success("데이터 조회가 완료되었습니다.")
                
                # Plotly 시각화
                fig = px.line(
                    df, 
                    x="날짜", 
                    y="비율", 
                    color="검색어",
                    title="검색어별 검색 트렌드 (상대 비율)",
                    markers=True
                )
                fig.update_layout(
                    xaxis_title="날짜",
                    yaxis_title="검색 비율 (%)",
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("데이터 미리보기")
                st.dataframe(df, use_container_width=True)
