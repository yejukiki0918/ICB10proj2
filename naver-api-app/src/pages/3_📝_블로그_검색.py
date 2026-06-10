"""
네이버 블로그 검색 API를 활용하여
블로그 포스팅 데이터를 수집하고 TF-IDF 기반 핵심 키워드 및 날짜별 빈도를 분석합니다.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
import sys
import os
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_client import fetch_naver_search_api

st.set_page_config(page_title="블로그 검색", page_icon="📝", layout="wide")

st.title("📝 블로그 검색 분석")

if "client_id" not in st.session_state or "client_secret" not in st.session_state:
    st.warning("왼쪽 사이드바에서 API 인증 정보를 먼저 입력해주세요.")
    st.stop()

col1, col2 = st.columns([2, 1])

with col1:
    query = st.text_input("블로그 검색어 입력 (콤마로 다중 입력 가능)", "데이터 분석,인공지능")

with col2:
    display_count = st.slider("조회 건수 (검색어당 최대 100)", 10, 100, 100, 10)
    
if st.button("블로그 검색 조회"):
    queries = [q.strip() for q in query.split(",") if q.strip()]
    
    if not queries:
        st.error("검색어를 입력해주세요.")
    else:
        with st.spinner("블로그 데이터를 수집 중..."):
            client_id = st.session_state["client_id"]
            client_secret = st.session_state["client_secret"]
            
            all_df = pd.DataFrame()
            
            for q in queries:
                df, err = fetch_naver_search_api(client_id, client_secret, q, api_type="blog", display=display_count)
                if df is not None and not df.empty:
                    df['search_query'] = q
                    all_df = pd.concat([all_df, df], ignore_index=True)
            
            if all_df.empty:
                st.warning("조회된 결과가 없습니다.")
            else:
                st.success("데이터 수집 완료!")
                
                # 데이터 전처리: HTML 태그 제거
                all_df["title_clean"] = all_df["title"].str.replace(r'<[^<>]*>', '', regex=True)
                all_df["desc_clean"] = all_df["description"].str.replace(r'<[^<>]*>', '', regex=True)
                
                # 날짜 파싱 (블로그 날짜는 YYYYMMDD 형태인 경우가 많음)
                all_df["postdate"] = pd.to_datetime(all_df["postdate"], errors="coerce")
                
                st.subheader("1. 날짜별 포스팅 수 분포")
                date_counts = all_df.groupby(["postdate", "search_query"]).size().reset_index(name="count")
                fig_date = px.bar(
                    date_counts, 
                    x="postdate", 
                    y="count", 
                    color="search_query",
                    title="날짜별 블로그 글 게시량",
                    barmode="group"
                )
                st.plotly_chart(fig_date, use_container_width=True)
                
                st.subheader("2. TF-IDF 기반 주요 키워드 추출")
                # TF-IDF 분석
                vectorizer = TfidfVectorizer(max_features=30, stop_words=['의', '가', '이', '은', '는', '에', '를', '과', '와', '도', '및'])
                text_data = all_df["title_clean"] + " " + all_df["desc_clean"]
                
                try:
                    tfidf_matrix = vectorizer.fit_transform(text_data)
                    feature_names = vectorizer.get_feature_names_out()
                    tfidf_scores = tfidf_matrix.sum(axis=0).A1
                    
                    tfidf_df = pd.DataFrame({"Keyword": feature_names, "Score": tfidf_scores})
                    tfidf_df = tfidf_df.sort_values(by="Score", ascending=False)
                    
                    fig_tfidf = px.bar(
                        tfidf_df, 
                        x="Score", 
                        y="Keyword", 
                        orientation='h',
                        title="상위 30개 핵심 키워드 (TF-IDF 점수순)"
                    )
                    fig_tfidf.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_tfidf, use_container_width=True)
                except ValueError:
                    st.info("단어 추출에 충분한 텍스트 데이터가 없습니다.")
                
                st.subheader("데이터 미리보기")
                st.dataframe(all_df[["title_clean", "bloggername", "postdate", "search_query"]], use_container_width=True)
