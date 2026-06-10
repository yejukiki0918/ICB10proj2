"""
네이버 API 연동 및 데이터 수집을 담당하는 모듈입니다.
검색어 트렌드, 블로그, 카페, 뉴스, 쇼핑 검색 등의 API를 호출하고
응답을 Pandas DataFrame으로 변환하여 Streamlit 앱에 제공합니다.
"""

import requests
import pandas as pd
import streamlit as st
import datetime

# 공통 헤더 생성
def get_headers(client_id, client_secret):
    return {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

@st.cache_data(ttl=3600)
def fetch_datalab_search_trend(client_id, client_secret, keywords, start_date, end_date):
    """
    통합 검색어 트렌드 조회 API
    keywords: list of strings (검색어 목록)
    """
    url = "https://openapi.naver.com/v1/datalab/search"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json"
    }
    
    keyword_groups = [{"groupName": kw, "keywords": [kw]} for kw in keywords]
    
    body = {
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "timeUnit": "date",
        "keywordGroups": keyword_groups
    }
    
    response = requests.post(url, headers=headers, json=body)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        
        all_data = []
        for res in results:
            title = res["title"]
            for d in res["data"]:
                all_data.append({
                    "날짜": d["period"],
                    "검색어": title,
                    "비율": d["ratio"]
                })
        df = pd.DataFrame(all_data)
        if not df.empty:
            df["날짜"] = pd.to_datetime(df["날짜"])
        return df, None
    else:
        return None, f"Error: {response.status_code} - {response.text}"

@st.cache_data(ttl=600)
def fetch_naver_search_api(client_id, client_secret, query, api_type="blog", display=100):
    """
    공통 네이버 검색 API 호출 (blog, news, cafearticle, shop)
    api_type: 'blog', 'news', 'cafearticle', 'shop'
    """
    url = f"https://openapi.naver.com/v1/search/{api_type}.json"
    headers = get_headers(client_id, client_secret)
    params = {
        "query": query,
        "display": display,
        "sort": "sim" if api_type == "shop" else "date" # 쇼핑은 정확도순, 나머지는 최신순 기본
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        df = pd.DataFrame(items)
        return df, None
    else:
        return None, f"Error: {response.status_code} - {response.text}"
